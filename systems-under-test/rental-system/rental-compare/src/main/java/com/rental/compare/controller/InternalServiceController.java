package com.rental.compare.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.*;

@RestController
@RequestMapping("/api/internal")
public class InternalServiceController {

    private final ObjectMapper jsonMapper = new ObjectMapper();
    private final Random random = new Random();

    @GetMapping("/insurance/query")
    public Map<String, Object> insuranceQuery(@RequestParam Long vehicleId, @RequestParam String plateNumber) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("vehicle_id", vehicleId);
        result.put("plate_number", plateNumber);
        result.put("insurance_company", "中国人民保险");
        result.put("insurance_type", "全险");
        result.put("coverage_amount", "500000.00");
        result.put("is_valid", true);
        result.put("query_time", new Date().toString());
        return result;
    }

    @GetMapping("/vehicle/check")
    public Map<String, Object> vehicleCheck(@RequestParam Long vehicleId) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("vehicle_id", vehicleId);
        result.put("available", true);
        result.put("message", "车辆可租用");
        return result;
    }

    @GetMapping("/credit/check")
    public Map<String, Object> creditCheck(@RequestParam Long userId) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("user_id", userId);
        result.put("credit_score", 750 + random.nextInt(200));
        result.put("level", "GOOD");
        result.put("message", "信用良好，可租车");
        return result;
    }

    @GetMapping("/refund/calculate")
    public Map<String, Object> refundCalculate(@RequestParam String orderNo, @RequestParam String reason) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("order_no", orderNo);
        result.put("refund_percentage", "80");
        result.put("refund_fee", "0.00");
        result.put("message", "退款计算完成");
        return result;
    }

    @GetMapping("/damage/check")
    public Map<String, Object> damageCheck(@RequestParam String orderNo, @RequestParam(required = false) String damageDesc) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("order_no", orderNo);
        result.put("has_damage", damageDesc != null && !damageDesc.isEmpty());
        result.put("damage_fee", damageDesc != null && !damageDesc.isEmpty() ? "500.00" : "0.00");
        result.put("message", "车辆检查完成");
        return result;
    }

    @GetMapping("/pricing/query")
    public Map<String, Object> pricingQuery(@RequestParam Long vehicleId,
                                             @RequestParam String start,
                                             @RequestParam String end) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("vehicle_id", vehicleId);
        result.put("daily_rate", "300.00");
        result.put("service_fee", "50.00");
        result.put("insurance_fee", "30.00");
        result.put("message", "定价查询完成");
        return result;
    }

    @GetMapping("/payment-gateway/process")
    public Map<String, Object> paymentProcess(@RequestParam String orderNo,
                                               @RequestParam BigDecimal amount,
                                               @RequestParam String method) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("gateway_trade_no", "GT" + System.currentTimeMillis());
        result.put("order_no", orderNo);
        result.put("amount", amount);
        result.put("channel", "A");
        result.put("status", "SUCCESS");
        result.put("message", "支付处理成功");
        return result;
    }

    @GetMapping("/payment-gateway/query")
    public Map<String, Object> paymentGatewayQuery(@RequestParam String paymentNo) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("payment_no", paymentNo);
        result.put("gateway_status", "SUCCESS");
        result.put("gateway_trade_no", "GT" + System.currentTimeMillis());
        return result;
    }

    @GetMapping("/payment-gateway/refund")
    public Map<String, Object> paymentGatewayRefund(@RequestParam String paymentNo,
                                                     @RequestParam BigDecimal amount,
                                                     @RequestParam String reason) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("payment_no", paymentNo);
        result.put("refund_amount", amount);
        result.put("refund_status", "SUCCESS");
        result.put("message", "退款处理成功");
        return result;
    }

    @GetMapping("/reconciliation/query")
    public Map<String, Object> reconciliationQuery(@RequestParam String date) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("date", date);
        result.put("total_count", 45 + random.nextInt(20));
        result.put("total_amount", "12500.50");
        result.put("matched_count", 43 + random.nextInt(20));
        result.put("diff_count", 2);
        return result;
    }

    @GetMapping("/store/info")
    public Map<String, Object> storeInfo(@RequestParam Long storeId) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("store_id", storeId);
        result.put("current_vehicles", 15 + random.nextInt(20));
        result.put("staff_count", 5 + random.nextInt(10));
        return result;
    }

    @GetMapping("/report/generate")
    public Map<String, Object> reportGenerate(@RequestParam String type, @RequestParam String params) {
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("code", "0000");
        result.put("type", type);
        result.put("report_id", "RPT" + System.currentTimeMillis());
        result.put("generated", true);
        result.put("message", "报告生成成功");
        return result;
    }
}
