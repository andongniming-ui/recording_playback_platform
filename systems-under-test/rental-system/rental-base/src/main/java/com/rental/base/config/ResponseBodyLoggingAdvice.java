package com.rental.base.config;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.xml.XmlMapper;
import com.rental.common.util.TransactionLogUtil;
import org.springframework.core.MethodParameter;
import org.springframework.http.MediaType;
import org.springframework.http.converter.HttpMessageConverter;
import org.springframework.http.server.ServerHttpRequest;
import org.springframework.http.server.ServerHttpResponse;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseBodyAdvice;

@ControllerAdvice
public class ResponseBodyLoggingAdvice implements ResponseBodyAdvice<Object> {
    private final ObjectMapper jsonMapper = new ObjectMapper();
    private final XmlMapper xmlMapper = new XmlMapper();

    @Override
    public boolean supports(MethodParameter returnType, Class<? extends HttpMessageConverter<?>> converterType) {
        return true;
    }

    @Override
    public Object beforeBodyWrite(Object body, MethodParameter returnType, MediaType selectedContentType,
                                  Class<? extends HttpMessageConverter<?>> selectedConverterType,
                                  ServerHttpRequest request, ServerHttpResponse response) {
        if (body == null) {
            TransactionLogUtil.setResponseBody("");
            return null;
        }
        try {
            if (MediaType.APPLICATION_XML.includes(selectedContentType)
                    || MediaType.TEXT_XML.includes(selectedContentType)) {
                TransactionLogUtil.setResponseBody(xmlMapper.writeValueAsString(body));
            } else if (MediaType.APPLICATION_JSON.includes(selectedContentType)) {
                TransactionLogUtil.setResponseBody(jsonMapper.writeValueAsString(body));
            } else {
                TransactionLogUtil.setResponseBody(String.valueOf(body));
            }
        } catch (Exception e) {
            TransactionLogUtil.setResponseBody(String.valueOf(body));
        }
        return body;
    }
}
