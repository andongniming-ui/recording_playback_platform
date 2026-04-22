package com.arex.demo.waimai.service;
import com.arex.demo.waimai.config.WaimaiVariantProperties;
import org.slf4j.Logger; import org.slf4j.LoggerFactory; import org.springframework.beans.factory.annotation.Autowired; import org.springframework.stereotype.Service;
import java.util.*;
@Service
public class InternalDeliveryTimeService {
    private static final Logger log = LoggerFactory.getLogger(InternalDeliveryTimeService.class);
    @Autowired private WaimaiVariantProperties variant;
    public Map<String,Object> estimate(Map<String,String> params) {
        log.info("[{}] DeliveryTime est, variant={}", TraceContext.getTraId(), variant.getLabel());
        int mins=new Random().nextInt(20)+15; boolean ins=variant.isEnableDeliveryInsurance();
        Map<String,Object> r=new LinkedHashMap<>(); r.put("estimatedMinutes",mins);
        r.put("deliveryInsurance",ins); r.put("maxCompensation",ins?"5.00":"0.00"); return r;
    }
}
