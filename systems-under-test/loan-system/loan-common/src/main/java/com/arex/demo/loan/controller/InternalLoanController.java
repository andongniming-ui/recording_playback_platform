package com.arex.demo.loan.controller;

import com.arex.demo.loan.model.GatewayResult;
import com.arex.demo.loan.service.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/loan/internal")
public class InternalLoanController {

    private static final Logger log = LoggerFactory.getLogger(InternalLoanController.class);

    @Autowired private QualifyService qualifyService;
    @Autowired private CreditService creditService;
    @Autowired private IncomeService incomeService;
    @Autowired private QuotaService quotaService;

    @PostMapping("/qualify")
    public GatewayResult qualify(@RequestBody Map<String, String> req) {
        TraceContext.init();
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> INTERNAL IN  | /qualify | requestTime={} | params={}", traId, TraceContext.getRequestTime(), req);
        try {
            Map<String, Object> data = qualifyService.check(req);
            GatewayResult result = GatewayResult.ok("INTERNAL_QUALIFY", data);
            log.info("[{}] <<< INTERNAL OUT | /qualify | elapsed={}ms | result={}", traId, TraceContext.getElapsedMs(), summarize(data));
            return result;
        } finally { TraceContext.clear(); }
    }

    @PostMapping("/credit")
    public GatewayResult credit(@RequestBody Map<String, String> req) {
        TraceContext.init();
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> INTERNAL IN  | /credit | requestTime={} | params={}", traId, TraceContext.getRequestTime(), req);
        try {
            Map<String, Object> data = creditService.check(req);
            GatewayResult result = GatewayResult.ok("INTERNAL_CREDIT", data);
            log.info("[{}] <<< INTERNAL OUT | /credit | elapsed={}ms | result={}", traId, TraceContext.getElapsedMs(), summarize(data));
            return result;
        } finally { TraceContext.clear(); }
    }

    @PostMapping("/income")
    public GatewayResult income(@RequestBody Map<String, String> req) {
        TraceContext.init();
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> INTERNAL IN  | /income | requestTime={} | params={}", traId, TraceContext.getRequestTime(), req);
        try {
            Map<String, Object> data = incomeService.check(req);
            GatewayResult result = GatewayResult.ok("INTERNAL_INCOME", data);
            log.info("[{}] <<< INTERNAL OUT | /income | elapsed={}ms | result={}", traId, TraceContext.getElapsedMs(), summarize(data));
            return result;
        } finally { TraceContext.clear(); }
    }

    @PostMapping("/quota")
    public GatewayResult quota(@RequestBody Map<String, String> req) {
        TraceContext.init();
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> INTERNAL IN  | /quota | requestTime={} | params={}", traId, TraceContext.getRequestTime(), req);
        try {
            Map<String, Object> data = quotaService.calculate(req);
            GatewayResult result = GatewayResult.ok("INTERNAL_QUOTA", data);
            log.info("[{}] <<< INTERNAL OUT | /quota | elapsed={}ms | result={}", traId, TraceContext.getElapsedMs(), summarize(data));
            return result;
        } finally { TraceContext.clear(); }
    }

    private String summarize(Map<String, Object> data) {
        if (data == null) return "null";
        String s = data.toString();
        return s.length() > 200 ? s.substring(0, 200) + "..." : s;
    }
}
