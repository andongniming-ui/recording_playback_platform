package com.arex.demo.loan.service;

import com.arex.demo.loan.config.LoanVariantProperties;
import com.arex.demo.loan.repository.LoanDataRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class IncomeService {

    private static final Logger log = LoggerFactory.getLogger(IncomeService.class);

    @Autowired private LoanDataRepository repo;
    @Autowired private LoanVariantProperties variant;

    public Map<String, Object> check(Map<String, String> params) {
        String customerId = params.getOrDefault("customerId", "");
        String productId = params.getOrDefault("productId", "P001");
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> SVC IN | IncomeService.check | customer={} product={} variant={} | requestTime={}", traId, customerId, productId, variant.getLabel(), TraceContext.getRequestTime());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("traId", traId);
        result.put("requestTime", TraceContext.getRequestTime());
        result.put("customerId", customerId);
        result.put("productId", productId);

        Map<String, Object> customer = repo.findCustomer(customerId);
        Map<String, Object> product = repo.findProduct(productId);

        if (customer == null || product == null) {
            result.put("incomeCheck", "FAIL");
            result.put("reason", customer == null ? "CUSTOMER_NOT_FOUND" : "PRODUCT_NOT_FOUND");
            log.info("[{}] <<< SVC OUT | IncomeService.check | NOT_FOUND | elapsed={}ms", traId, TraceContext.getElapsedMs());
            return result;
        }

        double monthlyIncome = ((Number) customer.get("monthly_income")).doubleValue();
        double monthlyDebt = ((Number) customer.get("monthly_debt")).doubleValue();
        double minIncome = ((Number) product.get("min_income")).doubleValue();
        double productMaxDebtRatio = ((Number) product.get("max_debt_ratio")).doubleValue();

        double debtRatio = monthlyIncome > 0 ? monthlyDebt / monthlyIncome : 1.0;
        boolean incomeOk = monthlyIncome >= minIncome;
        double effectiveDebtLimit = variant.getMaxDebtRatio() > 0 ? variant.getMaxDebtRatio() : productMaxDebtRatio;
        boolean debtRatioOk = debtRatio <= effectiveDebtLimit;
        boolean passed = incomeOk && debtRatioOk;

        result.put("incomeCheck", passed ? "PASS" : "FAIL");
        result.put("monthlyIncome", monthlyIncome);
        result.put("monthlyDebt", monthlyDebt);
        result.put("debtRatio", Math.round(debtRatio * 10000) / 10000.0);
        result.put("debtRatioPercent", Math.round(debtRatio * 10000) / 100.0 + "%");
        result.put("minIncomeRequired", minIncome);
        result.put("incomeOk", incomeOk);
        result.put("effectiveDebtLimit", effectiveDebtLimit);
        result.put("debtRatioOk", debtRatioOk);

        if (!passed) {
            List<String> reasons = new ArrayList<>();
            if (!incomeOk) reasons.add("INCOME_BELOW_THRESHOLD");
            if (!debtRatioOk) reasons.add("DEBT_RATIO_EXCEEDED");
            result.put("reason", String.join(",", reasons));
        }

        log.info("[{}] <<< SVC OUT | IncomeService.check | passed={} debtRatio={} limit={} | elapsed={}ms",
                traId, passed, String.format("%.4f", debtRatio), effectiveDebtLimit, TraceContext.getElapsedMs());
        return result;
    }
}
