package com.arex.demo.waimai.model;
public class TxnDefinition {
    private String code; private String name; private String type; private String desc;
    public TxnDefinition(String code, String name, String type, String desc) { this.code=code; this.name=name; this.type=type; this.desc=desc; }
    public String getCode() { return code; } public String getName() { return name; }
    public String getType() { return type; } public String getDesc() { return desc; }
}
