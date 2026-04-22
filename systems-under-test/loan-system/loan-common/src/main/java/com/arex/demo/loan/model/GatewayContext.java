package com.arex.demo.loan.model;
import java.util.Map;
public class GatewayContext {
    private String traId;
    private String requestTime;
    private String txnCode;
    private Map<String, String> params;
    public String getTraId() { return traId; } public void setTraId(String v) { this.traId = v; }
    public String getRequestTime() { return requestTime; } public void setRequestTime(String v) { this.requestTime = v; }
    public String getTxnCode() { return txnCode; } public void setTxnCode(String v) { this.txnCode = v; }
    public Map<String, String> getParams() { return params; } public void setParams(Map<String, String> v) { this.params = v; }
}
