package com.arex.demo.didi.common.service;

import java.math.BigDecimal;

import org.springframework.stereotype.Service;

import com.arex.demo.didi.common.config.DidiVariantProperties;
import com.arex.demo.didi.common.model.CarTransactionDefinition;
import com.arex.demo.didi.common.model.GatewayContext;
import com.arex.demo.didi.common.model.GatewayResult;

@Service
public class CarGatewayService {

    private final XmlPayloadService xmlPayloadService;
    private final CarTransactionCatalog catalog;
    private final CarComplexTransactionService complexTransactionService;
    private final DidiVariantProperties variantProperties;

    public CarGatewayService(XmlPayloadService xmlPayloadService,
                             CarTransactionCatalog catalog,
                             CarComplexTransactionService complexTransactionService,
                             DidiVariantProperties variantProperties) {
        this.xmlPayloadService = xmlPayloadService;
        this.catalog = catalog;
        this.complexTransactionService = complexTransactionService;
        this.variantProperties = variantProperties;
    }

    public String handle(String xmlPayload) {
        GatewayContext context = xmlPayloadService.parse(xmlPayload);
        CarTransactionDefinition definition = catalog.find(context.getTransactionCode());
        if (definition == null) {
            throw new IllegalArgumentException("unsupported transaction code: " + context.getTransactionCode());
        }
        GatewayResult result = definition.isComplex() ? complexTransactionService.process(definition, context) : simpleResult(definition);
        return xmlPayloadService.buildResponseXml(context, definition, result, variantProperties);
    }

    private GatewayResult simpleResult(CarTransactionDefinition definition) {
        DidiVariantProperties.VariantOverride override = variantProperties.overrideOf(definition.getCode());
        GatewayResult result = new GatewayResult();
        BigDecimal amount = definition.getBaseAmount().add(override.getAmountDelta()).setScale(2, BigDecimal.ROUND_HALF_UP);
        result.setStatus("SUCCESS");
        result.setMessage(definition.getDisplayName() + "处理完成" + suffix(override.getMessageSuffix()));
        result.setCustomerTier("LIGHT");
        result.setVehicleModel("CITY-CAR");
        result.setRiskLevel(hasText(override.getRiskLevel()) ? override.getRiskLevel() : "NONE");
        result.setDecision(hasText(override.getDecision()) ? override.getDecision() : "DIRECT_PASS");
        result.setDispatchCity(hasText(override.getDispatchCity()) ? override.getDispatchCity() : "SHANGHAI");
        result.setPolicyStatus("NA");
        result.setDbFlag("N");
        result.setSubCallFlag("N");
        result.setBaseAmount(definition.getBaseAmount());
        result.setFinalAmount(amount);
        return result;
    }

    private String suffix(String value) {
        return hasText(value) ? ("-" + value.trim()) : "";
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }
}
