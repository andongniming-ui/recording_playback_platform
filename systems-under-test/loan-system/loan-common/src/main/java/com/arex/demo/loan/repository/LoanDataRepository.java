package com.arex.demo.loan.repository;

import com.arex.demo.loan.service.TraceContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.*;

@Repository
public class LoanDataRepository {

    private static final Logger log = LoggerFactory.getLogger(LoanDataRepository.class);

    @Autowired
    private JdbcTemplate jdbc;

    public Map<String, Object> findCustomer(String customerId) {
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> DB QUERY | table=customer | key=customer_id={} | requestTime={}", traId, customerId, TraceContext.getRequestTime());
        long start = System.currentTimeMillis();
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT customer_id, name, id_card, age, status, monthly_income, monthly_debt FROM customer WHERE customer_id = ?",
                customerId);
        long elapsed = System.currentTimeMillis() - start;
        Map<String, Object> result = rows.isEmpty() ? null : rows.get(0);
        log.info("[{}] <<< DB RESULT | table=customer | found={} | elapsed={}ms | data={}", traId, result != null, elapsed, summarize(result));
        return result;
    }

    public Map<String, Object> findProduct(String productId) {
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> DB QUERY | table=product_rule | key=product_id={} | requestTime={}", traId, productId, TraceContext.getRequestTime());
        long start = System.currentTimeMillis();
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT product_id, product_name, min_age, max_age, min_income, max_debt_ratio, credit_factor, status FROM product_rule WHERE product_id = ?",
                productId);
        long elapsed = System.currentTimeMillis() - start;
        Map<String, Object> result = rows.isEmpty() ? null : rows.get(0);
        log.info("[{}] <<< DB RESULT | table=product_rule | found={} | elapsed={}ms | data={}", traId, result != null, elapsed, summarize(result));
        return result;
    }

    public boolean isOnBlacklist(String customerId) {
        String traId = TraceContext.getTraId();
        log.info("[{}] >>> DB QUERY | table=blacklist | key=customer_id={} | requestTime={}", traId, customerId, TraceContext.getRequestTime());
        long start = System.currentTimeMillis();
        List<Map<String, Object>> rows = jdbc.queryForList(
                "SELECT id FROM blacklist WHERE customer_id = ?", customerId);
        long elapsed = System.currentTimeMillis() - start;
        boolean onBlacklist = !rows.isEmpty();
        log.info("[{}] <<< DB RESULT | table=blacklist | found={} | elapsed={}ms", traId, onBlacklist, elapsed);
        return onBlacklist;
    }

    private String summarize(Map<String, Object> data) {
        if (data == null) return "NOT_FOUND";
        String s = data.toString();
        return s.length() > 300 ? s.substring(0, 300) + "..." : s;
    }
}
