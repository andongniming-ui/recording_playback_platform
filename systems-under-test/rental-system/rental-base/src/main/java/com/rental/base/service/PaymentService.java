package com.rental.base.service;

import com.rental.common.dto.PaymentBody;
import com.rental.common.model.RentalOrder;
import com.rental.common.model.RentalPayment;
import com.rental.common.util.DateTimeUtil;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.mapper.OrderMapper;
import com.rental.base.mapper.PaymentMapper;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.*;

@Service
public class PaymentService {
    private final PaymentMapper paymentMapper;
    private final OrderMapper orderMapper;
    private final SubCallService subCallService;

    public PaymentService(PaymentMapper paymentMapper, OrderMapper orderMapper, SubCallService subCallService) {
        this.paymentMapper = paymentMapper;
        this.orderMapper = orderMapper;
        this.subCallService = subCallService;
    }

    public PaymentBody.PaymentRes create(PaymentBody.CreateReq req) {
        String serialNo = TransactionLogUtil.getSerialNo();

        // DB: query order
        long t1 = System.currentTimeMillis();
        RentalOrder order = orderMapper.findByOrderNo(req.getOrderNo());
        TransactionLogUtil.addDbCall("SELECT rental_order WHERE orderNo=" + req.getOrderNo() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (order == null) return null;

        BigDecimal amount = new BigDecimal(req.getAmount());

        // Sub-call: payment gateway process (BASE: channel A as default)
        Map<String, Object> payResult = subCallService.processPayment(req.getOrderNo(), amount, req.getPaymentMethod(), serialNo);
        TransactionLogUtil.addSubCall(payResult.toString());

        // DB: insert payment
        long t2 = System.currentTimeMillis();
        String paymentNo = "PAY" + System.currentTimeMillis() + String.format("%04d", new Random().nextInt(10000));
        RentalPayment payment = new RentalPayment();
        payment.setPaymentNo(paymentNo);
        payment.setOrderNo(req.getOrderNo());
        payment.setAmount(amount);
        payment.setChannel("A"); // BASE: channel A
        payment.setPaymentMethod(req.getPaymentMethod());
        payment.setStatus(2); // success
        payment.setPayTime(new Date());
        paymentMapper.insert(payment);
        TransactionLogUtil.addDbCall("INSERT rental_payment paymentNo=" + paymentNo + " elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        return toPaymentRes(paymentMapper.findByPaymentNo(paymentNo));
    }

    public PaymentBody.PaymentRes query(PaymentBody.QueryReq req) {
        long t1 = System.currentTimeMillis();
        RentalPayment payment = null;
        if (req.getPaymentNo() != null) {
            payment = paymentMapper.findByPaymentNo(req.getPaymentNo());
        } else if (req.getOrderNo() != null) {
            payment = paymentMapper.findByOrderNo(req.getOrderNo());
        }
        TransactionLogUtil.addDbCall("SELECT rental_payment elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (payment == null) return null;

        // Sub-call: query payment gateway status
        String serialNo = TransactionLogUtil.getSerialNo();
        Map<String, Object> gwResult = subCallService.queryPaymentGateway(payment.getPaymentNo(), serialNo);
        TransactionLogUtil.addSubCall(gwResult.toString());

        return toPaymentRes(payment);
    }

    public PaymentBody.PaymentRes refund(PaymentBody.RefundReq req) {
        long t1 = System.currentTimeMillis();
        RentalPayment payment = paymentMapper.findByPaymentNo(req.getPaymentNo());
        TransactionLogUtil.addDbCall("SELECT rental_payment WHERE paymentNo=" + req.getPaymentNo() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (payment == null || payment.getStatus() != 2) return null;

        BigDecimal refundAmount = req.getRefundAmount() != null ? new BigDecimal(req.getRefundAmount()) : payment.getAmount();

        // Sub-call: payment gateway refund
        String serialNo = TransactionLogUtil.getSerialNo();
        Map<String, Object> refundResult = subCallService.refundPayment(req.getPaymentNo(), refundAmount, req.getRefundReason(), serialNo);
        TransactionLogUtil.addSubCall(refundResult.toString());

        // DB: update payment status
        long t2 = System.currentTimeMillis();
        paymentMapper.updateStatus(req.getPaymentNo(), 4); // refunded
        TransactionLogUtil.addDbCall("UPDATE rental_payment status=4 elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        return toPaymentRes(paymentMapper.findByPaymentNo(req.getPaymentNo()));
    }

    public PaymentBody.PaymentRes callback(PaymentBody.CallbackReq req) {
        long t1 = System.currentTimeMillis();
        RentalPayment payment = paymentMapper.findByPaymentNo(req.getPaymentNo());
        TransactionLogUtil.addDbCall("SELECT rental_payment WHERE paymentNo=" + req.getPaymentNo() + " elapsed=" + (System.currentTimeMillis() - t1) + "ms");
        if (payment == null) return null;

        long t2 = System.currentTimeMillis();
        paymentMapper.updateStatus(req.getPaymentNo(), req.getStatus());
        TransactionLogUtil.addDbCall("UPDATE rental_payment callback elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        return toPaymentRes(paymentMapper.findByPaymentNo(req.getPaymentNo()));
    }

    public Map<String, Object> reconcile(PaymentBody.ReconcileReq req) {
        String serialNo = TransactionLogUtil.getSerialNo();

        // DB: query local payments for the date
        long t1 = System.currentTimeMillis();
        Date date = DateTimeUtil.parse(req.getReconcileDate() + " 00:00:00");
        java.util.Calendar cal = java.util.Calendar.getInstance();
        cal.setTime(date);
        cal.set(java.util.Calendar.HOUR_OF_DAY, 23);
        cal.set(java.util.Calendar.MINUTE, 59);
        cal.set(java.util.Calendar.SECOND, 59);
        Date endOfDay = cal.getTime();
        List<RentalPayment> localPayments = paymentMapper.findByDateRange(date, endOfDay);
        TransactionLogUtil.addDbCall("SELECT rental_payment for reconcile elapsed=" + (System.currentTimeMillis() - t1) + "ms");

        // Sub-call: external reconciliation service
        Map<String, Object> reconResult = subCallService.queryReconciliation(req.getReconcileDate(), serialNo);
        TransactionLogUtil.addSubCall(reconResult.toString());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("reconcile_date", req.getReconcileDate());
        result.put("local_count", localPayments.size());
        BigDecimal localTotal = BigDecimal.ZERO;
        for (RentalPayment p : localPayments) {
            localTotal = localTotal.add(p.getAmount());
        }
        result.put("local_total", localTotal.toString());
        result.put("external_count", reconResult.getOrDefault("total_count", 0));
        result.put("external_total", reconResult.getOrDefault("total_amount", "0"));
        result.put("is_matched", localPayments.size() == (Integer) reconResult.getOrDefault("matched_count", 0));
        return result;
    }

    private PaymentBody.PaymentRes toPaymentRes(RentalPayment p) {
        PaymentBody.PaymentRes res = new PaymentBody.PaymentRes();
        res.setPaymentNo(p.getPaymentNo());
        res.setOrderNo(p.getOrderNo());
        res.setAmount(p.getAmount() != null ? p.getAmount().toString() : "0.00");
        res.setChannel(p.getChannel());
        res.setPaymentMethod(p.getPaymentMethod());
        res.setStatus(p.getStatus());
        res.setPayTime(DateTimeUtil.format(p.getPayTime()));
        res.setCreateTime(DateTimeUtil.format(p.getCreateTime()));
        return res;
    }
}
