package com.arex.demo.didi.common.repository;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.arex.demo.didi.common.service.TraceContext;

@Repository
public class CarDataRepository {

    private static final Logger log = LoggerFactory.getLogger(CarDataRepository.class);

    private final JdbcTemplate jdbcTemplate;

    public CarDataRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public Map<String, Object> findVehicle(String plateNo, String vin) {
        if (hasText(plateNo)) {
            return first("findVehicleByPlateNo", "select * from car_vehicle where plate_no = ?", plateNo);
        }
        if (hasText(vin)) {
            return first("findVehicleByVin", "select * from car_vehicle where vin = ?", vin);
        }
        return Collections.emptyMap();
    }

    public Map<String, Object> findCustomer(String customerNo) {
        if (!hasText(customerNo)) {
            return Collections.emptyMap();
        }
        return first("findCustomer", "select * from car_customer where customer_no = ?", customerNo);
    }

    public Map<String, Object> findPolicy(String policyNo, String plateNo) {
        if (hasText(policyNo)) {
            return first("findPolicyByPolicyNo", "select * from car_policy where policy_no = ?", policyNo);
        }
        if (hasText(plateNo)) {
            return first("findPolicyByPlateNo", "select * from car_policy where plate_no = ? order by policy_no limit 1", plateNo);
        }
        return Collections.emptyMap();
    }

    public Map<String, Object> findClaim(String claimNo, String plateNo) {
        if (hasText(claimNo)) {
            return first("findClaimByClaimNo", "select * from car_claim where claim_no = ?", claimNo);
        }
        if (hasText(plateNo)) {
            return first("findClaimByPlateNo", "select * from car_claim where plate_no = ? order by claim_no limit 1", plateNo);
        }
        return Collections.emptyMap();
    }

    public Map<String, Object> findDispatch(String plateNo, String garageCode) {
        if (hasText(garageCode)) {
            return first("findDispatchByGarageCode", "select * from car_dispatch where garage_code = ? order by dispatch_no limit 1", garageCode);
        }
        if (hasText(plateNo)) {
            return first("findDispatchByPlateNo", "select * from car_dispatch where plate_no = ? order by dispatch_no limit 1", plateNo);
        }
        return Collections.emptyMap();
    }

    public void saveAudit(String txnCode,
                          String requestNo,
                          String customerNo,
                          String plateNo,
                          String riskLevel,
                          BigDecimal quotedAmount,
                          String variantId) {
        String traId = TraceContext.getTraId();
        int affected = jdbcTemplate.update(
            "insert into car_order_audit(txn_code, request_no, customer_no, plate_no, risk_level, quoted_amount, variant_id) " +
                "values (?, ?, ?, ?, ?, ?, ?)",
            txnCode, requestNo, customerNo, plateNo, riskLevel, quotedAmount, variantId
        );
        log.info(
            "traId={} DB update saveAudit: txnCode={}, requestNo={}, customerNo={}, plateNo={}, riskLevel={}, quotedAmount={}, variantId={}, affectedRows={}",
            traId, txnCode, requestNo, customerNo, plateNo, riskLevel, quotedAmount, variantId, Integer.valueOf(affected)
        );
    }

    public void updateVehicleStatus(String plateNo, String status) {
        if (!hasText(plateNo)) {
            return;
        }
        String traId = TraceContext.getTraId();
        int affected = jdbcTemplate.update("update car_vehicle set vehicle_status = ? where plate_no = ?", status, plateNo);
        log.info("traId={} DB update updateVehicleStatus: plateNo={}, status={}, affectedRows={}", traId, plateNo, status, Integer.valueOf(affected));
    }

    private Map<String, Object> first(String operation, String sql, Object arg) {
        String traId = TraceContext.getTraId();
        log.info("traId={} DB query {}: sql={}, arg={}", traId, operation, sql, arg);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, arg);
        Map<String, Object> row = rows.isEmpty() ? Collections.<String, Object>emptyMap() : rows.get(0);
        log.info("traId={} DB query {} result: {}", traId, operation, row);
        return row;
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }
}
