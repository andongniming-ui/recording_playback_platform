package com.arex.demo.didi.common.service;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import com.arex.demo.didi.common.config.DidiVariantProperties;
import com.arex.demo.didi.common.model.CarTransactionDefinition;
import com.arex.demo.didi.common.model.GatewayContext;
import com.arex.demo.didi.common.model.GatewayResult;
import com.arex.demo.didi.common.repository.CarDataRepository;

@Service
public class CarComplexTransactionService {

    private static final Logger log = LoggerFactory.getLogger(CarComplexTransactionService.class);

    private final CarDataRepository repository;
    private final RestTemplate restTemplate;
    private final DidiVariantProperties variantProperties;

    public CarComplexTransactionService(CarDataRepository repository,
                                        RestTemplate restTemplate,
                                        DidiVariantProperties variantProperties) {
        this.repository = repository;
        this.restTemplate = restTemplate;
        this.variantProperties = variantProperties;
    }

    public GatewayResult process(CarTransactionDefinition definition, GatewayContext context) {
        Map<String, Object> vehicle = repository.findVehicle(context.getPlateNo(), context.getVin());
        String customerNo = hasText(context.getCustomerNo()) ? context.getCustomerNo() : stringValue(vehicle, "owner_customer_no", "C10001");
        Map<String, Object> customer = repository.findCustomer(customerNo);
        Map<String, Object> policy = repository.findPolicy(context.getPolicyNo(), context.getPlateNo());
        Map<String, Object> claim = repository.findClaim(context.getClaimNo(), context.getPlateNo());
        Map<String, Object> dispatch = repository.findDispatch(context.getPlateNo(), context.getGarageCode());

        Integer riskScore = integerValue(vehicle.get("risk_score"), Integer.valueOf(45));
        Map<String, Object> riskResult = fetch("/internal/didi/risk",
            definition.getCode(),
            customerNo,
            stringValue(vehicle, "plate_no", context.getPlateNo()),
            definition.getBaseAmount(),
            riskScore);
        Map<String, Object> pricingResult = fetch("/internal/didi/pricing",
            definition.getCode(),
            stringValue(customer, "tier_level", "STANDARD"),
            stringValue(vehicle, "plate_no", context.getPlateNo()),
            definition.getBaseAmount(),
            riskScore);

        BigDecimal quotedAmount = decimalValue(pricingResult.get("quoteAmount"), definition.getBaseAmount());
        String riskLevel = stringValue(riskResult, "riskLevel", "LOW");
        String decision = stringValue(riskResult, "decision", "AUTO_PASS");

        repository.saveAudit(
            definition.getCode(),
            context.getRequestNo(),
            customerNo,
            stringValue(vehicle, "plate_no", context.getPlateNo()),
            riskLevel,
            quotedAmount,
            variantProperties.getVariantId()
        );
        repository.updateVehicleStatus(stringValue(vehicle, "plate_no", context.getPlateNo()),
            "MANUAL_REVIEW".equals(decision) ? "INSPECTING" : "ACTIVE");

        DidiVariantProperties.VariantOverride override = variantProperties.overrideOf(definition.getCode());
        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage(definition.getDisplayName() + "处理完成" + suffix(override.getMessageSuffix()));
        result.setCustomerTier(stringValue(customer, "tier_level", "STANDARD"));
        result.setVehicleModel(stringValue(vehicle, "model_name", "DIDI-CAR"));
        result.setRiskLevel(riskLevel);
        result.setDecision(decision);
        result.setDispatchCity(firstNonBlank(override.getDispatchCity(), stringValue(dispatch, "city", context.getCity())));
        result.setPolicyStatus(firstNonBlank(
            stringValue(policy, "policy_status", null),
            stringValue(claim, "claim_status", "OPEN")
        ));
        result.setDbFlag("Y");
        result.setSubCallFlag("Y");
        result.setBaseAmount(definition.getBaseAmount());
        result.setFinalAmount(quotedAmount);
        return result;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> fetch(String path,
                                      String txnCode,
                                      String customerNo,
                                      String plateNo,
                                      BigDecimal baseAmount,
                                      Integer riskScore) {
        String traId = TraceContext.getTraId();
        String url = UriComponentsBuilder.fromHttpUrl(variantProperties.getInternalBaseUrl() + path)
            .queryParam("traId", traId)
            .queryParam("txnCode", txnCode)
            .queryParam("customerNo", customerNo)
            .queryParam("plateNo", plateNo)
            .queryParam("baseAmount", baseAmount)
            .queryParam("riskScore", riskScore)
            .toUriString();
        log.info("traId={} HTTP sub-call request: {}", traId, url);
        ResponseEntity<Map> entity = restTemplate.getForEntity(url, Map.class);
        Map<String, Object> body = entity.getBody() == null ? Collections.<String, Object>emptyMap() : entity.getBody();
        log.info("traId={} HTTP sub-call response: status={}, body={}", traId, entity.getStatusCodeValue(), body);
        return body;
    }

    private BigDecimal decimalValue(Object raw, BigDecimal fallback) {
        if (raw == null) {
            return fallback;
        }
        return new BigDecimal(String.valueOf(raw)).setScale(2, BigDecimal.ROUND_HALF_UP);
    }

    private Integer integerValue(Object raw, Integer fallback) {
        if (raw == null) {
            return fallback;
        }
        return Integer.valueOf(String.valueOf(raw));
    }

    private String stringValue(Map<String, Object> map, String key, String fallback) {
        Object raw = map.get(key);
        return raw == null ? fallback : String.valueOf(raw);
    }

    private String firstNonBlank(String first, String second) {
        return hasText(first) ? first : second;
    }

    private String suffix(String value) {
        return hasText(value) ? ("-" + value.trim()) : "";
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }
}
