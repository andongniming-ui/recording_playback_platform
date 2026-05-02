package com.arex.demo.credit.service;

import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class RiskDecisionService {

    public Map<String, Object> evaluate(Map<String, String> params) {
        int creditScore = parseInt(params.get("creditScore"), 0);
        String fraudLevel = normalize(params.get("fraudLevel"));
        int multiLoanCount = parseInt(params.get("multiLoanCount"), 0);
        int overdueDays = parseInt(params.get("maxOverdueDays"), 0);

        String riskLevel = "LOW";
        String decision = "PASS";
        if ("HIGH".equals(fraudLevel) || overdueDays > 30 || creditScore < 60) {
            riskLevel = "HIGH";
            decision = "REJECT";
        } else if ("MEDIUM".equals(fraudLevel) || multiLoanCount >= 4 || creditScore < 70 || overdueDays > 10) {
            riskLevel = "MEDIUM";
            decision = "PASS";
        }

        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.put("txnCode", params.get("txnCode"));
        result.put("customerId", params.get("customerId"));
        result.put("riskLevel", riskLevel);
        result.put("decision", decision);
        result.put("variantId", "CREDIT_CORE");
        return result;
    }

    private int parseInt(String value, int defaultValue) {
        try {
            return Integer.parseInt(value);
        } catch (Exception e) {
            return defaultValue;
        }
    }

    private String normalize(String value) {
        return value == null ? "" : value.trim().toUpperCase();
    }
}
