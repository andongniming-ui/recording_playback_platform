package com.arex.demo.credit.service;

import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class PricingService {

    public Map<String, Object> price(Map<String, String> params) {
        BigDecimal monthlyIncome = decimal(params.get("monthlyIncome"));
        BigDecimal debtRatio = decimal(params.get("debtRatio"));
        BigDecimal baseLimit = decimal(params.get("baseLimit"));
        BigDecimal annualRate = decimal(params.get("annualRate"));
        String riskLevel = safe(params.get("riskLevel"));

        BigDecimal factor = new BigDecimal("1.00");
        if ("MEDIUM".equals(riskLevel)) {
            factor = new BigDecimal("0.75");
        } else if ("HIGH".equals(riskLevel)) {
            factor = new BigDecimal("0.50");
        }

        BigDecimal ratioPenalty = BigDecimal.ONE.subtract(debtRatio.min(new BigDecimal("0.80")));
        if (ratioPenalty.compareTo(new BigDecimal("0.20")) < 0) {
            ratioPenalty = new BigDecimal("0.20");
        }

        BigDecimal approvedLimit = baseLimit.multiply(factor).multiply(ratioPenalty).setScale(2, RoundingMode.HALF_UP);
        String limitGrade = approvedLimit.compareTo(new BigDecimal("80000")) >= 0 ? "A" :
                approvedLimit.compareTo(new BigDecimal("40000")) >= 0 ? "B" : "C";
        BigDecimal finalRate = annualRate.add("MEDIUM".equals(riskLevel) ? new BigDecimal("1.20") :
                "HIGH".equals(riskLevel) ? new BigDecimal("2.80") : BigDecimal.ZERO).setScale(4, RoundingMode.HALF_UP);

        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("txnCode", params.get("txnCode"));
        result.put("customerId", params.get("customerId"));
        result.put("monthlyIncome", monthlyIncome);
        result.put("debtRatio", debtRatio);
        result.put("approvedLimit", approvedLimit);
        result.put("limitGrade", limitGrade);
        result.put("pricingRate", finalRate);
        result.put("variantId", "CREDIT_CORE");
        return result;
    }

    private BigDecimal decimal(String value) {
        try {
            return new BigDecimal(value);
        } catch (Exception e) {
            return BigDecimal.ZERO;
        }
    }

    private String safe(String value) {
        return value == null ? "" : value.trim().toUpperCase();
    }
}
