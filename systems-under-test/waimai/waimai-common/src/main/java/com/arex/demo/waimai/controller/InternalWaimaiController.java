package com.arex.demo.waimai.controller;
import com.arex.demo.waimai.model.GatewayResult;
import com.arex.demo.waimai.service.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.util.Map;

@RestController
@RequestMapping("/waimai/internal")
public class InternalWaimaiController {
    private static final Logger log = LoggerFactory.getLogger(InternalWaimaiController.class);
    @Autowired private InternalPricingService pricingService;
    @Autowired private InternalDiscountService discountService;
    @Autowired private InternalRiskService riskService;
    @Autowired private InternalDeliveryTimeService deliveryTimeService;

    @PostMapping("/pricing")
    public GatewayResult pricing(@RequestBody Map<String,String> req) {
        TraceContext.init();
        log.info("[{}] Internal pricing request, requestTime={}, body={}", TraceContext.getTraId(), TraceContext.getRequestTime(), req);
        try {
            GatewayResult result = GatewayResult.ok("INTERNAL_PRICING", pricingService.calculate(req));
            log.info("[{}] Internal pricing response, body={}", TraceContext.getTraId(), result.getData());
            return result;
        } finally { TraceContext.clear(); }
    }

    @PostMapping("/discount")
    public GatewayResult discount(@RequestBody Map<String,String> req) {
        TraceContext.init();
        log.info("[{}] Internal discount request, requestTime={}, body={}", TraceContext.getTraId(), TraceContext.getRequestTime(), req);
        try {
            GatewayResult result = GatewayResult.ok("INTERNAL_DISCOUNT", discountService.calculate(req));
            log.info("[{}] Internal discount response, body={}", TraceContext.getTraId(), result.getData());
            return result;
        } finally { TraceContext.clear(); }
    }

    @PostMapping("/risk")
    public GatewayResult risk(@RequestBody Map<String,String> req) {
        TraceContext.init();
        log.info("[{}] Internal risk request, requestTime={}, body={}", TraceContext.getTraId(), TraceContext.getRequestTime(), req);
        try {
            GatewayResult result = GatewayResult.ok("INTERNAL_RISK", riskService.evaluate(req));
            log.info("[{}] Internal risk response, body={}", TraceContext.getTraId(), result.getData());
            return result;
        } finally { TraceContext.clear(); }
    }

    @PostMapping("/delivery-time")
    public GatewayResult deliveryTime(@RequestBody Map<String,String> req) {
        TraceContext.init();
        log.info("[{}] Internal delivery-time request, requestTime={}, body={}", TraceContext.getTraId(), TraceContext.getRequestTime(), req);
        try {
            GatewayResult result = GatewayResult.ok("INTERNAL_DELIVERY_TIME", deliveryTimeService.estimate(req));
            log.info("[{}] Internal delivery-time response, body={}", TraceContext.getTraId(), result.getData());
            return result;
        } finally { TraceContext.clear(); }
    }
}
