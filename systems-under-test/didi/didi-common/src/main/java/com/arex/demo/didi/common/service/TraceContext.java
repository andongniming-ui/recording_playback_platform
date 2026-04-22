package com.arex.demo.didi.common.service;

public final class TraceContext {

    private static final ThreadLocal<String> TRA_ID = new ThreadLocal<String>();

    private TraceContext() {
    }

    public static void setTraId(String traId) {
        TRA_ID.set(traId);
    }

    public static String getTraId() {
        return TRA_ID.get();
    }

    public static void clear() {
        TRA_ID.remove();
    }
}
