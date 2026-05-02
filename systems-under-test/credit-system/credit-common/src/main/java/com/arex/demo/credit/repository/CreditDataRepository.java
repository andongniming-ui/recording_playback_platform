package com.arex.demo.credit.repository;

import com.arex.demo.credit.service.TraceContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Map;

@Repository
public class CreditDataRepository {

    private static final Logger log = LoggerFactory.getLogger(CreditDataRepository.class);

    private final JdbcTemplate jdbcTemplate;

    public CreditDataRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public Map<String, Object> findCustomer(String customerId) {
        String sql = "select * from credit_customer where customer_id = ?";
        log.info("traId={} DB query findCustomer: sql={}, arg={}", TraceContext.getTraId(), sql, customerId);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, customerId);
        Map<String, Object> row = rows.isEmpty() ? null : rows.get(0);
        log.info("traId={} DB query findCustomer result: {}", TraceContext.getTraId(), summarize(row));
        return row;
    }

    public Map<String, Object> findProductRule(String productId) {
        String sql = "select * from credit_product_rule where product_id = ?";
        log.info("traId={} DB query findProductRule: sql={}, arg={}", TraceContext.getTraId(), sql, productId);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, productId);
        Map<String, Object> row = rows.isEmpty() ? null : rows.get(0);
        log.info("traId={} DB query findProductRule result: {}", TraceContext.getTraId(), summarize(row));
        return row;
    }

    public Map<String, Object> findBlacklist(String customerId) {
        String sql = "select * from credit_blacklist where customer_id = ? and status = 'ACTIVE' order by id desc limit 1";
        log.info("traId={} DB query findBlacklist: sql={}, arg={}", TraceContext.getTraId(), sql, customerId);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, customerId);
        Map<String, Object> row = rows.isEmpty() ? null : rows.get(0);
        log.info("traId={} DB query findBlacklist result: {}", TraceContext.getTraId(), summarize(row));
        return row;
    }

    public Map<String, Object> findCreditHistory(String customerId) {
        String sql = "select * from credit_history where customer_id = ?";
        log.info("traId={} DB query findCreditHistory: sql={}, arg={}", TraceContext.getTraId(), sql, customerId);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, customerId);
        Map<String, Object> row = rows.isEmpty() ? null : rows.get(0);
        log.info("traId={} DB query findCreditHistory result: {}", TraceContext.getTraId(), summarize(row));
        return row;
    }

    public Map<String, Object> findIncomeProof(String customerId) {
        String sql = "select * from credit_income_proof where customer_id = ?";
        log.info("traId={} DB query findIncomeProof: sql={}, arg={}", TraceContext.getTraId(), sql, customerId);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, customerId);
        Map<String, Object> row = rows.isEmpty() ? null : rows.get(0);
        log.info("traId={} DB query findIncomeProof result: {}", TraceContext.getTraId(), summarize(row));
        return row;
    }

    public Map<String, Object> findEmployment(String customerId) {
        String sql = "select * from credit_employment where customer_id = ?";
        log.info("traId={} DB query findEmployment: sql={}, arg={}", TraceContext.getTraId(), sql, customerId);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, customerId);
        Map<String, Object> row = rows.isEmpty() ? null : rows.get(0);
        log.info("traId={} DB query findEmployment result: {}", TraceContext.getTraId(), summarize(row));
        return row;
    }

    public int saveApplyAudit(Map<String, Object> payload) {
        String sql = "insert into credit_apply_audit (txn_code, tra_id, request_time, request_no, customer_id, product_id, apply_amount, apply_term, credit_score, fraud_level, multi_loan_count, risk_level, admit_result, approved_limit, limit_grade, pricing_rate, decision_reason) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        int affected = jdbcTemplate.update(
                sql,
                payload.get("txnCode"),
                payload.get("traId"),
                payload.get("requestTime"),
                payload.get("requestNo"),
                payload.get("customerId"),
                payload.get("productId"),
                payload.get("applyAmount"),
                payload.get("applyTerm"),
                payload.get("creditScore"),
                payload.get("fraudLevel"),
                payload.get("multiLoanCount"),
                payload.get("riskLevel"),
                payload.get("admitResult"),
                payload.get("approvedLimit"),
                payload.get("limitGrade"),
                payload.get("pricingRate"),
                payload.get("decisionReason")
        );
        log.info("traId={} DB update saveApplyAudit: payload={}, affectedRows={}", TraceContext.getTraId(), payload, affected);
        return affected;
    }

    public int saveExternalCache(String traId, String customerId, String extType, String request, String response) {
        String sql = "insert into credit_external_cache (tra_id, customer_id, ext_type, ext_request, ext_response) values (?, ?, ?, ?, ?)";
        int affected = jdbcTemplate.update(sql, traId, customerId, extType, request, response);
        log.info("traId={} DB update saveExternalCache: extType={}, customerId={}, affectedRows={}", TraceContext.getTraId(), extType, customerId, affected);
        return affected;
    }

    public int saveRiskStrategyLog(String traId, String customerId, String productId, String strategyName, String strategyResult, String strategyDetail) {
        String sql = "insert into credit_risk_strategy_log (tra_id, customer_id, product_id, strategy_name, strategy_result, strategy_detail) values (?, ?, ?, ?, ?, ?)";
        int affected = jdbcTemplate.update(sql, traId, customerId, productId, strategyName, strategyResult, strategyDetail);
        log.info("traId={} DB update saveRiskStrategyLog: strategyName={}, strategyResult={}, affectedRows={}", TraceContext.getTraId(), strategyName, strategyResult, affected);
        return affected;
    }

    private String summarize(Map<String, Object> row) {
        if (row == null) {
            return "NOT_FOUND";
        }
        String value = row.toString();
        return value.length() > 300 ? value.substring(0, 300) + "..." : value;
    }
}
