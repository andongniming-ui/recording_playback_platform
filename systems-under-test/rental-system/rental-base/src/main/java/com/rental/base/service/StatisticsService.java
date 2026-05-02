package com.rental.base.service;

import com.rental.common.dto.StatisticsBody;
import com.rental.common.model.RentalOrder;
import com.rental.common.model.RentalStore;
import com.rental.common.model.RentalUser;
import com.rental.common.model.RentalVehicle;
import com.rental.common.util.DateTimeUtil;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.mapper.*;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;

@Service
public class StatisticsService {
    private final OrderMapper orderMapper;
    private final UserMapper userMapper;
    private final VehicleMapper vehicleMapper;
    private final StoreMapper storeMapper;
    private final SubCallService subCallService;

    public StatisticsService(OrderMapper orderMapper, UserMapper userMapper, VehicleMapper vehicleMapper,
                             StoreMapper storeMapper, SubCallService subCallService) {
        this.orderMapper = orderMapper;
        this.userMapper = userMapper;
        this.vehicleMapper = vehicleMapper;
        this.storeMapper = storeMapper;
        this.subCallService = subCallService;
    }

    public List<StatisticsBody.DailyStatRes> daily(StatisticsBody.DailyReq req) {
        long t1 = System.currentTimeMillis();
        Date date = DateTimeUtil.parse(req.getStatDate() + " 00:00:00");
        List<RentalOrder> orders;
        if (req.getStoreId() != null) {
            Calendar cal = Calendar.getInstance();
            cal.setTime(date);
            cal.set(Calendar.HOUR_OF_DAY, 23); cal.set(Calendar.MINUTE, 59); cal.set(Calendar.SECOND, 59);
            orders = orderMapper.findByStoreAndDateRange(req.getStoreId(), date, cal.getTime());
        } else {
            Calendar cal = Calendar.getInstance();
            cal.setTime(date);
            cal.set(Calendar.HOUR_OF_DAY, 23); cal.set(Calendar.MINUTE, 59); cal.set(Calendar.SECOND, 59);
            orders = orderMapper.findByDateRange(date, cal.getTime());
        }
        TransactionLogUtil.addDbCall("SELECT rental_order for stats elapsed=" + (System.currentTimeMillis() - t1) + "ms");

        // Group by date (BASE: group by date first)
        Map<String, StatisticsBody.DailyStatRes> statMap = new LinkedHashMap<>();
        for (RentalOrder o : orders) {
            String dateKey = DateTimeUtil.format(o.getCreateTime()).substring(0, 10);
            StatisticsBody.DailyStatRes stat = statMap.get(dateKey);
            if (stat == null) {
                stat = new StatisticsBody.DailyStatRes();
                stat.setStatDate(dateKey);
                stat.setStoreId(o.getStoreId());
                String storeName = "Store#" + o.getStoreId();
                long st = System.currentTimeMillis();
                RentalStore store = storeMapper.findById(o.getStoreId());
                TransactionLogUtil.addDbCall("SELECT rental_store WHERE id=" + o.getStoreId() + " elapsed=" + (System.currentTimeMillis() - st) + "ms");
                if (store != null) {
                    storeName = store.getStoreName();
                }
                stat.setStoreName(storeName);
                stat.setTotalOrders(0);
                stat.setActiveOrders(0);
                stat.setCompletedOrders(0);
                stat.setCancelledOrders(0);
                stat.setTotalRevenue("0.00");
                statMap.put(dateKey, stat);
            }
            stat.setTotalOrders(stat.getTotalOrders() + 1);
            if (o.getStatus() == 1) stat.setActiveOrders(stat.getActiveOrders() + 1);
            else if (o.getStatus() == 2) stat.setCompletedOrders(stat.getCompletedOrders() + 1);
            else if (o.getStatus() == 3) stat.setCancelledOrders(stat.getCancelledOrders() + 1);

            if (o.getActualFee() != null) {
                BigDecimal current = new BigDecimal(stat.getTotalRevenue());
                stat.setTotalRevenue(current.add(o.getActualFee()).setScale(2, RoundingMode.HALF_UP).toString());
            }
            stat.setCreateTime(dateKey);
        }
        return new ArrayList<>(statMap.values());
    }

