package com.arex.demo.dating.common.model;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 网关响应结果
 */
public class GatewayResult {

    private String status;
    private String message;
    private String subCallFlag;
    private String dbFlag;
    private String riskLevel;
    private String riskScore;
    private String auditResult;
    private String matchScore;
    private String filterLevel;
    private String payStatus;
    private String verifyStatus;
    private String storageUrl;
    private String violationType;
    private String blockStatus;
    private String registerStatus;
    private String msgCount;
    private String unreadCount;
    private final Map<String, String> resultData = new LinkedHashMap<String, String>();

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public String getSubCallFlag() {
        return subCallFlag;
    }

    public void setSubCallFlag(String subCallFlag) {
        this.subCallFlag = subCallFlag;
    }

    public String getDbFlag() {
        return dbFlag;
    }

    public void setDbFlag(String dbFlag) {
        this.dbFlag = dbFlag;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public String getRiskScore() {
        return riskScore;
    }

    public void setRiskScore(String riskScore) {
        this.riskScore = riskScore;
    }

    public String getAuditResult() {
        return auditResult;
    }

    public void setAuditResult(String auditResult) {
        this.auditResult = auditResult;
    }

    public String getMatchScore() {
        return matchScore;
    }

    public void setMatchScore(String matchScore) {
        this.matchScore = matchScore;
    }

    public String getFilterLevel() {
        return filterLevel;
    }

    public void setFilterLevel(String filterLevel) {
        this.filterLevel = filterLevel;
    }

    public String getPayStatus() {
        return payStatus;
    }

    public void setPayStatus(String payStatus) {
        this.payStatus = payStatus;
    }

    public String getVerifyStatus() {
        return verifyStatus;
    }

    public void setVerifyStatus(String verifyStatus) {
        this.verifyStatus = verifyStatus;
    }

    public String getStorageUrl() {
        return storageUrl;
    }

    public void setStorageUrl(String storageUrl) {
        this.storageUrl = storageUrl;
    }

    public String getViolationType() {
        return violationType;
    }

    public void setViolationType(String violationType) {
        this.violationType = violationType;
    }

    public String getBlockStatus() {
        return blockStatus;
    }

    public void setBlockStatus(String blockStatus) {
        this.blockStatus = blockStatus;
    }

    public String getRegisterStatus() {
        return registerStatus;
    }

    public void setRegisterStatus(String registerStatus) {
        this.registerStatus = registerStatus;
    }

    public String getMsgCount() {
        return msgCount;
    }

    public void setMsgCount(String msgCount) {
        this.msgCount = msgCount;
    }

    public String getUnreadCount() {
        return unreadCount;
    }

    public void setUnreadCount(String unreadCount) {
        this.unreadCount = unreadCount;
    }

    public Map<String, String> getResultData() {
        return resultData;
    }

    public void addResultData(String key, String value) {
        resultData.put(key, value);
    }
}
