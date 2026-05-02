package com.arex.demo.credit.controller;

import com.arex.demo.credit.model.GatewayResult;
import com.arex.demo.credit.service.CreditGatewayService;
import com.arex.demo.credit.service.TraceContext;
import com.arex.demo.credit.service.XmlPayloadService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/credit")
public class CreditGatewayController {

    private static final Logger log = LoggerFactory.getLogger(CreditGatewayController.class);

    private final XmlPayloadService xmlPayloadService;
    private final CreditGatewayService gatewayService;

    public CreditGatewayController(XmlPayloadService xmlPayloadService, CreditGatewayService gatewayService) {
        this.xmlPayloadService = xmlPayloadService;
        this.gatewayService = gatewayService;
    }

    @PostMapping(value = "/gateway", consumes = MediaType.APPLICATION_XML_VALUE, produces = MediaType.APPLICATION_XML_VALUE)
    public String gateway(@RequestBody String xmlBody) {
        Map<String, String> params = xmlPayloadService.extractParams(xmlBody);
        TraceContext.init(params.get("tra_id"), params.get("request_time"));
        String traId = TraceContext.getTraId();
        try {
            log.info("traId={} Received /credit/gateway request: {}", traId, summarize(xmlBody));
            GatewayResult result = gatewayService.process(params);
            String xml = xmlPayloadService.buildResponse(result);
            log.info("traId={} Completed /credit/gateway in {} ms, response: {}", traId, TraceContext.elapsedMs(), summarize(xml));
            return xml;
        } catch (Exception e) {
            log.error("traId={} Error processing /credit/gateway: {}", traId, e.getMessage(), e);
            return "<response><status>ERROR</status><tra_id>" + traId + "</tra_id><error_message>" + e.getMessage() + "</error_message></response>";
        } finally {
            TraceContext.clear();
        }
    }

    private String summarize(String text) {
        String flat = text == null ? "" : text.replace('\n', ' ').replace('\r', ' ').trim();
        return flat.length() > 400 ? flat.substring(0, 400) + "..." : flat;
    }
}
