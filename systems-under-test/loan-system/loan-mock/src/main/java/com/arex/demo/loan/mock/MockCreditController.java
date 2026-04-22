package com.arex.demo.loan.mock;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * Mock external credit bureau API.
 * Returns deterministic credit scores based on customerId.
 * Score=80 is the key boundary (triggers Bug2 in new system).
 */
@RestController
@RequestMapping("/mock")
public class MockCreditController {

    private static final Logger log = LoggerFactory.getLogger(MockCreditController.class);

    private static final Map<String, int[]> SCORES = new LinkedHashMap<>();
    static {
        SCORES.put("C001", new int[]{78, 0});   // MEDIUM (normal)
        SCORES.put("C002", new int[]{65, 0});   // MEDIUM (normal)
        SCORES.put("C003", new int[]{82, 0});   // LOW (normal)
        SCORES.put("C004", new int[]{45, 0});   // HIGH
        SCORES.put("C005", new int[]{88, 0});   // LOW
        SCORES.put("C006", new int[]{80, 0});   // BOUNDARY: LOW in old, MEDIUM in new (Bug2!)
        SCORES.put("C007", new int[]{55, 0});   // HIGH
        SCORES.put("C008", new int[]{72, 0});   // MEDIUM
        SCORES.put("C009", new int[]{92, 0});   // LOW
        SCORES.put("C010", new int[]{30, 0});   // HIGH + blacklist
    }

    @GetMapping("/credit")
    public Map<String, Object> queryCredit(@RequestParam String customerId) {
        log.info("[MockCredit] query for customerId={}", customerId);
        Map<String, Object> result = new LinkedHashMap<>();

        int[] entry = SCORES.getOrDefault(customerId, new int[]{70, 0});
        int score = entry[0];

        String level;
        if (score >= 80) level = "A";
        else if (score >= 60) level = "B";
        else level = "C";

        result.put("customerId", customerId);
        result.put("creditScore", score);
        result.put("creditLevel", level);
        result.put("source", "MOCK_CREDIT_BUREAU");
        result.put("queryTime", new Date().toString());

        log.info("[MockCredit] response: score={} level={}", score, level);
        return result;
    }

    @GetMapping("/health")
    public String health() { return "OK"; }
}
