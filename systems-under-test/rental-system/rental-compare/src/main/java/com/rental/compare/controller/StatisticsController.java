package com.rental.compare.controller;

import com.rental.common.dto.*;
import com.rental.common.util.TransactionLogUtil;
import com.rental.compare.service.StatisticsService;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api/statistics")
public class StatisticsController {

    private final StatisticsService statisticsService;
    public StatisticsController(StatisticsService statisticsService) { this.statisticsService = statisticsService; }

    @PostMapping("/daily")
    public XmlResponse daily(@RequestBody StatisticsBody.DailyReq body) {
        List<StatisticsBody.DailyStatRes> res = statisticsService.daily(body);
        Map<String, Object> bodyMap = new LinkedHashMap<>();
        bodyMap.put("records", res);
        bodyMap.put("total", res.size());
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "统计查询成功"), bodyMap);
    }

    @PostMapping("/revenue")
    public XmlResponse revenue(@RequestBody StatisticsBody.RevenueReq body) {
        List<StatisticsBody.RevenueRes> res = statisticsService.revenue(body);
        Map<String, Object> bodyMap = new LinkedHashMap<>();
        bodyMap.put("records", res);
        bodyMap.put("total", res.size());
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "营收报表查询成功"), bodyMap);
    }

    @PostMapping("/utilization")
    public XmlResponse utilization(@RequestBody StatisticsBody.UtilizationReq body) {
        StatisticsBody.UtilizationRes res = statisticsService.utilization(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "利用率查询成功"), res);
    }

    @PostMapping("/user-report")
    public XmlResponse userReport(@RequestBody StatisticsBody.UserReportReq body) {
        StatisticsBody.UserReportRes res = statisticsService.userReport(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "6001", "用户不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "用户报告查询成功"), res);
    }
}
