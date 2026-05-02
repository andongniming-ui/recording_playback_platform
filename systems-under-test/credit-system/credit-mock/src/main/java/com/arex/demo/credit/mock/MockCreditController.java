package com.arex.demo.credit.mock;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/mock")
public class MockCreditController {

    @GetMapping("/health")
    public String health() {
        return "OK";
    }

    @GetMapping("/credit-score")
    public Map<String, Object> creditScore(@RequestParam("customerId") String customerId) {
        Map<String, Object> body = new LinkedHashMap<String, Object>();
        body.put("customerId", customerId);
        if ("C10002".equals(customerId)) {
            body.put("creditScore", 88);
            body.put("creditLevel", "A");
        } else if ("C10003".equals(customerId)) {
            body.put("creditScore", 72);
            body.put("creditLevel", "B");
        } else if ("C10004".equals(customerId)) {
            body.put("creditScore", 68);
            body.put("creditLevel", "B");
        } else if ("C10005".equals(customerId)) {
            body.put("creditScore", 66);
            body.put("creditLevel", "C");
        } else if ("C10006".equals(customerId)) {
            body.put("creditScore", 64);
            body.put("creditLevel", "C");
        } else if ("C10007".equals(customerId)) {
            body.put("creditScore", 75);
            body.put("creditLevel", "B");
        } else if ("C10008".equals(customerId)) {
            body.put("creditScore", 70);
            body.put("creditLevel", "B");
        } else if ("C10009".equals(customerId)) {
            body.put("creditScore", 58);
            body.put("creditLevel", "D");
        } else if ("C10010".equals(customerId)) {
            body.put("creditScore", 74);
            body.put("creditLevel", "B");
        } else {
            body.put("creditScore", 78);
            body.put("creditLevel", "B");
        }
        body.put("hitRules", "NO_SERIOUS_OVERDUE");
        return body;
    }

    @GetMapping("/fraud")
    public Map<String, Object> fraud(@RequestParam("customerId") String customerId) {
        Map<String, Object> body = new LinkedHashMap<String, Object>();
        body.put("customerId", customerId);
        if ("C10008".equals(customerId)) {
            body.put("fraudLevel", "HIGH");
            body.put("fraudTags", "DEVICE_MISMATCH,ADDRESS_RISK");
        } else if ("C10004".equals(customerId) || "C10005".equals(customerId)) {
            body.put("fraudLevel", "MEDIUM");
            body.put("fraudTags", "CONTACT_FREQUENT_CHANGE");
        } else {
            body.put("fraudLevel", "LOW");
            body.put("fraudTags", "NORMAL_DEVICE,NORMAL_LOCATION");
        }
        return body;
    }

    @GetMapping("/multi-loan")
    public Map<String, Object> multiLoan(@RequestParam("customerId") String customerId) {
        Map<String, Object> body = new LinkedHashMap<String, Object>();
        body.put("customerId", customerId);
        if ("C10005".equals(customerId)) {
            body.put("loanPlatformCount", 5);
            body.put("applyCount30d", 4);
        } else if ("C10006".equals(customerId)) {
            body.put("loanPlatformCount", 4);
            body.put("applyCount30d", 3);
        } else if ("C10002".equals(customerId)) {
            body.put("loanPlatformCount", 1);
            body.put("applyCount30d", 1);
        } else {
            body.put("loanPlatformCount", 2);
            body.put("applyCount30d", 1);
        }
        return body;
    }

    @GetMapping("/contact-stability")
    public Map<String, Object> contactStability(@RequestParam("customerId") String customerId) {
        Map<String, Object> body = new LinkedHashMap<String, Object>();
        body.put("customerId", customerId);
        if ("C10003".equals(customerId) || "C10004".equals(customerId)) {
            body.put("stabilityLevel", "MEDIUM");
            body.put("recentChangeCount", 2);
        } else {
            body.put("stabilityLevel", "LOW");
            body.put("recentChangeCount", 0);
        }
        return body;
    }
}
