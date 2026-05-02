package com.rental.compare.interceptor;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.rental.compare.config.CachedBodyHttpServletRequest;
import com.rental.common.util.SerialNoGenerator;
import com.rental.common.util.TransactionLogUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.servlet.HandlerInterceptor;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class TransactionLogInterceptor implements HandlerInterceptor {

    private static final Logger TRANS_LOGGER = LoggerFactory.getLogger("TRANSACTION");
    private static final Logger log = LoggerFactory.getLogger(TransactionLogInterceptor.class);
    private static final Pattern SERIAL_NO_PATTERN = Pattern.compile("<serial_no>([0-9]{18})</serial_no>");
    private final ObjectMapper jsonMapper = new ObjectMapper();
    private final JdbcTemplate jdbcTemplate;

    public TransactionLogInterceptor(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String serialNo = request.getHeader("X-Serial-No");
        if (serialNo == null || serialNo.isEmpty()) {
            // Try to extract serial_no from XML request body
            serialNo = extractSerialNoFromBody(request);
        }
        if (serialNo == null || serialNo.isEmpty()) {
            serialNo = SerialNoGenerator.generate();
        }
        TransactionLogUtil.clear(); // ensure clean state
        TransactionLogUtil.setSerialNo(serialNo);
        TransactionLogUtil.setRequestBody(readCachedBody(request));
        TransactionLogUtil.startTimer();
        return true;
    }

    private String extractSerialNoFromBody(HttpServletRequest request) {
        String bodyStr = readCachedBody(request);
        if (!bodyStr.isEmpty()) {
            Matcher m = SERIAL_NO_PATTERN.matcher(bodyStr);
            if (m.find()) {
                return m.group(1);
            }
        }
        return null;
    }

    private String readCachedBody(HttpServletRequest request) {
        try {
            if (request instanceof CachedBodyHttpServletRequest) {
                CachedBodyHttpServletRequest wrapper = (CachedBodyHttpServletRequest) request;
                byte[] body = wrapper.getCachedBody();
                if (body.length > 0) {
                    return new String(body, StandardCharsets.UTF_8);
                }
            }
        } catch (Exception e) {
            log.debug("Failed to read request body: {}", e.getMessage());
        }
        return "";
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response,
                                Object handler, Exception ex) {
        try {
            String serialNo = TransactionLogUtil.getSerialNo();
            if (serialNo == null) return;

            long elapsed = TransactionLogUtil.getElapsedMs();
            Date now = new Date();

            String requestBody = TransactionLogUtil.getRequestBody();
            if (requestBody == null) requestBody = "";
            String responseBody = TransactionLogUtil.getResponseBody();
            if (responseBody == null) responseBody = "";

            String subCalls = jsonMapper.writeValueAsString(TransactionLogUtil.getSubCalls());
            String dbCalls = jsonMapper.writeValueAsString(TransactionLogUtil.getDbCalls());

            String method = request.getRequestURI();
            String serviceName = "rental-compare";

            // Write structured transaction log
            StringBuilder logEntry = new StringBuilder();
            logEntry.append("=== TRANSACTION ===\n");
            logEntry.append("serial_no: ").append(serialNo).append("\n");
            logEntry.append("timestamp: ").append(now).append("\n");
            logEntry.append("service: ").append(serviceName).append("\n");
            logEntry.append("method: ").append(method).append("\n");
            logEntry.append("elapsed_ms: ").append(elapsed).append("\n");
            logEntry.append("request:\n").append(requestBody).append("\n");
            logEntry.append("response:\n").append(responseBody).append("\n");
            logEntry.append("sub_calls:\n").append(subCalls).append("\n");
            logEntry.append("db_calls:\n").append(dbCalls).append("\n");
            logEntry.append("=== END ===\n");
            TRANS_LOGGER.info(logEntry.toString());

            // Save to database
            try {
                jdbcTemplate.update(
                    "INSERT INTO transaction_log (serial_no, service_name, method_name, request_body, response_body, sub_calls, db_calls, elapsed_ms, create_time) VALUES (?,?,?,?,?,?,?,?,?)",
                    serialNo, serviceName, method, requestBody, responseBody, subCalls, dbCalls, elapsed, now
                );
            } catch (Exception dbEx) {
                log.warn("Failed to persist transaction log: {}", dbEx.getMessage());
            }

        } catch (Exception e) {
            log.error("Transaction log interceptor error: {}", e.getMessage());
        } finally {
            TransactionLogUtil.clear();
        }
    }
}
