package com.arex.demo.loan.controller;

import com.arex.demo.loan.model.GatewayResult;
import com.arex.demo.loan.service.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/loan")
public class LoanGatewayController {

    private static final Logger log = LoggerFactory.getLogger(LoanGatewayController.class);

    @Autowired
    private LoanGatewayService gatewayService;

    @PostMapping(value = "/gateway", consumes = MediaType.APPLICATION_XML_VALUE, produces = MediaType.APPLICATION_XML_VALUE)
    public String executeXml(@RequestBody String xmlBody) {
        TraceContext.init();
        String traId = TraceContext.getTraId();
        String reqTime = TraceContext.getRequestTime();
        log.info("[{}] >>> REQUEST | traId={} | requestTime={} | protocol=XML", traId, traId, reqTime);
        try {
            String txnCode = gatewayService.extractTxnCode(xmlBody);
            Map<String, String> params = gatewayService.extractParams(xmlBody);
            log.info("[{}] >>> IN   | txnCode={} | params={}", traId, txnCode, params);
            String result = gatewayService.processXml(txnCode, params);
            log.info("[{}] <<< OUT  | txnCode={} | elapsed={}ms | responseLen={}", traId, txnCode, TraceContext.getElapsedMs(), result.length());
            log.info("[{}] <<< RESPONSE COMPLETE | traId={} | elapsed={}ms", traId, traId, TraceContext.getElapsedMs());
            return result;
        } catch (Exception e) {
            log.error("[{}] !!! ERROR | traId={} | error={} | elapsed={}ms", traId, traId, e.getMessage(), TraceContext.getElapsedMs(), e);
            return "<response><head><traId>" + traId + "</traId><requestTime>" + reqTime
                 + "</requestTime><status>ERROR</status><message>" + e.getMessage() + "</message><elapsed>" + TraceContext.getElapsedMs()
                 + "</elapsed></head></response>";
        } finally {
            TraceContext.clear();
        }
    }

    @PostMapping(value = "/gateway/json", consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public GatewayResult executeJson(@RequestBody Map<String, Object> req) {
        TraceContext.init();
        String traId = TraceContext.getTraId();
        String reqTime = TraceContext.getRequestTime();
        log.info("[{}] >>> REQUEST | traId={} | requestTime={} | protocol=JSON", traId, traId, reqTime);
        try {
            String txnCode = (String) req.getOrDefault("txnCode", "UNKNOWN");
            @SuppressWarnings("unchecked")
            Map<String, String> params = (Map<String, String>) req.getOrDefault("params", new HashMap<>());
            log.info("[{}] >>> IN   | txnCode={} | params={}", traId, txnCode, params);
            GatewayResult result = gatewayService.processJson(txnCode, params);
            log.info("[{}] <<< OUT  | txnCode={} | status={} | elapsed={}ms | bodySummary={}", traId, txnCode, result.getStatus(), result.getElapsed(), summarizeBody(result.getBody()));
            log.info("[{}] <<< RESPONSE COMPLETE | traId={} | elapsed={}ms", traId, traId, TraceContext.getElapsedMs());
            return result;
        } catch (Exception e) {
            log.error("[{}] !!! ERROR | traId={} | error={} | elapsed={}ms", traId, traId, e.getMessage(), TraceContext.getElapsedMs(), e);
            return GatewayResult.fail("ERROR", e.getMessage());
        } finally {
            TraceContext.clear();
        }
    }

    private String summarizeBody(Map<String, Object> body) {
        if (body == null) return "null";
        String s = body.toString();
        return s.length() > 200 ? s.substring(0, 200) + "..." : s;
    }
}
