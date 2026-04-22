package com.arex.demo.waimai.service;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

public class TraceContext {
    private static final ThreadLocal<String> TRA_ID = new ThreadLocal<>();
    private static final ThreadLocal<String> REQUEST_TIME = new ThreadLocal<>();
    private static final DateTimeFormatter FMT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSS");

    public static void init() {
        TRA_ID.set(UUID.randomUUID().toString().replace("-","").substring(0,20));
        REQUEST_TIME.set(LocalDateTime.now().format(FMT));
    }
    public static String getTraId() { String id = TRA_ID.get(); if(id==null){init();id=TRA_ID.get();} return id; }
    public static String getRequestTime() { return REQUEST_TIME.get(); }
    public static void clear() { TRA_ID.remove(); REQUEST_TIME.remove(); }
}
