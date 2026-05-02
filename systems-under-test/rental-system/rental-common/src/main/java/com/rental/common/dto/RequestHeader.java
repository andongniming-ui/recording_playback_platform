package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;

public class RequestHeader {
    @JacksonXmlProperty(localName = "serial_no")
    private String serialNo;
    private String timestamp;
    @JacksonXmlProperty(localName = "trans_code")
    private String transCode;

    public String getSerialNo() { return serialNo; }
    public void setSerialNo(String serialNo) { this.serialNo = serialNo; }
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    public String getTransCode() { return transCode; }
    public void setTransCode(String transCode) { this.transCode = transCode; }
}
