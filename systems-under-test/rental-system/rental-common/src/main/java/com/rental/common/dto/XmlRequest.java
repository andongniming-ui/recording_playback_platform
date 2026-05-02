package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "request")
public class XmlRequest {
    @JacksonXmlProperty(localName = "header")
    private RequestHeader header;
    @JacksonXmlProperty(localName = "body")
    private Object body;

    public RequestHeader getHeader() { return header; }
    public void setHeader(RequestHeader header) { this.header = header; }
    public Object getBody() { return body; }
    public void setBody(Object body) { this.body = body; }
}
