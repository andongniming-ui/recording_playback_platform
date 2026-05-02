package com.arex.demo.credit.service;

import com.arex.demo.credit.model.GatewayResult;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.LinkedHashMap;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class CreditGatewayServiceTest {

    @Mock
    private AdmitService admitService;

    @Mock
    private LimitService limitService;

    private CreditGatewayService gatewayService;

    @BeforeEach
    void setUp() {
        gatewayService = new CreditGatewayService(admitService, limitService);
        TraceContext.init("TRA-001", "20260424180000001");
    }

    @AfterEach
    void tearDown() {
        TraceContext.clear();
    }

    @Test
    void shouldReturnValidationErrorWhenRequiredFieldMissing() {
        Map<String, String> params = baseLimitParams();
        params.remove("request_no");

        GatewayResult result = gatewayService.process(params);

        assertEquals("ERROR", result.getStatus());
        assertEquals("MISSING_REQUIRED_FIELD:request_no", result.getBody().get("error_message"));
        verify(limitService, never()).process(params);
    }

    @Test
    void shouldDelegateToLimitServiceWhenParamsAreValid() {
        Map<String, String> params = baseLimitParams();
        GatewayResult expected = GatewayResult.success("CRD_LIMIT", "TRA-001", "20260424180000001", "20260424180000099", new LinkedHashMap<String, Object>());
        when(limitService.process(params)).thenReturn(expected);

        GatewayResult result = gatewayService.process(params);

        assertEquals(expected, result);
        verify(limitService).process(params);
    }

    private Map<String, String> baseLimitParams() {
        Map<String, String> params = new LinkedHashMap<String, String>();
        params.put("txn_code", "CRD_LIMIT");
        params.put("tra_id", "TRA-001");
        params.put("request_time", "20260424180000001");
        params.put("request_no", "REQ-001");
        params.put("customer_id", "C10001");
        params.put("product_id", "P001");
        params.put("apply_amount", "80000");
        params.put("apply_term", "12");
        return params;
    }
}