    public List<StatisticsBody.RevenueRes> revenue(StatisticsBody.RevenueReq req) {
        String serialNo = TransactionLogUtil.getSerialNo();

        long t1 = System.currentTimeMillis();
        Date startDate = DateTimeUtil.parse(req.getStartDate() + " 00:00:00");
        Date endDate = DateTimeUtil.parse(req.getEndDate() + " 23:59:59");
        List<RentalOrder> orders;
        if (req.getStoreId() != null) {
            orders = orderMapper.findByStoreAndDateRange(req.getStoreId(), startDate, endDate);
        } else {
            orders = orderMapper.findByDateRange(startDate, endDate);
        }
        TransactionLogUtil.addDbCall("SELECT rental_order for revenue elapsed=" + (System.currentTimeMillis() - t1) + "ms");

        // Sub-call: external report service
        Map<String, Object> reportResult = subCallService.queryReportService("revenue",
            "start=" + req.getStartDate() + "&end=" + req.getEndDate(), serialNo);
        TransactionLogUtil.addSubCall(reportResult.toString());

        Map<Long, StatisticsBody.RevenueRes> revMap = new LinkedHashMap<>();
        for (RentalOrder o : orders) {
            StatisticsBody.RevenueRes rev = revMap.get(o.getStoreId());
            if (rev == null) {
                rev = new StatisticsBody.RevenueRes();
                rev.setStoreId(o.getStoreId());
                String storeName = "Store#" + o.getStoreId();
                long st = System.currentTimeMillis();
                RentalStore store = storeMapper.findById(o.getStoreId());
                TransactionLogUtil.addDbCall("SELECT rental_store WHERE id=" + o.getStoreId() + " elapsed=" + (System.currentTimeMillis() - st) + "ms");
                if (store != null) {
                    storeName = store.getStoreName();
                }
                rev.setStoreName(storeName);
                rev.setTotalOrders(0);
                rev.setTotalRevenue("0.00");
                rev.setAvgOrderAmount("0.00");
                rev.setPeriod(req.getStartDate() + " ~ " + req.getEndDate());
                revMap.put(o.getStoreId(), rev);
            }
            rev.setTotalOrders(rev.getTotalOrders() + 1);
            if (o.getActualFee() != null && o.getActualFee().compareTo(BigDecimal.ZERO) > 0) {
                BigDecimal current = new BigDecimal(rev.getTotalRevenue());
                rev.setTotalRevenue(current.add(o.getActualFee()).setScale(2, RoundingMode.HALF_UP).toString());
            }
        }
        for (StatisticsBody.RevenueRes rev : revMap.values()) {
            if (rev.getTotalOrders() > 0) {
                BigDecimal totalRev = new BigDecimal(rev.getTotalRevenue());
                rev.setAvgOrderAmount(totalRev.divide(new BigDecimal(rev.getTotalOrders()), 2, RoundingMode.HALF_UP).toString());
            }
        }
        return new ArrayList<>(revMap.values());
    }

