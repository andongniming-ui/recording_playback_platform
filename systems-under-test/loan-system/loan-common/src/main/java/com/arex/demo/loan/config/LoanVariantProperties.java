package com.arex.demo.loan.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/**
 * Variant properties that drive behavioral differences between old and new systems.
 * Old system: standard (correct) values
 * New system: "optimized" values that introduce subtle boundary bugs
 */
@Component
@ConfigurationProperties(prefix = "loan.variant")
public class LoanVariantProperties {

    private String label = "old";

    /** Age upper bound comparison mode: INCLUSIVE(<=) or EXCLUSIVE(<) */
    private String ageCheckMode = "INCLUSIVE";

    /** Risk score upper bound comparison mode: INCLUSIVE(>=) or EXCLUSIVE(>) for LOW risk */
    private String riskGradeMode = "INCLUSIVE";

    /** Maximum debt-to-income ratio threshold */
    private double maxDebtRatio = 0.50;

    /** Credit limit adjustment factor */
    private double creditAdjustFactor = 0.80;

    public String getLabel() { return label; }
    public void setLabel(String v) { this.label = v; }

    public String getAgeCheckMode() { return ageCheckMode; }
    public void setAgeCheckMode(String v) { this.ageCheckMode = v; }

    public String getRiskGradeMode() { return riskGradeMode; }
    public void setRiskGradeMode(String v) { this.riskGradeMode = v; }

    public double getMaxDebtRatio() { return maxDebtRatio; }
    public void setMaxDebtRatio(double v) { this.maxDebtRatio = v; }

    public double getCreditAdjustFactor() { return creditAdjustFactor; }
    public void setCreditAdjustFactor(double v) { this.creditAdjustFactor = v; }

    public boolean isAgeUpperExclusive() { return "EXCLUSIVE".equalsIgnoreCase(ageCheckMode); }
    public boolean isRiskScoreUpperExclusive() { return "EXCLUSIVE".equalsIgnoreCase(riskGradeMode); }
}
