package com.arex.demo.waimai.controller;
import com.arex.demo.waimai.model.GatewayResult;
import com.arex.demo.waimai.service.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import java.util.*;

@RestController
@RequestMapping("/waimai/gateway")
public class WaimaiGatewayController {
    private static final Logger log = LoggerFactory.getLogger(WaimaiGatewayController.class);
    @Autowired private WaimaiGatewayService gatewayService;

    @PostMapping(value="/execute", consumes=MediaType.APPLICATION_XML_VALUE, produces=MediaType.APPLICATION_XML_VALUE)
    public String execute(@RequestBody String xmlBody) {
        TraceContext.init();
        log.info("[{}] Gateway XML request, requestTime={}, body={}", TraceContext.getTraId(), TraceContext.getRequestTime(), compact(xmlBody));
        try {
            String response = gatewayService.handleXmlRequest(xmlBody);
            log.info("[{}] Gateway XML response, body={}", TraceContext.getTraId(), compact(response));
            return response;
        }
        catch (Exception e) {
            log.error("[{}] Gateway error: {}", TraceContext.getTraId(), e.getMessage(), e);
            return "<response><status>ERROR</status><message>"+e.getMessage()+"</message><traId>"+TraceContext.getTraId()+"</traId><requestTime>"+TraceContext.getRequestTime()+"</requestTime></response>";
        } finally { TraceContext.clear(); }
    }

    @PostMapping(value="/json", consumes=MediaType.APPLICATION_JSON_VALUE, produces=MediaType.APPLICATION_JSON_VALUE)
    public GatewayResult executeJson(@RequestBody Map<String,Object> req) {
        TraceContext.init();
        log.info("[{}] Gateway JSON request, requestTime={}, body={}", TraceContext.getTraId(), TraceContext.getRequestTime(), req);
        try {
            String txnCode = (String) req.getOrDefault("txnCode","UNKNOWN");
            @SuppressWarnings("unchecked") Map<String,String> params = (Map<String,String>) req.getOrDefault("params", new HashMap<>());
            GatewayResult result = gatewayService.handleJsonRequest(txnCode, params);
            log.info("[{}] Gateway JSON response, txnCode={}, status={}, body={}",
                TraceContext.getTraId(),
                result.getTxnCode(),
                result.getStatus(),
                result.getData());
            return result;
        } catch (Exception e) {
            log.error("[{}] Gateway JSON error: {}", TraceContext.getTraId(), e.getMessage(), e);
            return GatewayResult.fail("ERROR", e.getMessage());
        } finally { TraceContext.clear(); }
    }

    private String compact(String text) {
        return text == null ? "" : text.replaceAll("\\s+", " ").trim();
    }
}
