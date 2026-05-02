package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;

public class ResponseHeader {
    @JacksonXmlProperty(localName = "serial_no")
    private String serialNo;
    private String timestamp;
    private String code;
    private String message;

    public ResponseHeader() {}
    public ResponseHeader(String serialNo, String code, String message) {
        this.serialNo = serialNo;
        this.timestamp = com.rental.common.util.DateTimeUtil.now();
        this.code = code;
        this.message = message;
    }

    public String getSerialNo() { return serialNo; }
    public void setSerialNo(String serialNo) { this.serialNo = serialNo; }
    public String getTimestamp() { return timestamp; }
    public void setTimestamp(String timestamp) { this.timestamp = timestamp; }
    public String getCode() { return code; }
    public void setCode(String code) { this.code = code; }
    public String getMessage() { return message; }
    public void setMessage(String message) { this.message = message; }
}
