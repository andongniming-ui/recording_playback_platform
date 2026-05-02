package com.arex.demo.credit.model;

import java.util.LinkedHashMap;
import java.util.Map;

public class GatewayResult {

    private String txnCode;
    private String traId;
    private String requestTime;
    private String responseTime;
    private String status;
    private Map<String, Object> body = new LinkedHashMap<String, Object>();

    public static GatewayResult success(String txnCode, String traId, String requestTime, String responseTime, Map<String, Object> body) {
        GatewayResult result = new GatewayResult();
        result.setTxnCode(txnCode);
        result.setTraId(traId);
        result.setRequestTime(requestTime);
        result.setResponseTime(responseTime);
        result.setStatus("SUCCESS");
        result.setBody(body);
        return result;
    }

    public static GatewayResult error(String txnCode, String traId, String requestTime, String responseTime, String message) {
        Map<String, Object> body = new LinkedHashMap<String, Object>();
        body.put("error_message", message);
        GatewayResult result = success(txnCode, traId, requestTime, responseTime, body);
        result.setStatus("ERROR");
        return result;
    }

    public String getTxnCode() {
        return txnCode;
    }

    public void setTxnCode(String txnCode) {
        this.txnCode = txnCode;
    }

    public String getTraId() {
        return traId;
    }

    public void setTraId(String traId) {
        this.traId = traId;
    }

    public String getRequestTime() {
        return requestTime;
    }

    public void setRequestTime(String requestTime) {
        this.requestTime = requestTime;
    }

    public String getResponseTime() {
        return responseTime;
    }

    public void setResponseTime(String responseTime) {
        this.responseTime = responseTime;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Map<String, Object> getBody() {
        return body;
    }

    public void setBody(Map<String, Object> body) {
        this.body = body;
    }
}
