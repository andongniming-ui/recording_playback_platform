package com.arex.demo.loan.service;

import com.arex.demo.loan.config.LoanVariantProperties;
import com.arex.demo.loan.model.GatewayResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class LoanGatewayService {

    private static final Logger log = LoggerFactory.getLogger(LoanGatewayService.class);

    @Autowired private XmlPayloadService xmlPayloadService;
    @Autowired private QualifyService qualifyService;
    @Autowired private CreditService creditService;
    @Autowired private IncomeService incomeService;
    @Autowired private QuotaService quotaService;
    @Autowired private AdmitService admitService;
    @Autowired private LoanVariantProperties variant;

    public String extractTxnCode(String xml) { return xmlPayloadService.extractTxnCode(xml); }
    public Map<String,String> extractParams(String xml) { return xmlPayloadService.extractParams(xml); }

    public String processXml(String txnCode, Map<String,String> params) {
        Map<String,Object> body = process(txnCode, params);
        return xmlPayloadService.buildResponse(txnCode, body);
    }

    public GatewayResult processJson(String txnCode, Map<String,String> params) {
        Map<String,Object> body = process(txnCode, params);
        return GatewayResult.ok(txnCode, body);
    }

    private Map<String,Object> process(String txnCode, Map<String,String> params) {
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> ROUTE | txnCode={} | variant={} | requestTime={}", traId, txnCode, variant.getLabel(), TraceContext.getRequestTime());
        Map<String,Object> result;
        switch (txnCode) {
            case "LOAN_QUALIFY": result = qualifyService.check(params); break;
            case "LOAN_CREDIT":  result = creditService.check(params); break;
            case "LOAN_INCOME":  result = incomeService.check(params); break;
            case "LOAN_QUOTA":   result = quotaService.calculate(params); break;
            case "LOAN_ADMIT":   result = admitService.assess(params); break;
            default:
                result = new LinkedHashMap<>();
                result.put("traId", traId);
                result.put("requestTime", TraceContext.getRequestTime());
                result.put("error", "UNKNOWN_TXN_CODE");
                result.put("txnCode", txnCode);
        }
        return result;
    }
}
