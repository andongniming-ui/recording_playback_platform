package com.arex.demo.dating.common.controller;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.arex.demo.dating.common.model.GatewayContext;
import com.arex.demo.dating.common.service.DatingGatewayService;
import com.arex.demo.dating.common.service.TraceContext;
import com.arex.demo.dating.common.service.XmlPayloadService;

/**
 * 交友系统网关控制器 - 接收 XML 格式请求
 * 所有交易统一通过 /api/dating/service 入口
 */
@RestController
@RequestMapping("/api/dating")
public class DatingGatewayController {

    private static final Logger log = LoggerFactory.getLogger(DatingGatewayController.class);

    private final DatingGatewayService gatewayService;
    private final XmlPayloadService xmlPayloadService;

    public DatingGatewayController(DatingGatewayService gatewayService,
                                   XmlPayloadService xmlPayloadService) {
        this.gatewayService = gatewayService;
        this.xmlPayloadService = xmlPayloadService;
    }

    @PostMapping(value = "/service",
        consumes = {MediaType.APPLICATION_XML_VALUE, MediaType.TEXT_XML_VALUE, MediaType.TEXT_PLAIN_VALUE},
        produces = MediaType.APPLICATION_XML_VALUE)
    public String handle(@RequestBody String xmlPayload) {
        // 解析 XML 报文
        GatewayContext context = xmlPayloadService.parse(xmlPayload);
        String traceId = context.getTraceId();
        TraceContext.setTraceId(traceId);

        long startAt = System.currentTimeMillis();
        try {
            log.info("traceId={} Received /api/dating/service request: {}", traceId, xmlPayload);
            String response = gatewayService.handle(context);
            log.info("traceId={} Completed /api/dating/service in {} ms, response: {}",
                traceId, System.currentTimeMillis() - startAt, response);
            return response;
        } catch (RuntimeException ex) {
            log.error("traceId={} Failed /api/dating/service in {} ms, request: {}",
                traceId, System.currentTimeMillis() - startAt, xmlPayload, ex);
            throw ex;
        } finally {
            TraceContext.clear();
        }
    }
}
