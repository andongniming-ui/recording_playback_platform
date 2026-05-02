package com.rental.base.controller;

import com.rental.common.dto.*;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.service.PaymentService;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/payment")
public class PaymentController {

    private final PaymentService paymentService;
    public PaymentController(PaymentService paymentService) { this.paymentService = paymentService; }

    @PostMapping("/create")
    public XmlResponse create(@RequestBody PaymentBody.CreateReq body) {
        PaymentBody.PaymentRes res = paymentService.create(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "5001", "支付创建失败-订单不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "支付创建成功"), res);
    }

    @PostMapping("/query")
    public XmlResponse query(@RequestBody PaymentBody.QueryReq body) {
        PaymentBody.PaymentRes res = paymentService.query(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "5002", "支付记录不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }

    @PostMapping("/refund")
    public XmlResponse refund(@RequestBody PaymentBody.RefundReq body) {
        PaymentBody.PaymentRes res = paymentService.refund(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "5003", "退款失败-支付状态不正确"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "退款成功"), res);
    }

    @PostMapping("/callback")
    public XmlResponse callback(@RequestBody PaymentBody.CallbackReq body) {
        PaymentBody.PaymentRes res = paymentService.callback(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "5002", "支付记录不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "回调处理成功"), res);
    }

    @PostMapping("/reconcile")
    public XmlResponse reconcile(@RequestBody PaymentBody.ReconcileReq body) {
        Map<String, Object> res = paymentService.reconcile(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "对账完成"), res);
    }
}
