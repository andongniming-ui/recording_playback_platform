package com.arex.demo.dating.common.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 交友系统变体配置 - 支持 SAT/UAT 双发比对
 */
@Component
@ConfigurationProperties(prefix = "dating")
public class DatingVariantProperties {

    private String systemName;
    private String variantId;
    private String compareHint;
    private String internalBaseUrl;
    private Map<String, VariantOverride> overrides = new LinkedHashMap<String, VariantOverride>();

    public String getSystemName() {
        return systemName;
    }

    public void setSystemName(String systemName) {
        this.systemName = systemName;
    }

    public String getVariantId() {
        return variantId;
    }

    public void setVariantId(String variantId) {
        this.variantId = variantId;
    }

    public String getCompareHint() {
        return compareHint;
    }

    public void setCompareHint(String compareHint) {
        this.compareHint = compareHint;
    }

    public String getInternalBaseUrl() {
        return internalBaseUrl;
    }

    public void setInternalBaseUrl(String internalBaseUrl) {
        this.internalBaseUrl = internalBaseUrl;
    }

    public Map<String, VariantOverride> getOverrides() {
        return overrides;
    }

    public void setOverrides(Map<String, VariantOverride> overrides) {
        this.overrides = overrides;
    }

    public VariantOverride overrideOf(String tranCode) {
        VariantOverride override = overrides.get(tranCode);
        return override != null ? override : new VariantOverride();
    }

    public static class VariantOverride {
        private String messageSuffix;
        private String riskLevel;
        private String matchScore;
        private String payStatus;

        public String getMessageSuffix() {
            return messageSuffix;
        }

        public void setMessageSuffix(String messageSuffix) {
            this.messageSuffix = messageSuffix;
        }

        public String getRiskLevel() {
            return riskLevel;
        }

        public void setRiskLevel(String riskLevel) {
            this.riskLevel = riskLevel;
        }

        public String getMatchScore() {
            return matchScore;
        }

        public void setMatchScore(String matchScore) {
            this.matchScore = matchScore;
        }

        public String getPayStatus() {
            return payStatus;
        }

        public void setPayStatus(String payStatus) {
            this.payStatus = payStatus;
        }
    }
}
