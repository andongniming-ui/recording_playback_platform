package com.arex.demo.didi.common.model;

import java.math.BigDecimal;

public class CarTransactionDefinition {

    private final String code;
    private final String requestField;
    private final String displayName;
    private final boolean complex;
    private final BigDecimal baseAmount;

    public CarTransactionDefinition(String code, String requestField, String displayName, boolean complex, BigDecimal baseAmount) {
        this.code = code;
        this.requestField = requestField;
        this.displayName = displayName;
        this.complex = complex;
        this.baseAmount = baseAmount;
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

    public boolean isComplex() {
        return complex;
    }

    public BigDecimal getBaseAmount() {
        return baseAmount;
    }
}
