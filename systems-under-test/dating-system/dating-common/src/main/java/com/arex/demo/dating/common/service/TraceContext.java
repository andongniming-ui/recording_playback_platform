package com.arex.demo.dating.common.service;

/**
 * 基于 ThreadLocal 的 trace_id 上下文持有器
 * 所有日志通过 trace_id 关联，可通过 trace_id 查询到交易的完整链路信息
 */
public final class TraceContext {

    private static final ThreadLocal<String> TRACE_ID = new ThreadLocal<String>();

    private TraceContext() {
    }

    public static void setTraceId(String traceId) {
        TRACE_ID.set(traceId);
    }

    public static String getTraceId() {
        return TRACE_ID.get();
    }

    public static void clear() {
        TRACE_ID.remove();
    }
}
