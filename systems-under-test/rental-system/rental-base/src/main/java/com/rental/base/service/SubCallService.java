package com.rental.base.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import java.math.BigDecimal;
import java.util.*;

@Service
public class SubCallService {
    private static final Logger log = LoggerFactory.getLogger(SubCallService.class);

    @Autowired
    private RestTemplate restTemplate;

    @Value("${server.port}")
    private int serverPort;

    private String internalBase() {
        return "http://localhost:" + serverPort + "/api/internal";
    }

    public Map<String, Object> queryInsurance(Long vehicleId, String plateNumber, String serialNo) {
        try {
            String url = internalBase() + "/insurance/query?vehicleId=" + vehicleId + "&plateNumber=" + plateNumber;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "insurance_service");
            result.put("url", url);
            result.put("request", "vehicleId=" + vehicleId + "&plateNumber=" + plateNumber);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(100) + 20);
            result.put("status", "SUCCESS");
            log.debug("[SUB_CALL] insurance query: {}", result);
            return result;
        } catch (Exception e) {
            log.warn("Sub-call insurance query failed: {}", e.getMessage());
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "insurance_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> checkVehicleAvailability(Long vehicleId, String serialNo) {
        try {
            String url = internalBase() + "/vehicle/check?vehicleId=" + vehicleId;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "vehicle_check_service");
            result.put("url", url);
            result.put("request", "vehicleId=" + vehicleId);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(80) + 10);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "vehicle_check_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> checkUserCredit(Long userId, String serialNo) {
        try {
            String url = internalBase() + "/credit/check?userId=" + userId;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "credit_check_service");
            result.put("url", url);
            result.put("request", "userId=" + userId);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(150) + 50);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "credit_check_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> calculateRefund(String orderNo, String cancelReason, String serialNo) {
        try {
            String url = internalBase() + "/refund/calculate?orderNo=" + orderNo + "&reason=" + cancelReason;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "refund_service");
            result.put("url", url);
            result.put("request", "orderNo=" + orderNo + "&reason=" + cancelReason);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(100) + 30);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "refund_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> checkDamage(String orderNo, String damageDesc, String serialNo) {
        try {
            String url = internalBase() + "/damage/check?orderNo=" + orderNo + "&damageDesc=" + (damageDesc != null ? damageDesc : "");
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "damage_check_service");
            result.put("url", url);
            result.put("request", "orderNo=" + orderNo + "&damageDesc=" + damageDesc);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(200) + 50);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "damage_check_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> queryPricing(Long vehicleId, String startTime, String endTime, String serialNo) {
        try {
            String url = internalBase() + "/pricing/query?vehicleId=" + vehicleId + "&start=" + startTime + "&end=" + endTime;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "pricing_service");
            result.put("url", url);
            result.put("request", "vehicleId=" + vehicleId + "&start=" + startTime + "&end=" + endTime);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(120) + 30);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "pricing_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> processPayment(String orderNo, BigDecimal amount, String paymentMethod, String serialNo) {
        try {
            String url = internalBase() + "/payment-gateway/process?orderNo=" + orderNo + "&amount=" + amount + "&method=" + paymentMethod;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "payment_gateway");
            result.put("url", url);
            result.put("request", "orderNo=" + orderNo + "&amount=" + amount + "&method=" + paymentMethod);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(300) + 100);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "payment_gateway");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> queryPaymentGateway(String paymentNo, String serialNo) {
        try {
            String url = internalBase() + "/payment-gateway/query?paymentNo=" + paymentNo;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "payment_gateway");
            result.put("url", url);
            result.put("request", "paymentNo=" + paymentNo);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(80) + 20);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "payment_gateway");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> refundPayment(String paymentNo, BigDecimal amount, String reason, String serialNo) {
        try {
            String url = internalBase() + "/payment-gateway/refund?paymentNo=" + paymentNo + "&amount=" + amount + "&reason=" + reason;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "payment_gateway");
            result.put("url", url);
            result.put("request", "paymentNo=" + paymentNo + "&amount=" + amount + "&reason=" + reason);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(200) + 80);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "payment_gateway");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> queryReconciliation(String date, String serialNo) {
        try {
            String url = internalBase() + "/reconciliation/query?date=" + date;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "reconciliation_service");
            result.put("url", url);
            result.put("request", "date=" + date);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(200) + 100);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "reconciliation_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> queryStoreInfo(Long storeId, String serialNo) {
        try {
            String url = internalBase() + "/store/info?storeId=" + storeId;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "store_service");
            result.put("url", url);
            result.put("request", "storeId=" + storeId);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(50) + 10);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "store_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }

    public Map<String, Object> queryReportService(String type, String params, String serialNo) {
        try {
            String url = internalBase() + "/report/generate?type=" + type + "&params=" + params;
            String response = restTemplate.getForObject(url, String.class);
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("type", "HttpClient");
            result.put("source", "report_service");
            result.put("url", url);
            result.put("request", "type=" + type + "&params=" + params);
            result.put("response", response);
            result.put("elapsed_ms", new Random().nextInt(250) + 100);
            result.put("status", "SUCCESS");
            return result;
        } catch (Exception e) {
            Map<String, Object> errResult = new LinkedHashMap<>();
            errResult.put("type", "HttpClient");
            errResult.put("source", "report_service");
            errResult.put("status", "ERROR");
            errResult.put("error", e.getMessage());
            return errResult;
        }
    }
}
