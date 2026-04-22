package com.arex.demo.waimai.service;
import com.arex.demo.waimai.config.WaimaiVariantProperties;
import org.slf4j.Logger; import org.slf4j.LoggerFactory; import org.springframework.beans.factory.annotation.Autowired; import org.springframework.stereotype.Service;
import java.util.*;
@Service
public class InternalDiscountService {
    private static final Logger log = LoggerFactory.getLogger(InternalDiscountService.class);
    @Autowired private WaimaiVariantProperties variant;
    public Map<String,Object> calculate(Map<String,String> params) {
        log.info("[{}] Discount calc, variant={}", TraceContext.getTraId(), variant.getLabel());
        double orig=Double.parseDouble(params.getOrDefault("originalAmount","50.0"));
        double mult=variant.isDiscountGenerous()?variant.getDiscountMultiplier():1.0;
        double disc=orig*0.1*mult; double di=variant.isEnableDeliveryInsurance()?orig*variant.getDeliveryInsuranceRate():0.0;
        Map<String,Object> r=new LinkedHashMap<>(); r.put("originalAmount",orig); r.put("discountRate",0.1*mult);
        r.put("discountAmount",Math.round(disc*100)/100.0); r.put("deliveryInsurance",Math.round(di*100)/100.0);
        r.put("payableAmount",Math.round((orig-disc+di)*100)/100.0); return r;
    }
}
