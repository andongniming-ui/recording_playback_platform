package com.arex.demo.credit.service;

import com.arex.demo.credit.config.CreditProperties;
import com.arex.demo.credit.model.GatewayResult;
import com.arex.demo.credit.repository.CreditDataRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AdmitServiceTest {

    @Mock
    private CreditDataRepository repository;

    @Mock
    private ExternalDataService externalDataService;

    @Mock
    private RestTemplate restTemplate;

    private CreditProperties properties;
    private AdmitService admitService;

    @BeforeEach
    void setUp() {
        properties = new CreditProperties();
        properties.getInternal().setBaseUrl("http://credit-core-host:39081");
        admitService = new AdmitService(repository, externalDataService, properties, restTemplate);
        TraceContext.init("TRA-ADMIT-001", "20260424180100001");
    }

    @AfterEach
    void tearDown() {
        TraceContext.clear();
    }

    @Test
    void shouldShortCircuitWhenBlacklistHit() {
        Map<String, String> params = baseAdmitParams();
        when(repository.findCustomer("C10001")).thenReturn(customer());
        when(repository.findProductRule("P001")).thenReturn(product());
        when(repository.findBlacklist("C10001")).thenReturn(row("reason", "BLACKLIST"));

        GatewayResult result = admitService.process(params);

        assertEquals("SUCCESS", result.getStatus());
        assertEquals("REJECT", result.getBody().get("admit_result"));
        assertEquals("BLACKLIST_HIT", result.getBody().get("reject_reason"));
        verify(externalDataService, never()).queryCreditScore("C10001");
        verify(restTemplate, never()).getForObject(org.mockito.ArgumentMatchers.anyString(), eq(Map.class));
    }

    @Test
    void shouldUseConfiguredInternalBaseUrl() {
        Map<String, String> params = baseAdmitParams();
        when(repository.findCustomer("C10001")).thenReturn(customer());
        when(repository.findProductRule("P001")).thenReturn(product());
        when(repository.findBlacklist("C10001")).thenReturn(null);
        when(repository.findCreditHistory("C10001")).thenReturn(row("max_overdue_days_12m", 0));
        when(externalDataService.queryCreditScore("C10001")).thenReturn(row("creditScore", 78));
        when(externalDataService.queryFraud("C10001")).thenReturn(row("fraudLevel", "LOW"));
        when(restTemplate.getForObject(org.mockito.ArgumentMatchers.anyString(), eq(Map.class)))
                .thenReturn(row("riskLevel", "LOW", "decision", "PASS"));

        admitService.process(params);

        ArgumentCaptor<String> urlCaptor = ArgumentCaptor.forClass(String.class);
        verify(restTemplate).getForObject(urlCaptor.capture(), eq(Map.class));
        assertTrue(urlCaptor.getValue().startsWith("http://credit-core-host:39081/internal/credit/risk"));
    }

    private Map<String, String> baseAdmitParams() {
        Map<String, String> params = new LinkedHashMap<String, String>();
        params.put("txn_code", "CRD_ADMIT");
        params.put("tra_id", "TRA-ADMIT-001");
        params.put("request_time", "20260424180100001");
        params.put("request_no", "REQ-ADMIT-001");
        params.put("customer_id", "C10001");
        params.put("product_id", "P001");
        params.put("apply_amount", "80000");
        params.put("apply_term", "12");
        params.put("id_no", "310101199001011234");
        params.put("mobile", "13800000001");
        params.put("apply_city", "SHANGHAI");
        return params;
    }

    private Map<String, Object> customer() {
        Map<String, Object> row = new LinkedHashMap<String, Object>();
        row.put("customer_status", "ACTIVE");
        row.put("age", 35);
        row.put("monthly_income", new BigDecimal("18000.00"));
        return row;
    }

    private Map<String, Object> product() {
        Map<String, Object> row = new LinkedHashMap<String, Object>();
        row.put("min_age", 22);
        row.put("max_age", 55);
        row.put("min_income", new BigDecimal("5000.00"));
        row.put("base_limit_factor", new BigDecimal("4.0000"));
        row.put("max_limit", new BigDecimal("80000.00"));
        row.put("min_credit_score", 60);
        row.put("max_overdue_days", 30);
        return row;
    }

    private Map<String, Object> row(Object... values) {
        Map<String, Object> row = new LinkedHashMap<String, Object>();
        for (int i = 0; i < values.length; i += 2) {
            row.put(String.valueOf(values[i]), values[i + 1]);
        }
        return row;
    }
}
