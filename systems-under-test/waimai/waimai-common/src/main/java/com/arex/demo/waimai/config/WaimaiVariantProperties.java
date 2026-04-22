package com.arex.demo.waimai.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "waimai.variant")
public class WaimaiVariantProperties {
    private String label = "base";
    private boolean enableExtraFee = false;
    private double extraFeeRate = 0.0;
    private boolean strictRisk = false;
    private int riskThreshold = 80;
    private boolean discountGenerous = false;
    private double discountMultiplier = 1.0;
    private boolean enableDeliveryInsurance = false;
    private double deliveryInsuranceRate = 0.0;
    private boolean differentPricing = false;
    private double pricingAdjustRate = 0.0;
    private boolean stockPessimistic = false;
    private boolean reconciliationExtra = false;
    private String greeting = "欢迎光临";
    private String orderConfirmMsg = "下单成功";

    public String getLabel() { return label; } public void setLabel(String v) { this.label = v; }
    public boolean isEnableExtraFee() { return enableExtraFee; } public void setEnableExtraFee(boolean v) { this.enableExtraFee = v; }
    public double getExtraFeeRate() { return extraFeeRate; } public void setExtraFeeRate(double v) { this.extraFeeRate = v; }
    public boolean isStrictRisk() { return strictRisk; } public void setStrictRisk(boolean v) { this.strictRisk = v; }
    public int getRiskThreshold() { return riskThreshold; } public void setRiskThreshold(int v) { this.riskThreshold = v; }
    public boolean isDiscountGenerous() { return discountGenerous; } public void setDiscountGenerous(boolean v) { this.discountGenerous = v; }
    public double getDiscountMultiplier() { return discountMultiplier; } public void setDiscountMultiplier(double v) { this.discountMultiplier = v; }
    public boolean isEnableDeliveryInsurance() { return enableDeliveryInsurance; } public void setEnableDeliveryInsurance(boolean v) { this.enableDeliveryInsurance = v; }
    public double getDeliveryInsuranceRate() { return deliveryInsuranceRate; } public void setDeliveryInsuranceRate(double v) { this.deliveryInsuranceRate = v; }
    public boolean isDifferentPricing() { return differentPricing; } public void setDifferentPricing(boolean v) { this.differentPricing = v; }
    public double getPricingAdjustRate() { return pricingAdjustRate; } public void setPricingAdjustRate(double v) { this.pricingAdjustRate = v; }
    public boolean isStockPessimistic() { return stockPessimistic; } public void setStockPessimistic(boolean v) { this.stockPessimistic = v; }
    public boolean isReconciliationExtra() { return reconciliationExtra; } public void setReconciliationExtra(boolean v) { this.reconciliationExtra = v; }
    public String getGreeting() { return greeting; } public void setGreeting(String v) { this.greeting = v; }
    public String getOrderConfirmMsg() { return orderConfirmMsg; } public void setOrderConfirmMsg(String v) { this.orderConfirmMsg = v; }
}
