package com.arex.demo.didi.common.controller;

import java.math.BigDecimal;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.arex.demo.didi.common.service.InternalDecisionService;

@RestController
@RequestMapping("/internal/didi")
public class InternalDecisionController {

    private static final Logger log = LoggerFactory.getLogger(InternalDecisionController.class);

    private final InternalDecisionService internalDecisionService;

    public InternalDecisionController(InternalDecisionService internalDecisionService) {
        this.internalDecisionService = internalDecisionService;
    }

    @GetMapping("/risk")
    public Map<String, Object> risk(@RequestParam(value = "traId", required = false) String traId,
                                    @RequestParam("txnCode") String txnCode,
                                    @RequestParam(value = "customerNo", required = false) String customerNo,
                                    @RequestParam(value = "plateNo", required = false) String plateNo,
                                    @RequestParam(value = "riskScore", required = false) Integer riskScore) {
        log.info("traId={} Internal risk request: txnCode={}, customerNo={}, plateNo={}, riskScore={}", traId, txnCode, customerNo, plateNo, riskScore);
        Map<String, Object> payload = internalDecisionService.evaluateRisk(txnCode, customerNo, plateNo, riskScore);
        log.info("traId={} Internal risk response: {}", traId, payload);
        return payload;
    }

    @GetMapping("/pricing")
    public Map<String, Object> pricing(@RequestParam(value = "traId", required = false) String traId,
                                       @RequestParam("txnCode") String txnCode,
                                       @RequestParam(value = "customerNo", required = false) String customerNo,
                                       @RequestParam(value = "plateNo", required = false) String plateNo,
                                       @RequestParam("baseAmount") BigDecimal baseAmount) {
        log.info("traId={} Internal pricing request: txnCode={}, customerNo={}, plateNo={}, baseAmount={}", traId, txnCode, customerNo, plateNo, baseAmount);
        Map<String, Object> payload = internalDecisionService.calculatePrice(txnCode, customerNo, baseAmount);
        log.info("traId={} Internal pricing response: {}", traId, payload);
        return payload;
    }
}
