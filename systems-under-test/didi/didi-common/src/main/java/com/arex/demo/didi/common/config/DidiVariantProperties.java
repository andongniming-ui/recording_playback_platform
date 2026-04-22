package com.arex.demo.didi.common.config;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "didi")
public class DidiVariantProperties {

    private String systemName = "didi-system";
    private String variantId = "base";
    private String compareHint = "BASELINE";
    private String internalBaseUrl = "http://127.0.0.1:${server.port}";
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

    public VariantOverride overrideOf(String code) {
        VariantOverride override = overrides.get(code);
        return override == null ? new VariantOverride() : override;
    }

    public static class VariantOverride {
        private String messageSuffix = "";
        private BigDecimal amountDelta = BigDecimal.ZERO;
        private String riskLevel;
        private String decision;
        private String dispatchCity;

        public String getMessageSuffix() {
            return messageSuffix;
        }

        public void setMessageSuffix(String messageSuffix) {
            this.messageSuffix = messageSuffix;
        }

        public BigDecimal getAmountDelta() {
            return amountDelta;
        }

        public void setAmountDelta(BigDecimal amountDelta) {
            this.amountDelta = amountDelta == null ? BigDecimal.ZERO : amountDelta;
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
    }
}
