package com.arex.demo.loan.model;
import com.arex.demo.loan.service.TraceContext;
import java.util.Map;

public class GatewayResult {
    private String traId;
    private String requestTime;
    private String txnCode;
    private String status;
    private String message;
    private long elapsed;
    private Map<String, Object> body;

    public static GatewayResult ok(String txnCode, Map<String, Object> body) {
        GatewayResult r = new GatewayResult();
        r.setTraId(TraceContext.getTraId());
        r.setRequestTime(TraceContext.getRequestTime());
        r.setTxnCode(txnCode);
        r.setStatus("SUCCESS");
        r.setMessage("ok");
        r.setElapsed(TraceContext.getElapsedMs());
        r.setBody(body);
        return r;
    }

    public static GatewayResult fail(String txnCode, String msg) {
        GatewayResult r = new GatewayResult();
        r.setTraId(TraceContext.getTraId());
        r.setRequestTime(TraceContext.getRequestTime());
        r.setTxnCode(txnCode);
        r.setStatus("FAIL");
        r.setMessage(msg);
        r.setElapsed(TraceContext.getElapsedMs());
        return r;
    }

    public String getTraId() { return traId; } public void setTraId(String v) { this.traId = v; }
    public String getRequestTime() { return requestTime; } public void setRequestTime(String v) { this.requestTime = v; }
    public String getTxnCode() { return txnCode; } public void setTxnCode(String v) { this.txnCode = v; }
    public String getStatus() { return status; } public void setStatus(String v) { this.status = v; }
    public String getMessage() { return message; } public void setMessage(String v) { this.message = v; }
    public long getElapsed() { return elapsed; } public void setElapsed(long v) { this.elapsed = v; }
    public Map<String, Object> getBody() { return body; } public void setBody(Map<String, Object> v) { this.body = v; }
}
