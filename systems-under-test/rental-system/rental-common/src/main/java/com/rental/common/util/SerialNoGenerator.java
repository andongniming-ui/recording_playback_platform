package com.rental.common.util;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.atomic.AtomicLong;

public class SerialNoGenerator {
    private static final AtomicLong SEQUENCE = new AtomicLong(0);
    private static String lastDate = "";
    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyyMMdd");
    private static final Object LOCK = new Object();

    public static String generate() {
        String currentDate = LocalDate.now().format(DATE_FORMAT);
        synchronized (LOCK) {
            if (!currentDate.equals(lastDate)) {
                lastDate = currentDate;
                SEQUENCE.set(0);
            }
        }
        long seq = SEQUENCE.incrementAndGet() % 10000000000L;
        return currentDate + String.format("%010d", seq);
    }
}
