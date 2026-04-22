package com.arex.demo.waimai.model;
import com.arex.demo.waimai.service.TraceContext;
import java.util.Map;
public class GatewayResult {
    private String traId; private String requestTime; private String txnCode; private String status; private String message; private Map<String,Object> data;

    public static GatewayResult ok(String txnCode, Map<String,Object> data) {
        GatewayResult r = new GatewayResult(); r.setTraId(TraceContext.getTraId()); r.setRequestTime(TraceContext.getRequestTime());
        r.setTxnCode(txnCode); r.setStatus("SUCCESS"); r.setMessage("ok"); r.setData(data); return r;
    }
    public static GatewayResult fail(String txnCode, String msg) {
        GatewayResult r = new GatewayResult(); r.setTraId(TraceContext.getTraId()); r.setRequestTime(TraceContext.getRequestTime());
        r.setTxnCode(txnCode); r.setStatus("FAIL"); r.setMessage(msg); return r;
    }

    public String getTraId() { return traId; } public void setTraId(String v) { this.traId = v; }
    public String getRequestTime() { return requestTime; } public void setRequestTime(String v) { this.requestTime = v; }
    public String getTxnCode() { return txnCode; } public void setTxnCode(String v) { this.txnCode = v; }
    public String getStatus() { return status; } public void setStatus(String v) { this.status = v; }
    public String getMessage() { return message; } public void setMessage(String v) { this.message = v; }
    public Map<String,Object> getData() { return data; } public void setData(Map<String,Object> v) { this.data = v; }
}
