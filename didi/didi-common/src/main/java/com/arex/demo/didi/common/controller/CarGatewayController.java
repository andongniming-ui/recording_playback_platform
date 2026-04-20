package com.arex.demo.didi.common.controller;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.arex.demo.didi.common.service.CarGatewayService;

@RestController
@RequestMapping("/api/car")
public class CarGatewayController {

    private final CarGatewayService gatewayService;

    public CarGatewayController(CarGatewayService gatewayService) {
        this.gatewayService = gatewayService;
    }

    @PostMapping(value = "/service", consumes = {MediaType.APPLICATION_XML_VALUE, MediaType.TEXT_XML_VALUE, MediaType.TEXT_PLAIN_VALUE}, produces = MediaType.APPLICATION_XML_VALUE)
    public String handle(@RequestBody String xmlPayload) {
        return gatewayService.handle(xmlPayload);
    }
}
