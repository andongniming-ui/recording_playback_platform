package com.arex.demo.loan.service;

import com.arex.demo.loan.config.LoanVariantProperties;
import com.arex.demo.loan.repository.LoanDataRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
public class QualifyService {

    private static final Logger log = LoggerFactory.getLogger(QualifyService.class);

    @Autowired private LoanDataRepository repo;
    @Autowired private LoanVariantProperties variant;

    public Map<String, Object> check(Map<String, String> params) {
        String customerId = params.getOrDefault("customerId", "");
        String productId = params.getOrDefault("productId", "P001");
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> SVC IN | QualifyService.check | customer={} product={} variant={} | requestTime={}", traId, customerId, productId, variant.getLabel(), TraceContext.getRequestTime());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("traId", traId);
        result.put("requestTime", TraceContext.getRequestTime());
        result.put("customerId", customerId);
        result.put("productId", productId);

        Map<String, Object> customer = repo.findCustomer(customerId);
        Map<String, Object> product = repo.findProduct(productId);

        if (customer == null) {
            result.put("qualified", false);
            result.put("reason", "CUSTOMER_NOT_FOUND");
            log.info("[{}] <<< SVC OUT | QualifyService.check | NOT_FOUND | elapsed={}ms", traId, TraceContext.getElapsedMs());
            return result;
        }
        if (product == null) {
            result.put("qualified", false);
            result.put("reason", "PRODUCT_NOT_FOUND");
            log.info("[{}] <<< SVC OUT | QualifyService.check | PRODUCT_NOT_FOUND | elapsed={}ms", traId, TraceContext.getElapsedMs());
            return result;
        }

        int age = ((Number) customer.get("age")).intValue();
        String status = (String) customer.get("status");
        String idCard = (String) customer.get("id_card");
        int minAge = ((Number) product.get("min_age")).intValue();
        int maxAge = ((Number) product.get("max_age")).intValue();

        boolean ageMinOk = age >= minAge;
        boolean ageMaxOk;
        if (variant.isAgeUpperExclusive()) {
            ageMaxOk = age < maxAge;
        } else {
            ageMaxOk = age <= maxAge;
        }
        boolean ageOk = ageMinOk && ageMaxOk;

        boolean idFormatOk = idCard != null && idCard.matches("\\d{17}[\\dXx]");
        boolean statusOk = "ACTIVE".equals(status);
        boolean qualified = ageOk && idFormatOk && statusOk;

        result.put("qualified", qualified);
        result.put("ageCheck", ageOk ? "PASS" : "FAIL");
        result.put("ageValue", age);
        result.put("ageRange", minAge + "-" + maxAge);
        result.put("ageCheckMode", variant.getAgeCheckMode());
        result.put("idFormatCheck", idFormatOk ? "PASS" : "FAIL");
        result.put("statusCheck", statusOk ? "PASS" : "FAIL");
        result.put("customerStatus", status);

        if (!qualified) {
            List<String> reasons = new ArrayList<>();
            if (!ageOk) reasons.add("AGE_OUT_OF_RANGE");
            if (!idFormatOk) reasons.add("ID_FORMAT_INVALID");
            if (!statusOk) reasons.add("STATUS_NOT_ACTIVE");
            result.put("reason", String.join(",", reasons));
        }

        log.info("[{}] <<< SVC OUT | QualifyService.check | qualified={} age={} mode={} | elapsed={}ms",
                traId, qualified, age, variant.getAgeCheckMode(), TraceContext.getElapsedMs());
        return result;
    }
}
