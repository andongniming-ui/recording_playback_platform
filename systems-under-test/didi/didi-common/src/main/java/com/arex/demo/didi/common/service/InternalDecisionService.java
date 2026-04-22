package com.arex.demo.didi.common.service;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.stereotype.Service;

import com.arex.demo.didi.common.config.DidiVariantProperties;

@Service
public class InternalDecisionService {

    private final DidiVariantProperties variantProperties;

    public InternalDecisionService(DidiVariantProperties variantProperties) {
        this.variantProperties = variantProperties;
    }

    public Map<String, Object> evaluateRisk(String txnCode, String customerNo, String plateNo, Integer riskScore) {
        int score = riskScore == null ? 45 : riskScore.intValue();
        String riskLevel = score >= 80 ? "HIGH" : (score >= 55 ? "MEDIUM" : "LOW");
        String decision = "HIGH".equals(riskLevel) ? "MANUAL_REVIEW" : "AUTO_PASS";

        DidiVariantProperties.VariantOverride override = variantProperties.overrideOf(txnCode);
        if (hasText(override.getRiskLevel())) {
            riskLevel = override.getRiskLevel();
        }
        if (hasText(override.getDecision())) {
            decision = override.getDecision();
        }

        Map<String, Object> payload = new LinkedHashMap<String, Object>();
        payload.put("txnCode", txnCode);
        payload.put("customerNo", customerNo);
        payload.put("plateNo", plateNo);
        payload.put("riskLevel", riskLevel);
        payload.put("decision", decision);
        payload.put("variantId", variantProperties.getVariantId());
        return payload;
    }

    public Map<String, Object> calculatePrice(String txnCode, String customerTier, BigDecimal baseAmount) {
        BigDecimal discount = "VIP".equalsIgnoreCase(customerTier) ? new BigDecimal("0.92") : new BigDecimal("1.00");
        BigDecimal quoteAmount = baseAmount.multiply(discount).setScale(2, BigDecimal.ROUND_HALF_UP);

        DidiVariantProperties.VariantOverride override = variantProperties.overrideOf(txnCode);
        if (override.getAmountDelta() != null) {
            quoteAmount = quoteAmount.add(override.getAmountDelta()).setScale(2, BigDecimal.ROUND_HALF_UP);
        }

        Map<String, Object> payload = new LinkedHashMap<String, Object>();
        payload.put("txnCode", txnCode);
        payload.put("customerTier", customerTier);
        payload.put("baseAmount", baseAmount.setScale(2, BigDecimal.ROUND_HALF_UP));
        payload.put("quoteAmount", quoteAmount);
        payload.put("variantId", variantProperties.getVariantId());
        return payload;
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }
}
