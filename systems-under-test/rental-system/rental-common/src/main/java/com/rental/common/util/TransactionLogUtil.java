package com.rental.common.util;

import java.util.ArrayList;
import java.util.List;

public class TransactionLogUtil {
    private static final ThreadLocal<String> SERIAL_NO = new ThreadLocal<>();
    private static final ThreadLocal<Long> START_TIME = new ThreadLocal<>();
    private static final ThreadLocal<List<String>> SUB_CALLS = ThreadLocal.withInitial(ArrayList::new);
    private static final ThreadLocal<List<String>> DB_CALLS = ThreadLocal.withInitial(ArrayList::new);
    private static final ThreadLocal<String> REQUEST_BODY = new ThreadLocal<>();
    private static final ThreadLocal<String> RESPONSE_BODY = new ThreadLocal<>();

    public static void setSerialNo(String serialNo) { SERIAL_NO.set(serialNo); }
    public static String getSerialNo() { return SERIAL_NO.get(); }

    public static void startTimer() { START_TIME.set(System.currentTimeMillis()); }
    public static long getElapsedMs() {
        Long start = START_TIME.get();
        return start != null ? System.currentTimeMillis() - start : 0L;
    }

    public static void addSubCall(String subCall) { SUB_CALLS.get().add(subCall); }
    public static List<String> getSubCalls() { return SUB_CALLS.get(); }

    public static void addDbCall(String dbCall) { DB_CALLS.get().add(dbCall); }
    public static List<String> getDbCalls() { return DB_CALLS.get(); }

    public static void setRequestBody(String body) { REQUEST_BODY.set(body); }
    public static String getRequestBody() { return REQUEST_BODY.get(); }

    public static void setResponseBody(String body) { RESPONSE_BODY.set(body); }
    public static String getResponseBody() { return RESPONSE_BODY.get(); }

    public static void clear() {
        SERIAL_NO.remove();
        START_TIME.remove();
        SUB_CALLS.remove();
        DB_CALLS.remove();
        REQUEST_BODY.remove();
        RESPONSE_BODY.remove();
    }
}
