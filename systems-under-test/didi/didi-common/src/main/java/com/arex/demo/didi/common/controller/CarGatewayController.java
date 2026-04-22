package com.arex.demo.didi.common.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.arex.demo.didi.common.model.GatewayContext;
import com.arex.demo.didi.common.service.CarGatewayService;
import com.arex.demo.didi.common.service.TraceContext;
import com.arex.demo.didi.common.service.XmlPayloadService;

@RestController
@RequestMapping("/api/car")
public class CarGatewayController {

    private static final Logger log = LoggerFactory.getLogger(CarGatewayController.class);

    private final CarGatewayService gatewayService;
    private final XmlPayloadService xmlPayloadService;

    public CarGatewayController(CarGatewayService gatewayService, XmlPayloadService xmlPayloadService) {
        this.gatewayService = gatewayService;
        this.xmlPayloadService = xmlPayloadService;
    }

    @PostMapping(value = "/service", consumes = {MediaType.APPLICATION_XML_VALUE, MediaType.TEXT_XML_VALUE, MediaType.TEXT_PLAIN_VALUE}, produces = MediaType.APPLICATION_XML_VALUE)
    public String handle(@RequestBody String xmlPayload) {
        GatewayContext context = xmlPayloadService.parse(xmlPayload);
        String traId = context.getTraId();
        TraceContext.setTraId(traId);
        long startAt = System.currentTimeMillis();
        try {
            log.info("traId={} Received /api/car/service request: {}", traId, xmlPayload);
            String response = gatewayService.handle(context);
            log.info("traId={} Completed /api/car/service in {} ms, response: {}", traId, System.currentTimeMillis() - startAt, response);
            return response;
        } catch (RuntimeException ex) {
            log.error("traId={} Failed /api/car/service in {} ms, request: {}", traId, System.currentTimeMillis() - startAt, xmlPayload, ex);
            throw ex;
        } finally {
            TraceContext.clear();
        }
    }
}
