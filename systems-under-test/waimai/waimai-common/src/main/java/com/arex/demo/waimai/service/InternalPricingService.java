package com.arex.demo.waimai.service;
import com.arex.demo.waimai.config.WaimaiVariantProperties;
import org.slf4j.Logger; import org.slf4j.LoggerFactory; import org.springframework.beans.factory.annotation.Autowired; import org.springframework.stereotype.Service;
import java.util.*;
@Service
public class InternalPricingService {
    private static final Logger log = LoggerFactory.getLogger(InternalPricingService.class);
    @Autowired private WaimaiVariantProperties variant;
    public Map<String,Object> calculate(Map<String,String> params) {
        log.info("[{}] Pricing calc, variant={}", TraceContext.getTraId(), variant.getLabel());
        double base=Double.parseDouble(params.getOrDefault("basePrice","30.0"));
        double rate=variant.isDifferentPricing()?variant.getPricingAdjustRate():0.0;
        double fp=base*(1.0+rate); double ef=variant.isEnableExtraFee()?base*variant.getExtraFeeRate():0.0;
        Map<String,Object> r=new LinkedHashMap<>(); r.put("basePrice",base); r.put("adjustRate",rate);
        r.put("finalPrice",Math.round(fp*100)/100.0); r.put("extraFee",Math.round(ef*100)/100.0);
        r.put("totalPrice",Math.round((fp+ef)*100)/100.0); return r;
    }
}
