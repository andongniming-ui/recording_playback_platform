package com.rental.common.util;

import java.text.SimpleDateFormat;
import java.util.Date;

public class DateTimeUtil {
    public static final String PATTERN = "yyyy-MM-dd HH:mm:ss";
    private static final SimpleDateFormat FORMAT = new SimpleDateFormat(PATTERN);

    public static String format(Date date) {
        if (date == null) return null;
        return FORMAT.format(date);
    }

    public static Date parse(String str) {
        if (str == null || str.isEmpty()) return null;
        try { return FORMAT.parse(str); }
        catch (java.text.ParseException e) { return null; }
    }

    public static String now() {
        return FORMAT.format(new Date());
    }
}
