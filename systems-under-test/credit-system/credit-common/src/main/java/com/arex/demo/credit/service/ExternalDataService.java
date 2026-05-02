package com.arex.demo.credit.service;

import com.arex.demo.credit.config.CreditProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class ExternalDataService {

    private static final Logger log = LoggerFactory.getLogger(ExternalDataService.class);

    private final RestTemplate restTemplate;
    private final CreditProperties creditProperties;

    public ExternalDataService(RestTemplate restTemplate, CreditProperties creditProperties) {
        this.restTemplate = restTemplate;
        this.creditProperties = creditProperties;
    }

    public Map<String, Object> queryCreditScore(String customerId) {
        return doGet("credit-score", "/mock/credit-score?customerId=" + customerId);
    }

    public Map<String, Object> queryFraud(String customerId) {
        return doGet("fraud", "/mock/fraud?customerId=" + customerId);
    }

    public Map<String, Object> queryMultiLoan(String customerId) {
        return doGet("multi-loan", "/mock/multi-loan?customerId=" + customerId);
    }

    public Map<String, Object> queryContactStability(String customerId) {
        return doGet("contact-stability", "/mock/contact-stability?customerId=" + customerId);
    }

    private Map<String, Object> doGet(String label, String path) {
        String url = creditProperties.getMock().getBaseUrl() + path;
        log.info("traId={} HTTP sub-call request: {}", TraceContext.getTraId(), url);
        ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                url,
                HttpMethod.GET,
                null,
                new ParameterizedTypeReference<Map<String, Object>>() {}
        );
        Map<String, Object> body = response.getBody() == null ? Collections.<String, Object>emptyMap() : response.getBody();
        log.info("traId={} HTTP sub-call response: status={}, body={}", TraceContext.getTraId(), response.getStatusCodeValue(), body);
        Map<String, Object> result = new LinkedHashMap<String, Object>();
        result.putAll(body);
        result.put("_label", label);
        result.put("_url", url);
        return result;
    }
}
