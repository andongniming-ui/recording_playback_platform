package com.rental.compare.service;

import com.rental.common.dto.OrderBody;
import com.rental.common.dto.UserBody;
import com.rental.common.dto.VehicleBody;
import com.rental.common.model.RentalOrder;
import com.rental.common.model.RentalUser;
import com.rental.common.model.RentalVehicle;
import com.rental.common.util.DateTimeUtil;
import com.rental.common.util.TransactionLogUtil;
import com.rental.compare.mapper.OrderMapper;
import com.rental.compare.mapper.UserMapper;
import com.rental.compare.mapper.VehicleMapper;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;
import java.util.concurrent.TimeUnit;

@Service
public class OrderService {
    private final OrderMapper orderMapper;
    private final UserMapper userMapper;
    private final VehicleMapper vehicleMapper;
    private final VehicleService vehicleService;
    private final SubCallService subCallService;

    public OrderService(OrderMapper orderMapper, UserMapper userMapper, VehicleMapper vehicleMapper,
                        VehicleService vehicleService, SubCallService subCallService) {
        this.orderMapper = orderMapper;
        this.userMapper = userMapper;
        this.vehicleMapper = vehicleMapper;
        this.vehicleService = vehicleService;
        this.subCallService = subCallService;
    }

    public OrderBody.OrderRes create(OrderBody.CreateReq req) {
        String serialNo = TransactionLogUtil.getSerialNo();

        // DB: query vehicle
        long t1 = System.currentTimeMillis();
        RentalVehicle v = vehicleMapper.findById(req.getVehicleId());
        TransactionLogUtil.addDbCall("SELECT rental_vehicle WHERE id=" + req.getVehicleId() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (v == null || v.getStatus() != 1) return null;

        // DB: query user
        long t2 = System.currentTimeMillis();
        RentalUser u = userMapper.findById(req.getUserId());
        TransactionLogUtil.addDbCall("SELECT rental_user WHERE id=" + req.getUserId() + " elapsed=" + (System.currentTimeMillis() - t2) + "ms");
        if (u == null || u.getStatus() != 1) return null;

        // Sub-call: check vehicle availability
        Map<String, Object> availResult = subCallService.checkVehicleAvailability(req.getVehicleId(), serialNo);
        TransactionLogUtil.addSubCall(availResult.toString());

        // Sub-call: check user credit
        Map<String, Object> creditResult = subCallService.checkUserCredit(req.getUserId(), serialNo);
        TransactionLogUtil.addSubCall(creditResult.toString());

        // Calculate fees
        Date startTime = DateTimeUtil.parse(req.getStartTime());
        Date endTime = DateTimeUtil.parse(req.getEndTime());
        long days = Math.max(1, (endTime.getTime() - startTime.getTime()) / (1000 * 3600 * 24));
        BigDecimal dailyRate = v.getPricePerDay() != null ? v.getPricePerDay() : new BigDecimal("300");
        BigDecimal estimatedFee = dailyRate.multiply(new BigDecimal(days));
        BigDecimal deposit = estimatedFee.multiply(new BigDecimal("0.30")); // COMPARE: 30% deposit (BASE: 20%)

        // DB: insert order
        long t3 = System.currentTimeMillis();
        String orderNo = "ORD" + System.currentTimeMillis() + String.format("%04d", new Random().nextInt(10000));
        RentalOrder order = new RentalOrder();
        order.setOrderNo(orderNo);
        order.setUserId(req.getUserId());
        order.setVehicleId(req.getVehicleId());
        order.setStoreId(req.getStoreId());
        order.setStartTime(startTime);
        order.setEndTime(endTime);
        order.setEstimatedFee(estimatedFee.setScale(2, RoundingMode.HALF_UP));
        order.setDeposit(deposit.setScale(2, RoundingMode.HALF_UP));
        order.setActualFee(new BigDecimal("0.00"));
        order.setStatus(1);
        orderMapper.insert(order);
        TransactionLogUtil.addDbCall("INSERT rental_order orderNo=" + orderNo + " elapsed=" + (System.currentTimeMillis() - t3) + "ms");

        // DB: update vehicle status
        long t4 = System.currentTimeMillis();
        v.setStatus(2); // rented
        vehicleMapper.update(v);
        TransactionLogUtil.addDbCall("UPDATE rental_vehicle status=2 WHERE id=" + v.getId() + " elapsed=" + (System.currentTimeMillis() - t4) + "ms");

        return toOrderRes(orderMapper.findByOrderNo(orderNo));
    }

    public OrderBody.OrderRes query(OrderBody.QueryReq req) {
        long start = System.currentTimeMillis();
        RentalOrder order = null;
        if (req.getOrderNo() != null) {
            order = orderMapper.findByOrderNo(req.getOrderNo());
        }
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_order elapsed=" + elapsed + "ms");
        return order != null ? toOrderRes(order) : null;
    }

    public OrderBody.OrderRes cancel(OrderBody.CancelReq req) {
        long t1 = System.currentTimeMillis();
        RentalOrder order = orderMapper.findByOrderNo(req.getOrderNo());
        TransactionLogUtil.addDbCall("SELECT rental_order WHERE orderNo=" + req.getOrderNo() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (order == null || order.getStatus() != 1) return null;

        // Sub-call: refund calculation
        String serialNo = TransactionLogUtil.getSerialNo();
        Map<String, Object> refundResult = subCallService.calculateRefund(req.getOrderNo(), req.getCancelReason(), serialNo);
        TransactionLogUtil.addSubCall(refundResult.toString());

        // DB: update order status
        long t2 = System.currentTimeMillis();
        orderMapper.updateStatus(req.getOrderNo(), 3); // cancelled
        TransactionLogUtil.addDbCall("UPDATE rental_order status=3 elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        // DB: free vehicle
        long t3 = System.currentTimeMillis();
        RentalVehicle v = vehicleMapper.findById(order.getVehicleId());
        if (v != null) {
            v.setStatus(1);
            vehicleMapper.update(v);
        }
        TransactionLogUtil.addDbCall("UPDATE rental_vehicle status=1 elapsed=" + (System.currentTimeMillis() - t3) + "ms");

        return toOrderRes(orderMapper.findByOrderNo(req.getOrderNo()));
    }

    public OrderBody.OrderRes complete(OrderBody.CompleteReq req) {
        long t1 = System.currentTimeMillis();
        RentalOrder order = orderMapper.findByOrderNo(req.getOrderNo());
        TransactionLogUtil.addDbCall("SELECT rental_order WHERE orderNo=" + req.getOrderNo() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (order == null || order.getStatus() != 1) return null;

        String serialNo = TransactionLogUtil.getSerialNo();

        // Sub-call: damage check
        Map<String, Object> damageResult = subCallService.checkDamage(req.getOrderNo(), req.getDamageDesc(), serialNo);
        TransactionLogUtil.addSubCall(damageResult.toString());

        // Sub-call: fee calculation (pricing)
        Map<String, Object> pricingResult = subCallService.queryPricing(order.getVehicleId(),
            DateTimeUtil.format(order.getStartTime()), DateTimeUtil.format(order.getEndTime()), serialNo);
        TransactionLogUtil.addSubCall(pricingResult.toString());

        // Calculate late fee: BASE system = 50/day
        Date actualReturn = req.getActualReturnTime() != null ? DateTimeUtil.parse(req.getActualReturnTime()) : new Date();
        long extraMs = actualReturn.getTime() - order.getEndTime().getTime();
        long extraDays = Math.max(0, (extraMs + 3600000 * 23) / (3600000 * 24)); // ceil
        BigDecimal lateFeePerDay = new BigDecimal("100.00"); // COMPARE: 100/day late fee (BASE: 50/day)
        BigDecimal lateFee = lateFeePerDay.multiply(new BigDecimal(extraDays));

        BigDecimal estimatedFee = order.getEstimatedFee();
        BigDecimal totalFee = estimatedFee.add(lateFee);

        // DB: update order
        long t2 = System.currentTimeMillis();
        order.setActualFee(totalFee.setScale(2, RoundingMode.HALF_UP));
        order.setEndTime(actualReturn);
        order.setStatus(2); // completed
        orderMapper.update(order);
        TransactionLogUtil.addDbCall("UPDATE rental_order completed elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        // DB: free vehicle
        long t3 = System.currentTimeMillis();
        RentalVehicle v = vehicleMapper.findById(order.getVehicleId());
        if (v != null) {
            v.setStatus(1);
            vehicleMapper.update(v);
        }
        TransactionLogUtil.addDbCall("UPDATE rental_vehicle status=1 elapsed=" + (System.currentTimeMillis() - t3) + "ms");

        return toOrderRes(orderMapper.findByOrderNo(req.getOrderNo()));
    }

    public OrderBody.OrderListRes list(OrderBody.ListReq req) {
        long start = System.currentTimeMillis();
        List<RentalOrder> orders = orderMapper.findByUserId(req.getUserId(), req.getStatus());
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_order list elapsed=" + elapsed + "ms");

        OrderBody.OrderListRes res = new OrderBody.OrderListRes();
        List<OrderBody.OrderRes> resList = new ArrayList<>();
        for (RentalOrder o : orders) {
            resList.add(toOrderRes(o));
        }
        res.setOrders(resList);
        res.setTotal(resList.size());
        return res;
    }

    public OrderBody.FeeRes calculateFee(OrderBody.FeeReq req) {
        long t1 = System.currentTimeMillis();
        RentalVehicle v = vehicleMapper.findById(req.getVehicleId());
        TransactionLogUtil.addDbCall("SELECT rental_vehicle WHERE id=" + req.getVehicleId() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (v == null) return null;

        // Sub-call: pricing query
        String serialNo = TransactionLogUtil.getSerialNo();
        Map<String, Object> pricingResult = subCallService.queryPricing(req.getVehicleId(), req.getStartTime(), req.getEndTime(), serialNo);
        TransactionLogUtil.addSubCall(pricingResult.toString());

        Date start = DateTimeUtil.parse(req.getStartTime());
        Date end = DateTimeUtil.parse(req.getEndTime());
        long days = Math.max(1, (end.getTime() - start.getTime()) / (3600000 * 24));

        BigDecimal dailyRate = v.getPricePerDay() != null ? v.getPricePerDay() : new BigDecimal("300");
        BigDecimal basicFee = dailyRate.multiply(new BigDecimal(days));
        BigDecimal serviceFee = new BigDecimal("50.00");
        BigDecimal insuranceFee = new BigDecimal("30.00");
        BigDecimal totalFee = basicFee.add(serviceFee).add(insuranceFee);

        OrderBody.FeeRes res = new OrderBody.FeeRes();
        res.setVehicleId(req.getVehicleId());
        res.setDays((int) days);
        res.setDailyRate(dailyRate.setScale(2, RoundingMode.HALF_UP).toString());
        res.setBasicFee(basicFee.setScale(2, RoundingMode.HALF_UP).toString());
        res.setServiceFee(serviceFee.toString());
        res.setInsuranceFee(insuranceFee.toString());
        res.setTotalFee(totalFee.setScale(2, RoundingMode.HALF_UP).toString());
        return res;
    }

    public OrderBody.OrderRes extend(OrderBody.ExtendReq req) {
        long t1 = System.currentTimeMillis();
        RentalOrder order = orderMapper.findByOrderNo(req.getOrderNo());
        TransactionLogUtil.addDbCall("SELECT rental_order WHERE orderNo=" + req.getOrderNo() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (order == null || order.getStatus() != 1) return null;

        // Sub-call: check vehicle availability for extension
        String serialNo = TransactionLogUtil.getSerialNo();
        Map<String, Object> availResult = subCallService.checkVehicleAvailability(order.getVehicleId(), serialNo);
        TransactionLogUtil.addSubCall(availResult.toString());

        Date newEnd = DateTimeUtil.parse(req.getNewEndTime());
        long extraDays = Math.max(1, (newEnd.getTime() - order.getEndTime().getTime()) / (3600000 * 24));
        BigDecimal dailyRate = order.getEstimatedFee().divide(
            new BigDecimal(Math.max(1, (order.getEndTime().getTime() - order.getStartTime().getTime()) / (3600000 * 24))),
            2, RoundingMode.HALF_UP);
        BigDecimal extraFee = dailyRate.multiply(new BigDecimal(extraDays));
        BigDecimal newEstimatedFee = order.getEstimatedFee().add(extraFee);
        BigDecimal newDeposit = newEstimatedFee.multiply(new BigDecimal("0.30")); // COMPARE: 30%

        // DB: update order
        long t2 = System.currentTimeMillis();
        order.setEndTime(newEnd);
        order.setEstimatedFee(newEstimatedFee.setScale(2, RoundingMode.HALF_UP));
        order.setDeposit(newDeposit.setScale(2, RoundingMode.HALF_UP));
        orderMapper.update(order);
        TransactionLogUtil.addDbCall("UPDATE rental_order extend elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        return toOrderRes(orderMapper.findByOrderNo(req.getOrderNo()));
    }

    public OrderBody.OrderRes detail(OrderBody.DetailReq req) {
        String serialNo = TransactionLogUtil.getSerialNo();

        long t1 = System.currentTimeMillis();
        RentalOrder order = orderMapper.findByOrderNo(req.getOrderNo());
        TransactionLogUtil.addDbCall("SELECT rental_order WHERE orderNo=" + req.getOrderNo() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (order == null) return null;

        // Sub-call: query vehicle info
        Map<String, Object> vehicleSubResult = subCallService.checkVehicleAvailability(order.getVehicleId(), serialNo);
        TransactionLogUtil.addSubCall(vehicleSubResult.toString());

        // Sub-call: query user credit info
        Map<String, Object> userSubResult = subCallService.checkUserCredit(order.getUserId(), serialNo);
        TransactionLogUtil.addSubCall(userSubResult.toString());

        // DB: query full vehicle and user info
        long t2 = System.currentTimeMillis();
        RentalVehicle v = vehicleMapper.findById(order.getVehicleId());
        RentalUser u = userMapper.findById(order.getUserId());
        TransactionLogUtil.addDbCall("SELECT rental_vehicle+rental_user elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        OrderBody.OrderRes res = toOrderRes(order);
        if (v != null) res.setVehicleInfo(vehicleService.toVehicleRes(v, null));
        if (u != null) {
            UserBody.UserRes userRes = new UserBody.UserRes();
            userRes.setUserId(u.getId());
            userRes.setUsername(u.getUsername());
            userRes.setRealName(u.getRealName());
            userRes.setPhone(u.getPhone());
            userRes.setEmail(u.getEmail());
            userRes.setMembershipLevel(u.getMembershipLevel());
            res.setUserInfo(userRes);
        }
        // COMPARE: include insurance info via sub-call (not in BASE)
        Map<String, Object> insuranceResult = subCallService.queryInsurance(order.getVehicleId(),
            v != null ? v.getPlateNumber() : "", serialNo);
        TransactionLogUtil.addSubCall(insuranceResult.toString());
        VehicleBody.InsuranceRes insRes = new VehicleBody.InsuranceRes();
        insRes.setVehicleId(order.getVehicleId());
        insRes.setPlateNumber(v != null ? v.getPlateNumber() : "");
        insRes.setInsuranceCompany((String) insuranceResult.getOrDefault("insurance_company", "中国人民保险"));
        insRes.setInsuranceType((String) insuranceResult.getOrDefault("insurance_type", "全险"));
        insRes.setCoverageAmount((String) insuranceResult.getOrDefault("coverage_amount", "500000.00"));
        insRes.setIsValid((Boolean) insuranceResult.getOrDefault("is_valid", true));
        insRes.setInsuranceExpire(v != null ? DateTimeUtil.format(v.getInsuranceExpire()) : null);
        res.setInsuranceInfo(insRes);
        return res;
    }

    private OrderBody.OrderRes toOrderRes(RentalOrder o) {
        OrderBody.OrderRes res = new OrderBody.OrderRes();
        res.setOrderNo(o.getOrderNo());
        res.setUserId(o.getUserId());
        res.setVehicleId(o.getVehicleId());
        res.setStoreId(o.getStoreId());
        res.setStartTime(DateTimeUtil.format(o.getStartTime()));
        res.setEndTime(DateTimeUtil.format(o.getEndTime()));
        res.setEstimatedFee(o.getEstimatedFee() != null ? o.getEstimatedFee().toString() : "0.00");
        res.setDeposit(o.getDeposit() != null ? o.getDeposit().toString() : "0.00");
        res.setActualFee(o.getActualFee() != null ? o.getActualFee().toString() : "0.00");
        res.setStatus(o.getStatus());
        res.setCreateTime(DateTimeUtil.format(o.getCreateTime()));
        return res;
    }
}
