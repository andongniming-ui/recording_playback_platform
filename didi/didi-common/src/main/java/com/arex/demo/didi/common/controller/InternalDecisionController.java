package com.arex.demo.didi.common.controller;

import java.math.BigDecimal;
import java.util.Map;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.arex.demo.didi.common.service.InternalDecisionService;

@RestController
@RequestMapping("/internal/didi")
public class InternalDecisionController {

    private final InternalDecisionService internalDecisionService;

    public InternalDecisionController(InternalDecisionService internalDecisionService) {
        this.internalDecisionService = internalDecisionService;
    }

    @GetMapping("/risk")
    public Map<String, Object> risk(@RequestParam("txnCode") String txnCode,
                                    @RequestParam(value = "customerNo", required = false) String customerNo,
                                    @RequestParam(value = "plateNo", required = false) String plateNo,
                                    @RequestParam(value = "riskScore", required = false) Integer riskScore) {
        return internalDecisionService.evaluateRisk(txnCode, customerNo, plateNo, riskScore);
    }

    @GetMapping("/pricing")
    public Map<String, Object> pricing(@RequestParam("txnCode") String txnCode,
                                       @RequestParam(value = "customerNo", required = false) String customerNo,
                                       @RequestParam(value = "plateNo", required = false) String plateNo,
                                       @RequestParam("baseAmount") BigDecimal baseAmount) {
        return internalDecisionService.calculatePrice(txnCode, customerNo, baseAmount);
    }
}
