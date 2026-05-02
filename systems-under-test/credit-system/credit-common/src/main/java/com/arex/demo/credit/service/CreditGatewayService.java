package com.arex.demo.credit.service;

import com.arex.demo.credit.model.GatewayResult;
import org.springframework.stereotype.Service;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

@Service
public class CreditGatewayService {

    private final AdmitService admitService;
    private final LimitService limitService;

    public CreditGatewayService(AdmitService admitService, LimitService limitService) {
        this.admitService = admitService;
        this.limitService = limitService;
    }

    public GatewayResult process(Map<String, String> params) {
        String txnCode = params.get("txn_code");
        String validationError = validate(params);
        if (validationError != null) {
            return GatewayResult.error(txnCode, TraceContext.getTraId(), TraceContext.getRequestTime(), TraceContext.responseTime(), validationError);
        }
        if ("CRD_ADMIT".equals(txnCode)) {
            return admitService.process(params);
        }
        if ("CRD_LIMIT".equals(txnCode)) {
            return limitService.process(params);
        }
        return GatewayResult.error(txnCode, TraceContext.getTraId(), TraceContext.getRequestTime(), TraceContext.responseTime(), "UNKNOWN_TXN_CODE");
    }

    private String validate(Map<String, String> params) {
        List<String> required = Arrays.asList("txn_code", "request_no", "customer_id", "product_id", "apply_amount", "apply_term");
        for (String key : required) {
            if (blank(params.get(key))) {
                return "MISSING_REQUIRED_FIELD:" + key;
            }
        }

        String txnCode = params.get("txn_code");
        if ("CRD_ADMIT".equals(txnCode)) {
            List<String> admitRequired = Arrays.asList("tra_id", "request_time", "id_no", "mobile", "apply_city");
            for (String key : admitRequired) {
                if (blank(params.get(key))) {
                    return "MISSING_REQUIRED_FIELD:" + key;
                }
            }
            return null;
        }

        if ("CRD_LIMIT".equals(txnCode)) {
            List<String> limitRequired = Arrays.asList("tra_id", "request_time");
            for (String key : limitRequired) {
                if (blank(params.get(key))) {
                    return "MISSING_REQUIRED_FIELD:" + key;
                }
            }
            return null;
        }

        return null;
    }

    private boolean blank(String value) {
        return value == null || value.trim().isEmpty();
    }
}
