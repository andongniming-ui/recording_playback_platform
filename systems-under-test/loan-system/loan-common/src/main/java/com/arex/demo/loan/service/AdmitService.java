package com.arex.demo.loan.service;

import com.arex.demo.loan.config.LoanVariantProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class AdmitService {

    private static final Logger log = LoggerFactory.getLogger(AdmitService.class);

    @Autowired private LoanVariantProperties variant;
    @Autowired private RestTemplate restTemplate;

    public Map<String, Object> assess(Map<String, String> params) {
        String customerId = params.getOrDefault("customerId", "");
        String productId = params.getOrDefault("productId", "P001");
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> SVC IN | AdmitService.assess | customer={} product={} variant={} | requestTime={}", traId, customerId, productId, variant.getLabel(), TraceContext.getRequestTime());

        int port = Integer.parseInt(System.getProperty("server.port", "28081"));

        Map<String, Object> qualifyResult = callInternal(port, "/loan/internal/qualify", params, "qualify");
        Map<String, Object> creditResult = callInternal(port, "/loan/internal/credit", params, "credit");
        Map<String, Object> incomeResult = callInternal(port, "/loan/internal/income", params, "income");
        Map<String, Object> quotaResult = callInternal(port, "/loan/internal/quota", params, "quota");

        boolean qualified = safeBool(qualifyResult, "qualified");
        String riskLevel = safeStr(creditResult, "riskLevel");
        boolean incomeOk = "PASS".equals(safeStr(incomeResult, "incomeCheck"));
        double quota = safeDouble(quotaResult, "quota");
        boolean onBlacklist = safeBool(creditResult, "onBlacklist");

        boolean admitted = qualified && !onBlacklist && incomeOk && !"HIGH".equals(riskLevel);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("traId", traId);
        result.put("requestTime", TraceContext.getRequestTime());
        result.put("customerId", customerId);
        result.put("productId", productId);
        result.put("admitted", admitted);
        result.put("admitDecision", admitted ? "APPROVE" : "REJECT");
        result.put("approvedQuota", admitted ? quota : 0);
        result.put("qualifyResult", qualifyResult);
        result.put("creditResult", creditResult);
        result.put("incomeResult", incomeResult);
        result.put("quotaResult", quotaResult);

        if (!admitted) {
            List<String> reasons = new ArrayList<>();
            if (!qualified) reasons.add("QUALIFY_FAILED");
            if (onBlacklist) reasons.add("ON_BLACKLIST");
            if (!incomeOk) reasons.add("INCOME_CHECK_FAILED");
            if ("HIGH".equals(riskLevel)) reasons.add("HIGH_RISK");
            result.put("rejectReasons", String.join(",", reasons));
        }

        log.info("[{}] <<< SVC OUT | AdmitService.assess | admitted={} quota={} | elapsed={}ms",
                traId, admitted, quota, TraceContext.getElapsedMs());
        return result;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> callInternal(int port, String path, Map<String, String> params, String label) {
        String traId = TraceContext.getTraId();
        try {
            String url = "http://localhost:" + port + path;
            log.info("[{}] >>> HTTP OUT | POST {} | label={} | traId={}", traId, url, label, traId);
            long start = System.currentTimeMillis();
            Map<String, Object> resp = restTemplate.postForObject(url, params, Map.class);
            long elapsed = System.currentTimeMillis() - start;
            log.info("[{}] <<< HTTP IN  | POST {} | label={} | elapsed={}ms | status={}", traId, path, label, elapsed, resp != null ? resp.get("status") : "null");
            if (resp != null && "SUCCESS".equals(resp.get("status"))) {
                return (Map<String, Object>) resp.getOrDefault("body", new HashMap<>());
            }
            log.warn("[{}] !!! HTTP WARN | {} returned non-SUCCESS", traId, label);
        } catch (Exception e) {
            log.warn("[{}] !!! HTTP FAIL | POST {} | label={} | error={}", traId, path, label, e.getMessage());
        }
        return new HashMap<>();
    }

    private boolean safeBool(Map<String, Object> m, String key) {
        Object v = m.get(key); return v != null && Boolean.parseBoolean(v.toString());
    }
    private String safeStr(Map<String, Object> m, String key) {
        Object v = m.get(key); return v != null ? v.toString() : "";
    }
    private double safeDouble(Map<String, Object> m, String key) {
        Object v = m.get(key); if (v instanceof Number) return ((Number) v).doubleValue(); return 0;
    }
}
