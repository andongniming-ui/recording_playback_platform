package com.arex.demo.credit.service;

import com.arex.demo.credit.config.CreditProperties;
import com.arex.demo.credit.model.GatewayResult;
import com.arex.demo.credit.repository.CreditDataRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.LinkedHashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class LimitServiceTest {

    @Mock
    private CreditDataRepository repository;

    @Mock
    private ExternalDataService externalDataService;

    @Mock
    private RestTemplate restTemplate;

    private LimitService limitService;

    @BeforeEach
    void setUp() {
        CreditProperties properties = new CreditProperties();
        properties.getInternal().setBaseUrl("http://credit-core-host:39081");
        limitService = new LimitService(repository, externalDataService, properties, restTemplate);
        TraceContext.init("TRA-LIMIT-001", "20260424180200001");
    }

    @AfterEach
    void tearDown() {
        TraceContext.clear();
    }

    @Test
    void shouldKeepApprovedLimitAtLeastProductMinLimitAfterDowngrade() {
        Map<String, String> params = baseLimitParams();
        when(repository.findCustomer("C10005")).thenReturn(customer());
        when(repository.findProductRule("P002")).thenReturn(product());
        when(repository.findCreditHistory("C10005")).thenReturn(row("current_balance", new BigDecimal("26000.00"), "max_overdue_days_12m", 12));
        when(repository.findIncomeProof("C10005")).thenReturn(row("tax_verified", "N"));
        when(repository.findEmployment("C10005")).thenReturn(row("employment_status", "EMPLOYED"));
        when(externalDataService.queryCreditScore("C10005")).thenReturn(row("creditScore", 66));
        when(externalDataService.queryFraud("C10005")).thenReturn(row("fraudLevel", "MEDIUM"));
        when(externalDataService.queryMultiLoan("C10005")).thenReturn(row("loanPlatformCount", 5));
        when(restTemplate.getForObject(anyString(), eq(Map.class)))
                .thenReturn(row("riskLevel", "MEDIUM", "decision", "PASS"))
                .thenReturn(row("approvedLimit", new BigDecimal("10000.00"), "limitGrade", "C", "pricingRate", new BigDecimal("13.8")));

        GatewayResult result = limitService.process(params);

        assertEquals("PASS", result.getBody().get("limit_result"));
        assertEquals("10000.00", result.getBody().get("approved_limit"));
    }

    private Map<String, String> baseLimitParams() {
        Map<String, String> params = new LinkedHashMap<String, String>();
        params.put("txn_code", "CRD_LIMIT");
        params.put("tra_id", "TRA-LIMIT-001");
        params.put("request_time", "20260424180200001");
        params.put("request_no", "REQ-LIMIT-001");
        params.put("customer_id", "C10005");
        params.put("product_id", "P002");
        params.put("apply_amount", "120000");
        params.put("apply_term", "12");
        return params;
    }

    private Map<String, Object> customer() {
        Map<String, Object> row = new LinkedHashMap<String, Object>();
        row.put("monthly_income", new BigDecimal("12000.00"));
        return row;
    }

    private Map<String, Object> product() {
        Map<String, Object> row = new LinkedHashMap<String, Object>();
        row.put("base_limit_factor", new BigDecimal("3.5000"));
        row.put("min_limit", new BigDecimal("10000.00"));
        row.put("max_limit", new BigDecimal("120000.00"));
        row.put("annual_rate", new BigDecimal("12.6000"));
        row.put("term_options", "6,12");
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
