package com.rental.base.controller;

import com.rental.common.dto.*;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.service.OrderService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/order")
public class OrderController {

    private final OrderService orderService;
    public OrderController(OrderService orderService) { this.orderService = orderService; }

    @PostMapping("/create")
    public XmlResponse create(@RequestBody OrderBody.CreateReq body) {
        OrderBody.OrderRes res = orderService.create(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "4001", "创建订单失败-车辆不可用或用户不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "订单创建成功"), res);
    }

    @PostMapping("/query")
    public XmlResponse query(@RequestBody OrderBody.QueryReq body) {
        OrderBody.OrderRes res = orderService.query(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "4002", "订单不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }

    @PostMapping("/cancel")
    public XmlResponse cancel(@RequestBody OrderBody.CancelReq body) {
        OrderBody.OrderRes res = orderService.cancel(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "4003", "取消失败-订单状态不正确"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "订单取消成功"), res);
    }

    @PostMapping("/complete")
    public XmlResponse complete(@RequestBody OrderBody.CompleteReq body) {
        OrderBody.OrderRes res = orderService.complete(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "4004", "还车失败-订单状态不正确"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "还车完成"), res);
    }

    @PostMapping("/list")
    public XmlResponse list(@RequestBody OrderBody.ListReq body) {
        OrderBody.OrderListRes res = orderService.list(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }

    @PostMapping("/calculate-fee")
    public XmlResponse calculateFee(@RequestBody OrderBody.FeeReq body) {
        OrderBody.FeeRes res = orderService.calculateFee(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "4005", "计算失败-车辆不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "费用计算完成"), res);
    }

    @PostMapping("/extend")
    public XmlResponse extend(@RequestBody OrderBody.ExtendReq body) {
        OrderBody.OrderRes res = orderService.extend(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "4006", "续租失败-订单状态不正确"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "续租成功"), res);
    }

    @PostMapping("/detail")
    public XmlResponse detail(@RequestBody OrderBody.DetailReq body) {
        OrderBody.OrderRes res = orderService.detail(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "4002", "订单不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }
}
