package com.arex.demo.credit.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "credit")
public class CreditProperties {

    private final Mock mock = new Mock();
    private final Internal internal = new Internal();
    private final Features features = new Features();

    public Mock getMock() {
        return mock;
    }

    public Internal getInternal() {
        return internal;
    }

    public Features getFeatures() {
        return features;
    }

    public static class Mock {
        private String baseUrl = "http://127.0.0.1:29083";

        public String getBaseUrl() {
            return baseUrl;
        }

        public void setBaseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
        }
    }

    public static class Internal {
        private String baseUrl = "http://127.0.0.1:29081";

        public String getBaseUrl() {
            return baseUrl;
        }

        public void setBaseUrl(String baseUrl) {
            this.baseUrl = baseUrl;
        }
    }

    public static class Features {
        private boolean enableExternalCache = true;
        private boolean enableContactStability = true;

        public boolean isEnableExternalCache() {
            return enableExternalCache;
        }

        public void setEnableExternalCache(boolean enableExternalCache) {
            this.enableExternalCache = enableExternalCache;
        }

        public boolean isEnableContactStability() {
            return enableContactStability;
        }

        public void setEnableContactStability(boolean enableContactStability) {
            this.enableContactStability = enableContactStability;
        }
    }
}
