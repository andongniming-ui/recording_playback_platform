package com.arex.demo.dating.common.model;

/**
 * 交易码定义
 */
public class DatingTransactionDefinition {

    private final String code;
    private final String requestField;
    private final String displayName;
    private final String subCallPath;
    private final String description;

    public DatingTransactionDefinition(String code, String requestField, String displayName,
                                       String subCallPath, String description) {
        this.code = code;
        this.requestField = requestField;
        this.displayName = displayName;
        this.subCallPath = subCallPath;
        this.description = description;
    }

    public String getCode() {
        return code;
    }

    public String getRequestField() {
        return requestField;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getSubCallPath() {
        return subCallPath;
    }

    public String getDescription() {
        return description;
    }

    @Override
    public String toString() {
        return "DatingTransactionDefinition{code='" + code + "', displayName='" + displayName + "'}";
    }
}
