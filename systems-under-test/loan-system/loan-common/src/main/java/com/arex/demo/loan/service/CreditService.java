package com.arex.demo.loan.service;

import com.arex.demo.loan.config.LoanVariantProperties;
import com.arex.demo.loan.repository.LoanDataRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.*;

@Service
public class CreditService {

    private static final Logger log = LoggerFactory.getLogger(CreditService.class);

    @Autowired private LoanDataRepository repo;
    @Autowired private LoanVariantProperties variant;
    @Autowired private RestTemplate restTemplate;

    @SuppressWarnings("unchecked")
    public Map<String, Object> check(Map<String, String> params) {
        String customerId = params.getOrDefault("customerId", "");
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> SVC IN | CreditService.check | customer={} | variant={} | requestTime={}", traId, customerId, variant.getLabel(), TraceContext.getRequestTime());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("traId", traId);
        result.put("requestTime", TraceContext.getRequestTime());
        result.put("customerId", customerId);

        // Step 1: Check blacklist (DB call)
        boolean onBlacklist = repo.isOnBlacklist(customerId);
        result.put("onBlacklist", onBlacklist);

        if (onBlacklist) {
            result.put("riskLevel", "HIGH");
            result.put("riskDecision", "REJECT");
            result.put("creditScore", 0);
            log.info("[{}] <<< SVC OUT | CreditService.check | BLACKLIST | elapsed={}ms", traId, TraceContext.getElapsedMs());
            return result;
        }

        // Step 2: Call mock credit service (HTTP external call)
        int creditScore = 0;
        String creditLevel = "UNKNOWN";
        try {
            String mockPort = System.getProperty("mock.port", "28083");
            String mockUrl = "http://localhost:" + mockPort + "/mock/credit?customerId=" + customerId;
            log.info("[{}] >>> HTTP OUT | GET {} | traId={}", traId, mockUrl, traId);
            long httpStart = System.currentTimeMillis();
            Map<String, Object> resp = restTemplate.getForObject(mockUrl, Map.class);
            long httpElapsed = System.currentTimeMillis() - httpStart;
            log.info("[{}] <<< HTTP IN  | GET /mock/credit | elapsed={}ms | response={}", traId, httpElapsed, resp);
            if (resp != null) {
                creditScore = ((Number) resp.getOrDefault("creditScore", 0)).intValue();
                creditLevel = (String) resp.getOrDefault("creditLevel", "C");
            }
        } catch (Exception e) {
            log.warn("[{}] !!! HTTP FAIL | GET /mock/credit | error={} | using fallback score=70", traId, e.getMessage());
            creditScore = 70;
            creditLevel = "C";
        }

        // Step 3: Risk grading (Bug 2: INCLUSIVE=>=80, EXCLUSIVE=>80 for LOW)
        String riskLevel;
        if (variant.isRiskScoreUpperExclusive()) {
            if (creditScore > 80) { riskLevel = "LOW"; }
            else if (creditScore >= 60) { riskLevel = "MEDIUM"; }
            else { riskLevel = "HIGH"; }
        } else {
            if (creditScore >= 80) { riskLevel = "LOW"; }
            else if (creditScore >= 60) { riskLevel = "MEDIUM"; }
            else { riskLevel = "HIGH"; }
        }

        String riskDecision = "LOW".equals(riskLevel) || "MEDIUM".equals(riskLevel) ? "APPROVE" : "REJECT";

        result.put("creditScore", creditScore);
        result.put("creditLevel", creditLevel);
        result.put("riskLevel", riskLevel);
        result.put("riskDecision", riskDecision);
        result.put("riskGradeMode", variant.getRiskGradeMode());

        log.info("[{}] <<< SVC OUT | CreditService.check | riskLevel={} score={} mode={} | elapsed={}ms",
                traId, riskLevel, creditScore, variant.getRiskGradeMode(), TraceContext.getElapsedMs());
        return result;
    }
}
