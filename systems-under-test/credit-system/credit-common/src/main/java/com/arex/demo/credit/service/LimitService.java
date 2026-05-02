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
public class LimitService {

    private static final Logger log = LoggerFactory.getLogger(LimitService.class);

    private final CreditDataRepository repository;
    private final ExternalDataService externalDataService;
    private final CreditProperties creditProperties;
    private final RestTemplate restTemplate;

    public LimitService(
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
        BigDecimal applyAmount = decimal(params.get("apply_amount"));

        Map<String, Object> customer = repository.findCustomer(customerId);
        Map<String, Object> product = repository.findProductRule(productId);
        Map<String, Object> history = repository.findCreditHistory(customerId);
        Map<String, Object> incomeProof = null;
        Map<String, Object> employment = null;

        if (customer == null || product == null) {
            return GatewayResult.error(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), "CUSTOMER_OR_PRODUCT_NOT_FOUND");
        }

        Map<String, Object> creditScore = externalDataService.queryCreditScore(customerId);
        Map<String, Object> fraud = externalDataService.queryFraud(customerId);
        Map<String, Object> multiLoan = null;
        if ("P002".equals(productId) || applyAmount.compareTo(new BigDecimal("80000")) >= 0) {
            multiLoan = externalDataService.queryMultiLoan(customerId);
            incomeProof = repository.findIncomeProof(customerId);
            employment = repository.findEmployment(customerId);
        }

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

        Map<String, Object> body = new LinkedHashMap<String, Object>();
        if ("REJECT".equals(String.valueOf(risk.get("decision")))) {
            body.put("limit_result", "REJECT");
            body.put("risk_level", value(risk.get("riskLevel")));
            body.put("approved_limit", "0.00");
            body.put("limit_grade", "N");
            body.put("pricing_rate", value(product.get("annual_rate")));
            body.put("term_options", value(product.get("term_options")));
            body.put("decision_reason", "RISK_ENGINE_REJECT");
            audit(params, body, creditScore, fraud, multiLoan);
            return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
        }

        BigDecimal monthlyIncome = decimal(customer.get("monthly_income"));
        BigDecimal currentBalance = history == null ? BigDecimal.ZERO : decimal(history.get("current_balance"));
        BigDecimal debtRatio = monthlyIncome.compareTo(BigDecimal.ZERO) > 0
                ? currentBalance.divide(monthlyIncome, 4, RoundingMode.HALF_UP)
                : BigDecimal.ONE;
        BigDecimal baseLimit = monthlyIncome.multiply(decimal(product.get("base_limit_factor"))).setScale(2, RoundingMode.HALF_UP);

        String pricingUrl = String.format(
                "%s/internal/credit/pricing?traId=%s&txnCode=%s&customerId=%s&riskLevel=%s&monthlyIncome=%s&debtRatio=%s&baseLimit=%s&annualRate=%s",
                creditProperties.getInternal().getBaseUrl(),
                traId,
                txnCode,
                customerId,
                value(risk.get("riskLevel")),
                monthlyIncome.toPlainString(),
                debtRatio.toPlainString(),
                baseLimit.toPlainString(),
                value(product.get("annual_rate"))
        );
        log.info("traId={} HTTP sub-call request: {}", traId, pricingUrl);
        @SuppressWarnings("unchecked")
        Map<String, Object> pricing = restTemplate.getForObject(pricingUrl, Map.class);
        log.info("traId={} HTTP sub-call response: status=200, body={}", traId, pricing);

        BigDecimal approvedLimit = decimal(pricing.get("approvedLimit"));
        BigDecimal minLimit = decimal(product.get("min_limit"));
        BigDecimal maxLimit = decimal(product.get("max_limit"));
        if (approvedLimit.compareTo(minLimit) < 0) {
            approvedLimit = minLimit;
        }
        if (approvedLimit.compareTo(maxLimit) > 0) {
            approvedLimit = maxLimit;
        }

        if ("MEDIUM".equals(String.valueOf(risk.get("riskLevel")))) {
            approvedLimit = approvedLimit.multiply(new BigDecimal("0.85")).setScale(2, RoundingMode.HALF_UP);
        }
        if (incomeProof != null && !"Y".equals(String.valueOf(incomeProof.get("tax_verified")))) {
            approvedLimit = approvedLimit.multiply(new BigDecimal("0.90")).setScale(2, RoundingMode.HALF_UP);
        }
        if (approvedLimit.compareTo(minLimit) < 0) {
            approvedLimit = minLimit;
        }
        if (approvedLimit.compareTo(maxLimit) > 0) {
            approvedLimit = maxLimit;
        }

        if ("MEDIUM".equals(String.valueOf(risk.get("riskLevel"))) || applyAmount.compareTo(new BigDecimal("100000")) >= 0) {
            repository.saveRiskStrategyLog(
                    traId,
                    customerId,
                    productId,
                    "LIMIT_DOWNGRADE",
                    "APPLIED",
                    "riskLevel=" + value(risk.get("riskLevel")) + ", employment=" + summarize(employment)
            );
        }

        body.put("limit_result", "PASS");
        body.put("risk_level", value(risk.get("riskLevel")));
        body.put("approved_limit", approvedLimit.toPlainString());
        body.put("limit_grade", value(pricing.get("limitGrade")));
        body.put("pricing_rate", value(pricing.get("pricingRate")));
        body.put("term_options", value(product.get("term_options")));
        body.put("decision_reason", "准入通过，额度模型评分正常");

        audit(params, body, creditScore, fraud, multiLoan);
        return GatewayResult.success(txnCode, traId, TraceContext.getRequestTime(), TraceContext.responseTime(), body);
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
        payload.put("admitResult", body.get("limit_result"));
        payload.put("approvedLimit", body.get("approved_limit"));
        payload.put("limitGrade", body.get("limit_grade"));
        payload.put("pricingRate", body.get("pricing_rate"));
        payload.put("decisionReason", body.get("decision_reason"));
        repository.saveApplyAudit(payload);
    }

    private BigDecimal decimal(Object value) {
        try {
            return new BigDecimal(String.valueOf(value));
        } catch (Exception e) {
            return BigDecimal.ZERO;
        }
    }

    private String value(Object value) {
        return value == null ? "" : String.valueOf(value);
    }

    private String summarize(Map<String, Object> row) {
        if (row == null) {
            return "NOT_FOUND";
        }
        String text = row.toString();
        return text.length() > 200 ? text.substring(0, 200) + "..." : text;
    }
}
