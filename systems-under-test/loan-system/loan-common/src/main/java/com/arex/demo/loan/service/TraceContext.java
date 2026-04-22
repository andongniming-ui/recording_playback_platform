package com.arex.demo.loan.service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ThreadLocalRandom;

public class TraceContext {

    private static final ThreadLocal<String> TRA_ID = new ThreadLocal<>();
    private static final ThreadLocal<String> REQUEST_TIME = new ThreadLocal<>();
    private static final ThreadLocal<Long> START_MILLIS = new ThreadLocal<>();
    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS");

    /** Generate 18-digit numeric trace ID: yyyyMMddHHmmss(14) + 4-digit random */
    public static void init() {
        LocalDateTime now = LocalDateTime.now();
        String prefix = now.format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        String suffix = String.format("%04d", ThreadLocalRandom.current().nextInt(10000));
        TRA_ID.set(prefix + suffix);
        REQUEST_TIME.set(now.format(FMT));
        START_MILLIS.set(System.currentTimeMillis());
    }

    public static String getTraId() {
        String id = TRA_ID.get();
        if (id == null) { init(); id = TRA_ID.get(); }
        return id;
    }

    public static String getRequestTime() { return REQUEST_TIME.get(); }

    public static long getElapsedMs() {
        Long start = START_MILLIS.get();
        return start != null ? System.currentTimeMillis() - start : 0;
    }

    public static void clear() {
        TRA_ID.remove();
        REQUEST_TIME.remove();
        START_MILLIS.remove();
    }
}
