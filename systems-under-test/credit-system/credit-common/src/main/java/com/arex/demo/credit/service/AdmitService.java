package com.arex.demo.credit.service;

import com.arex.demo.credit.config.CreditProperties;
import com.arex.demo.credit.model.GatewayResult;
import com.arex.demo.credit.repository.CreditDataRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class AdmitService {

    private static final Logger log = LoggerFactory.getLogger(AdmitService.class);

    private final CreditDataRepository repository;
    private final ExternalDataService externalDataService;
    private final CreditProperties creditProperties;
    private final RestTemplate restTemplate;

    public AdmitService(
            CreditDataRepository repository,
            ExternalDataService externalDataService,
            CreditProperties creditProperties,
            RestTemplate restTemplate
    ) {
        this.repository = repository;
        this.externalDataService = externalDataService;
        this.creditProperties = creditProperties;
        this.restTemplate = restTemplate;
    }

    public GatewayResult process(Map<String, String> params) {
        String traId = TraceContext.getTraId();
        String txnCode = params.get("txn_code");
        String customerId = params.get("customer_id");
        String productId = params.get("product_id");
        String requestNo = params.get("request_no");
        BigDecimal applyAmount = decimal(params.get("apply_amount"));

        Map<String, Object> customer = repository.findCustomer(customerId);
        Map<String, Object> product = repository.findProductRule(productId);
        Map<String, Object> body = new LinkedHashMap<String, Object>();

        if (customer == null || product == null) {
            body.put("admit_result", "REJECT");
            body.put("risk_level", "HIGH");
            body.put("reject_reason", "CUSTOMER_OR_PRODUCT_NOT_FOUND");
            audit(params, body, null, null, null);
            return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
        }

        if (!"ACTIVE".equals(String.valueOf(customer.get("customer_status")))) {
            body.put("admit_result", "REJECT");
            body.put("risk_level", "HIGH");
            body.put("reject_reason", "CUSTOMER_STATUS_INVALID");
            audit(params, body, null, null, null);
            return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
        }

        int age = intValue(customer.get("age"));
        int minAge = intValue(product.get("min_age"));
        int maxAge = intValue(product.get("max_age"));
        if (age < minAge || age > maxAge) {
            body.put("admit_result", "REJECT");
            body.put("risk_level", "HIGH");
            body.put("reject_reason", "AGE_OUT_OF_RANGE");
            audit(params, body, null, null, null);
            return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
        }

        BigDecimal income = decimal(customer.get("monthly_income"));
        BigDecimal minIncome = decimal(product.get("min_income"));
        if (income.compareTo(minIncome) < 0) {
            body.put("admit_result", "REJECT");
            body.put("risk_level", "HIGH");
            body.put("reject_reason", "INCOME_TOO_LOW");
            audit(params, body, null, null, null);
            return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
        }

        Map<String, Object> blacklist = repository.findBlacklist(customerId);
        if (blacklist != null) {
            body.put("admit_result", "REJECT");
            body.put("risk_level", "HIGH");
            body.put("reject_reason", "BLACKLIST_HIT");
            audit(params, body, null, null, null);
            return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
        }

        Map<String, Object> history = repository.findCreditHistory(customerId);
        Map<String, Object> creditScore = externalDataService.queryCreditScore(customerId);
        Map<String, Object> fraud = externalDataService.queryFraud(customerId);

        Map<String, Object> multiLoan = null;
        if ("P002".equals(productId) || applyAmount.compareTo(new BigDecimal("100000")) >= 0) {
            multiLoan = externalDataService.queryMultiLoan(customerId);
        }

        Map<String, Object> contact = null;
        if (creditProperties.getFeatures().isEnableContactStability() && (age < 25 || income.compareTo(new BigDecimal("8000")) < 0)) {
            contact = externalDataService.queryContactStability(customerId);
        }

        cacheExternal(customerId, "CREDIT_SCORE", creditScore);
        cacheExternal(customerId, "FRAUD", fraud);
        cacheExternal(customerId, "MULTI_LOAN", multiLoan);
        cacheExternal(customerId, "CONTACT_STABILITY", contact);

        String riskUrl = String.format(
                "%s/internal/credit/risk?traId=%s&txnCode=%s&customerId=%s&productId=%s&creditScore=%s&fraudLevel=%s&multiLoanCount=%s&maxOverdueDays=%s",
                creditProperties.getInternal().getBaseUrl(),
                traId,
                txnCode,
                customerId,
                productId,
                value(creditScore.get("creditScore")),
                value(fraud.get("fraudLevel")),
                multiLoan == null ? "0" : value(multiLoan.get("loanPlatformCount")),
                history == null ? "0" : value(history.get("max_overdue_days_12m"))
        );
        log.info("traId={} HTTP sub-call request: {}", traId, riskUrl);
        @SuppressWarnings("unchecked")
        Map<String, Object> risk = restTemplate.getForObject(riskUrl, Map.class);
        log.info("traId={} HTTP sub-call response: status=200, body={}", traId, risk);

        String admitResult = "PASS";
        String rejectReason = "";
        if (intValue(creditScore.get("creditScore")) < intValue(product.get("min_credit_score"))) {
            admitResult = "REJECT";
            rejectReason = "CREDIT_SCORE_TOO_LOW";
        } else if ("HIGH".equals(String.valueOf(fraud.get("fraudLevel")))) {
            admitResult = "REJECT";
            rejectReason = "FRAUD_RISK_TOO_HIGH";
        } else if (history != null && intValue(history.get("max_overdue_days_12m")) > intValue(product.get("max_overdue_days"))) {
            admitResult = "REJECT";
            rejectReason = "OVERDUE_TOO_SERIOUS";
        } else if ("REJECT".equals(String.valueOf(risk.get("decision")))) {
            admitResult = "REJECT";
            rejectReason = "RISK_ENGINE_REJECT";
        }

        BigDecimal suggestMin = income.multiply(new BigDecimal("2.0")).setScale(2, RoundingMode.HALF_UP);
        BigDecimal suggestMax = income.multiply(decimal(product.get("base_limit_factor"))).setScale(2, RoundingMode.HALF_UP);
        BigDecimal maxLimit = decimal(product.get("max_limit"));
        if (suggestMax.compareTo(maxLimit) > 0) {
            suggestMax = maxLimit;
        }

        body.put("admit_result", admitResult);
        body.put("risk_level", value(risk.get("riskLevel")));
        body.put("credit_score", value(creditScore.get("creditScore")));
        body.put("fraud_level", value(fraud.get("fraudLevel")));
        body.put("multi_loan_count", multiLoan == null ? "0" : value(multiLoan.get("loanPlatformCount")));
        body.put("reject_reason", rejectReason);
        body.put("suggest_min_limit", suggestMin.toPlainString());
        body.put("suggest_max_limit", suggestMax.toPlainString());

        audit(params, body, creditScore, fraud, multiLoan);
        return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
    }

    private void cacheExternal(String customerId, String type, Map<String, Object> payload) {
        if (!creditProperties.getFeatures().isEnableExternalCache() || payload == null) {
            return;
        }
        repository.saveExternalCache(
                TraceContext.getTraId(),
                customerId,
                type,
                "{\"customerId\":\"" + customerId + "\"}",
                payload.toString()
        );
    }

    private void audit(Map<String, String> params, Map<String, Object> body, Map<String, Object> creditScore, Map<String, Object> fraud, Map<String, Object> multiLoan) {
        Map<String, Object> payload = new LinkedHashMap<String, Object>();
        payload.put("txnCode", params.get("txn_code"));
        payload.put("traId", TraceContext.getTraId());
        payload.put("requestTime", TraceContext.getRequestTime());
        payload.put("requestNo", params.get("request_no"));
        payload.put("customerId", params.get("customer_id"));
        payload.put("productId", params.get("product_id"));
        payload.put("applyAmount", params.get("apply_amount"));
        payload.put("applyTerm", params.get("apply_term"));
        payload.put("creditScore", creditScore == null ? null : creditScore.get("creditScore"));
        payload.put("fraudLevel", fraud == null ? null : fraud.get("fraudLevel"));
        payload.put("multiLoanCount", multiLoan == null ? 0 : multiLoan.get("loanPlatformCount"));
        payload.put("riskLevel", body.get("risk_level"));
        payload.put("admitResult", body.get("admit_result"));
        payload.put("approvedLimit", null);
        payload.put("limitGrade", null);
        payload.put("pricingRate", null);
        payload.put("decisionReason", body.get("reject_reason"));
        repository.saveApplyAudit(payload);
    }

    private BigDecimal decimal(Object value) {
        try {
            return new BigDecimal(String.valueOf(value));
        } catch (Exception e) {
            return BigDecimal.ZERO;
        }
    }

    private int intValue(Object value) {
        try {
            return Integer.parseInt(String.valueOf(value));
        } catch (Exception e) {
            return 0;
        }
    }

    private String value(Object value) {
        return value == null ? "" : String.valueOf(value);
    }
}
