package com.rental.common.model;

public class TransactionLog {
    private Long id;
    private String serialNo;
    private String serviceName;
    private String methodName;
    private String requestBody;
    private String responseBody;
    private String subCalls;
    private String dbCalls;
    private Long elapsedMs;
    private java.util.Date createTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getSerialNo() { return serialNo; }
    public void setSerialNo(String serialNo) { this.serialNo = serialNo; }
    public String getServiceName() { return serviceName; }
    public void setServiceName(String serviceName) { this.serviceName = serviceName; }
    public String getMethodName() { return methodName; }
    public void setMethodName(String methodName) { this.methodName = methodName; }
    public String getRequestBody() { return requestBody; }
    public void setRequestBody(String requestBody) { this.requestBody = requestBody; }
    public String getResponseBody() { return responseBody; }
    public void setResponseBody(String responseBody) { this.responseBody = responseBody; }
    public String getSubCalls() { return subCalls; }
    public void setSubCalls(String subCalls) { this.subCalls = subCalls; }
    public String getDbCalls() { return dbCalls; }
    public void setDbCalls(String dbCalls) { this.dbCalls = dbCalls; }
    public Long getElapsedMs() { return elapsedMs; }
    public void setElapsedMs(Long elapsedMs) { this.elapsedMs = elapsedMs; }
    public java.util.Date getCreateTime() { return createTime; }
    public void setCreateTime(java.util.Date createTime) { this.createTime = createTime; }
}
