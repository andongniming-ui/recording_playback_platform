package com.arex.demo.didi.common.model;

import java.math.BigDecimal;

public class GatewayResult {

    private String status;
    private String message;
    private String customerTier;
    private String vehicleModel;
    private String riskLevel;
    private String decision;
    private String dispatchCity;
    private String policyStatus;
    private String dbFlag;
    private String subCallFlag;
    private BigDecimal baseAmount;
    private BigDecimal finalAmount;

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

    public String getCustomerTier() {
        return customerTier;
    }

    public void setCustomerTier(String customerTier) {
        this.customerTier = customerTier;
    }

    public String getVehicleModel() {
        return vehicleModel;
    }

    public void setVehicleModel(String vehicleModel) {
        this.vehicleModel = vehicleModel;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public String getDecision() {
        return decision;
    }

    public void setDecision(String decision) {
        this.decision = decision;
    }

    public String getDispatchCity() {
        return dispatchCity;
    }

    public void setDispatchCity(String dispatchCity) {
        this.dispatchCity = dispatchCity;
    }

    public String getPolicyStatus() {
        return policyStatus;
    }

    public void setPolicyStatus(String policyStatus) {
        this.policyStatus = policyStatus;
    }

    public String getDbFlag() {
        return dbFlag;
    }

    public void setDbFlag(String dbFlag) {
        this.dbFlag = dbFlag;
    }

    public String getSubCallFlag() {
        return subCallFlag;
    }

    public void setSubCallFlag(String subCallFlag) {
        this.subCallFlag = subCallFlag;
    }

    public BigDecimal getBaseAmount() {
        return baseAmount;
    }

    public void setBaseAmount(BigDecimal baseAmount) {
        this.baseAmount = baseAmount;
    }

    public BigDecimal getFinalAmount() {
        return finalAmount;
    }

    public void setFinalAmount(BigDecimal finalAmount) {
        this.finalAmount = finalAmount;
    }
}
