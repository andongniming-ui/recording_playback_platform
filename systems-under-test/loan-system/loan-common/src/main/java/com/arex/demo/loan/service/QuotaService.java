package com.arex.demo.loan.service;

import com.arex.demo.loan.config.LoanVariantProperties;
import com.arex.demo.loan.repository.LoanDataRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class QuotaService {

    private static final Logger log = LoggerFactory.getLogger(QuotaService.class);

    @Autowired private LoanDataRepository repo;
    @Autowired private LoanVariantProperties variant;

    public Map<String, Object> calculate(Map<String, String> params) {
        String customerId = params.getOrDefault("customerId", "");
        String productId = params.getOrDefault("productId", "P001");
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> SVC IN | QuotaService.calculate | customer={} product={} variant={} | requestTime={}", traId, customerId, productId, variant.getLabel(), TraceContext.getRequestTime());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("traId", traId);
        result.put("requestTime", TraceContext.getRequestTime());
        result.put("customerId", customerId);
        result.put("productId", productId);

        Map<String, Object> customer = repo.findCustomer(customerId);
        Map<String, Object> product = repo.findProduct(productId);

        if (customer == null || product == null) {
            result.put("quota", 0);
            result.put("reason", customer == null ? "CUSTOMER_NOT_FOUND" : "PRODUCT_NOT_FOUND");
            log.info("[{}] <<< SVC OUT | QuotaService.calculate | NOT_FOUND | elapsed={}ms", traId, TraceContext.getElapsedMs());
            return result;
        }

        double monthlyIncome = ((Number) customer.get("monthly_income")).doubleValue();
        double monthlyDebt = ((Number) customer.get("monthly_debt")).doubleValue();
        double creditFactor = ((Number) product.get("credit_factor")).doubleValue();
        double debtRatio = monthlyIncome > 0 ? monthlyDebt / monthlyIncome : 1.0;
        double adjustFactor = variant.getCreditAdjustFactor();
        double quota = monthlyIncome * creditFactor * adjustFactor * (1.0 - debtRatio);
        quota = Math.round(quota * 100) / 100.0;
        if (quota < 0) quota = 0;

        result.put("quota", quota);
        result.put("monthlyIncome", monthlyIncome);
        result.put("creditFactor", creditFactor);
        result.put("adjustFactor", adjustFactor);
        result.put("debtRatio", Math.round(debtRatio * 10000) / 10000.0);
        result.put("formula", "income*creditFactor*adjustFactor*(1-debtRatio)");

        log.info("[{}] <<< SVC OUT | QuotaService.calculate | quota={} adjust={} | elapsed={}ms",
                traId, quota, adjustFactor, TraceContext.getElapsedMs());
        return result;
    }
}
