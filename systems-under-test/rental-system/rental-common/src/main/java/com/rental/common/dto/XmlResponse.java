package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "response")
public class XmlResponse {
    @JacksonXmlProperty(localName = "header")
    private ResponseHeader header;
    @JacksonXmlProperty(localName = "body")
    private Object body;

    public XmlResponse() {}
    public XmlResponse(ResponseHeader header, Object body) {
        this.header = header;
        this.body = body;
    }

    public ResponseHeader getHeader() { return header; }
    public void setHeader(ResponseHeader header) { this.header = header; }
    public Object getBody() { return body; }
    public void setBody(Object body) { this.body = body; }
}
