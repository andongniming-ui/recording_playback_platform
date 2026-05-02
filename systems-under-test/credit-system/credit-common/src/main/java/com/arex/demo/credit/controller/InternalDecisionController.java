package com.arex.demo.credit.controller;

import com.arex.demo.credit.service.PricingService;
import com.arex.demo.credit.service.RiskDecisionService;
import com.arex.demo.credit.service.TraceContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;

@RestController
@RequestMapping("/internal/credit")
public class InternalDecisionController {

    private static final Logger log = LoggerFactory.getLogger(InternalDecisionController.class);

    private final RiskDecisionService riskDecisionService;
    private final PricingService pricingService;

    public InternalDecisionController(RiskDecisionService riskDecisionService, PricingService pricingService) {
        this.riskDecisionService = riskDecisionService;
        this.pricingService = pricingService;
    }

    @GetMapping("/risk")
    public Map<String, Object> risk(
            @RequestParam("traId") String traId,
            @RequestParam("txnCode") String txnCode,
            @RequestParam("customerId") String customerId,
            @RequestParam("productId") String productId,
            @RequestParam("creditScore") String creditScore,
            @RequestParam("fraudLevel") String fraudLevel,
            @RequestParam("multiLoanCount") String multiLoanCount,
            @RequestParam("maxOverdueDays") String maxOverdueDays
    ) {
        log.info("traId={} Internal risk request: txnCode={}, customerId={}, productId={}, creditScore={}, fraudLevel={}, multiLoanCount={}, maxOverdueDays={}",
                traId, txnCode, customerId, productId, creditScore, fraudLevel, multiLoanCount, maxOverdueDays);
        Map<String, String> params = new LinkedHashMap<String, String>();
        params.put("txnCode", txnCode);
        params.put("customerId", customerId);
        params.put("productId", productId);
        params.put("creditScore", creditScore);
        params.put("fraudLevel", fraudLevel);
        params.put("multiLoanCount", multiLoanCount);
        params.put("maxOverdueDays", maxOverdueDays);
        Map<String, Object> result = riskDecisionService.evaluate(params);
        log.info("traId={} Internal risk response: {}", traId, result);
        return result;
    }

    @GetMapping("/pricing")
    public Map<String, Object> pricing(
            @RequestParam("traId") String traId,
            @RequestParam("txnCode") String txnCode,
            @RequestParam("customerId") String customerId,
            @RequestParam("riskLevel") String riskLevel,
            @RequestParam("monthlyIncome") String monthlyIncome,
            @RequestParam("debtRatio") String debtRatio,
            @RequestParam("baseLimit") String baseLimit,
            @RequestParam("annualRate") String annualRate
    ) {
        log.info("traId={} Internal pricing request: txnCode={}, customerId={}, riskLevel={}, monthlyIncome={}, debtRatio={}, baseLimit={}",
                traId, txnCode, customerId, riskLevel, monthlyIncome, debtRatio, baseLimit);
        Map<String, String> params = new LinkedHashMap<String, String>();
        params.put("txnCode", txnCode);
        params.put("customerId", customerId);
        params.put("riskLevel", riskLevel);
        params.put("monthlyIncome", monthlyIncome);
        params.put("debtRatio", debtRatio);
        params.put("baseLimit", baseLimit);
        params.put("annualRate", annualRate);
        Map<String, Object> result = pricingService.price(params);
        log.info("traId={} Internal pricing response: {}", traId, result);
        return result;
    }
}
