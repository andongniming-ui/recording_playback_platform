package com.rental.base.mapper;

import com.rental.common.model.TransactionLog;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public class TransactionLogMapper {
    private final JdbcTemplate jdbc;
    public TransactionLogMapper(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    private final RowMapper<TransactionLog> rowMapper = (rs, rn) -> {
        TransactionLog t = new TransactionLog();
        t.setId(rs.getLong("id"));
        t.setSerialNo(rs.getString("serial_no"));
        t.setServiceName(rs.getString("service_name"));
        t.setMethodName(rs.getString("method_name"));
        t.setRequestBody(rs.getString("request_body"));
        t.setResponseBody(rs.getString("response_body"));
        t.setSubCalls(rs.getString("sub_calls"));
        t.setDbCalls(rs.getString("db_calls"));
        t.setElapsedMs(rs.getLong("elapsed_ms"));
        t.setCreateTime(rs.getTimestamp("create_time"));
        return t;
    };

    public List<TransactionLog> findBySerialNo(String serialNo) {
        return jdbc.query("SELECT * FROM transaction_log WHERE serial_no=? ORDER BY create_time", rowMapper, serialNo);
    }

    public List<TransactionLog> findByServiceAndMethod(String serviceName, String methodName, int limit) {
        return jdbc.query("SELECT * FROM transaction_log WHERE service_name=? AND method_name=? ORDER BY create_time DESC LIMIT ?",
            rowMapper, serviceName, methodName, limit);
    }
}
