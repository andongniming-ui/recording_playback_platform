package com.arex.demo.waimai.service;
import com.arex.demo.waimai.config.WaimaiVariantProperties;
import org.slf4j.Logger; import org.slf4j.LoggerFactory; import org.springframework.beans.factory.annotation.Autowired; import org.springframework.stereotype.Service;
import java.util.*;
@Service
public class InternalRiskService {
    private static final Logger log = LoggerFactory.getLogger(InternalRiskService.class);
    @Autowired private WaimaiVariantProperties variant;
    public Map<String,Object> evaluate(Map<String,String> params) {
        log.info("[{}] Risk eval, variant={}", TraceContext.getTraId(), variant.getLabel());
        int score=new Random().nextInt(40)+60; boolean pass=!variant.isStrictRisk()||score>=variant.getRiskThreshold();
        if(variant.isStrictRisk()&&score<variant.getRiskThreshold()) score=Math.min(score,variant.getRiskThreshold()-1);
        Map<String,Object> r=new LinkedHashMap<>(); r.put("riskScore",score); r.put("pass",pass);
        r.put("strictMode",variant.isStrictRisk()); r.put("threshold",variant.getRiskThreshold()); return r;
    }
}