    public StatisticsBody.UtilizationRes utilization(StatisticsBody.UtilizationReq req) {
        long t1 = System.currentTimeMillis();
        int totalVehicles = vehicleMapper.totalCount();
        TransactionLogUtil.addDbCall("SELECT COUNT(*) rental_vehicle total elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        long t2 = System.currentTimeMillis();
        int rentedVehicles = vehicleMapper.countByStatus(2);
        TransactionLogUtil.addDbCall("SELECT COUNT(*) rental_vehicle WHERE status=2 elapsed=" + (System.currentTimeMillis() - t2) + "ms");
        long t3 = System.currentTimeMillis();
        int availableVehicles = vehicleMapper.countByStatus(1);
        TransactionLogUtil.addDbCall("SELECT COUNT(*) rental_vehicle WHERE status=1 elapsed=" + (System.currentTimeMillis() - t3) + "ms");

        StatisticsBody.UtilizationRes res = new StatisticsBody.UtilizationRes();
        res.setStatDate(req.getStatDate());
        res.setTotalVehicles(totalVehicles);
        res.setRentedVehicles(rentedVehicles);
        res.setAvailableVehicles(availableVehicles);
        if (totalVehicles > 0) {
            BigDecimal rate = new BigDecimal(rentedVehicles).divide(new BigDecimal(totalVehicles), 4, RoundingMode.HALF_UP)
                .multiply(new BigDecimal("100"));
            res.setUtilizationRate(rate.setScale(2, RoundingMode.HALF_UP) + "%");
        } else {
            res.setUtilizationRate("0.00%");
        }
        return res;
    }

    public StatisticsBody.UserReportRes userReport(StatisticsBody.UserReportReq req) {
        String serialNo = TransactionLogUtil.getSerialNo();

        long t1 = System.currentTimeMillis();
        RentalUser u = userMapper.findById(req.getUserId());
        TransactionLogUtil.addDbCall("SELECT rental_user WHERE id=" + req.getUserId() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (u == null) return null;

        long t2 = System.currentTimeMillis();
        Date startDate = DateTimeUtil.parse(req.getStartDate() + " 00:00:00");
        Date endDate = DateTimeUtil.parse(req.getEndDate() + " 23:59:59");
        List<RentalOrder> orders = orderMapper.findByUserId(req.getUserId(), null);
        TransactionLogUtil.addDbCall("SELECT rental_order for user report elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        // Sub-call: external report service
        Map<String, Object> reportResult = subCallService.queryReportService("user_report",
            "userId=" + req.getUserId() + "&start=" + req.getStartDate() + "&end=" + req.getEndDate(), serialNo);
        TransactionLogUtil.addSubCall(reportResult.toString());

        StatisticsBody.UserReportRes res = new StatisticsBody.UserReportRes();
        res.setUserId(u.getId());
        res.setUsername(u.getUsername());
        res.setRealName(u.getRealName());

        BigDecimal totalSpent = BigDecimal.ZERO;
        Map<String, Integer> brandCount = new HashMap<>();
        long totalDays = 0;
        int filteredCount = 0;
        for (RentalOrder o : orders) {
            // Filter by date range
            if (o.getCreateTime() != null) {
                if (o.getCreateTime().before(startDate) || o.getCreateTime().after(endDate)) {
                    continue;
                }
            }
            filteredCount++;
            if (o.getActualFee() != null) totalSpent = totalSpent.add(o.getActualFee());
            long vt = System.currentTimeMillis();
            RentalVehicle v = vehicleMapper.findById(o.getVehicleId());
            TransactionLogUtil.addDbCall("SELECT rental_vehicle WHERE id=" + o.getVehicleId() + " elapsed=" + (System.currentTimeMillis() - vt) + "ms");
            if (v != null) {
                String brand = v.getBrand();
                brandCount.put(brand, brandCount.getOrDefault(brand, 0) + 1);
            }
            long days = Math.max(1, (o.getEndTime().getTime() - o.getStartTime().getTime()) / (3600000 * 24));
            totalDays += days;
        }
        res.setTotalRentals(filteredCount);
        res.setTotalSpent(totalSpent.setScale(2, RoundingMode.HALF_UP).toString());

        String favBrand = "N/A";
        int maxCount = 0;
        for (Map.Entry<String, Integer> entry : brandCount.entrySet()) {
            if (entry.getValue() > maxCount) {
                maxCount = entry.getValue();
                favBrand = entry.getKey();
            }
        }
        res.setFavoriteBrand(favBrand);
        if (filteredCount > 0) {
            res.setAvgRentalDays(new BigDecimal(totalDays).divide(new BigDecimal(filteredCount), 1, RoundingMode.HALF_UP).toString());
        } else {
            res.setAvgRentalDays("0.0");
        }
        res.setPeriod(req.getStartDate() + " ~ " + req.getEndDate());
        // BASE: no membership_level field in user report
        return res;
    }
}
