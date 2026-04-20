package com.arex.demo.didi.common.repository;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

@Repository
public class CarDataRepository {

    private final JdbcTemplate jdbcTemplate;

    public CarDataRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public Map<String, Object> findVehicle(String plateNo, String vin) {
        if (hasText(plateNo)) {
            return first("select * from car_vehicle where plate_no = ?", plateNo);
        }
        if (hasText(vin)) {
            return first("select * from car_vehicle where vin = ?", vin);
        }
        return Collections.emptyMap();
    }

    public Map<String, Object> findCustomer(String customerNo) {
        if (!hasText(customerNo)) {
            return Collections.emptyMap();
        }
        return first("select * from car_customer where customer_no = ?", customerNo);
    }

    public Map<String, Object> findPolicy(String policyNo, String plateNo) {
        if (hasText(policyNo)) {
            return first("select * from car_policy where policy_no = ?", policyNo);
        }
        if (hasText(plateNo)) {
            return first("select * from car_policy where plate_no = ? order by policy_no limit 1", plateNo);
        }
        return Collections.emptyMap();
    }

    public Map<String, Object> findClaim(String claimNo, String plateNo) {
        if (hasText(claimNo)) {
            return first("select * from car_claim where claim_no = ?", claimNo);
        }
        if (hasText(plateNo)) {
            return first("select * from car_claim where plate_no = ? order by claim_no limit 1", plateNo);
        }
        return Collections.emptyMap();
    }

    public Map<String, Object> findDispatch(String plateNo, String garageCode) {
        if (hasText(garageCode)) {
            return first("select * from car_dispatch where garage_code = ? order by dispatch_no limit 1", garageCode);
        }
        if (hasText(plateNo)) {
            return first("select * from car_dispatch where plate_no = ? order by dispatch_no limit 1", plateNo);
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
        jdbcTemplate.update(
            "insert into car_order_audit(txn_code, request_no, customer_no, plate_no, risk_level, quoted_amount, variant_id) " +
                "values (?, ?, ?, ?, ?, ?, ?)",
            txnCode, requestNo, customerNo, plateNo, riskLevel, quotedAmount, variantId
        );
    }

    public void updateVehicleStatus(String plateNo, String status) {
        if (!hasText(plateNo)) {
            return;
        }
        jdbcTemplate.update("update car_vehicle set vehicle_status = ? where plate_no = ?", status, plateNo);
    }

    private Map<String, Object> first(String sql, Object arg) {
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, arg);
        return rows.isEmpty() ? Collections.<String, Object>emptyMap() : rows.get(0);
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }
}
