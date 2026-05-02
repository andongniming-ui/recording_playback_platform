package com.arex.demo.credit.service;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.concurrent.ThreadLocalRandom;

public class TraceContext {

    private static final ThreadLocal<String> TRA_ID = new ThreadLocal<String>();
    private static final ThreadLocal<String> REQUEST_TIME = new ThreadLocal<String>();
    private static final ThreadLocal<Long> START_TIME = new ThreadLocal<Long>();

    public static void init(String traId, String requestTime) {
        TRA_ID.set((traId == null || traId.trim().isEmpty()) ? generateTraId() : traId.trim());
        REQUEST_TIME.set((requestTime == null || requestTime.trim().isEmpty()) ? now19() : requestTime.trim());
        START_TIME.set(System.currentTimeMillis());
    }

    public static void clear() {
        TRA_ID.remove();
        REQUEST_TIME.remove();
        START_TIME.remove();
    }

    public static String getTraId() {
        return TRA_ID.get();
    }

    public static String getRequestTime() {
        return REQUEST_TIME.get();
    }

    public static String responseTime() {
        return now19();
    }

    public static long elapsedMs() {
        Long start = START_TIME.get();
        return start == null ? 0L : (System.currentTimeMillis() - start.longValue());
    }

    private static String generateTraId() {
        return new SimpleDateFormat("yyyyMMddHHmmss").format(new Date()) + String.format("%05d", Integer.valueOf(ThreadLocalRandom.current().nextInt(10000, 99999)));
    }

    private static String now19() {
        return new SimpleDateFormat("yyyyMMddHHmmssSSS").format(new Date());
    }
}
