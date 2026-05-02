package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

public class PaymentBody {

    @JacksonXmlRootElement(localName = "body")
    public static class CreateReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "amount") private String amount;
        @JacksonXmlProperty(localName = "payment_method") private String paymentMethod;
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public String getAmount() { return amount; } public void setAmount(String v) { this.amount = v; }
        public String getPaymentMethod() { return paymentMethod; } public void setPaymentMethod(String v) { this.paymentMethod = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class QueryReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "payment_no") private String paymentNo;
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        public String getPaymentNo() { return paymentNo; } public void setPaymentNo(String v) { this.paymentNo = v; }
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class RefundReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "payment_no") private String paymentNo;
        @JacksonXmlProperty(localName = "refund_amount") private String refundAmount;
        @JacksonXmlProperty(localName = "refund_reason") private String refundReason;
        public String getPaymentNo() { return paymentNo; } public void setPaymentNo(String v) { this.paymentNo = v; }
        public String getRefundAmount() { return refundAmount; } public void setRefundAmount(String v) { this.refundAmount = v; }
        public String getRefundReason() { return refundReason; } public void setRefundReason(String v) { this.refundReason = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class CallbackReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "payment_no") private String paymentNo;
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "gateway_trade_no") private String gatewayTradeNo;
        @JacksonXmlProperty(localName = "pay_time") private String payTime;
        public String getPaymentNo() { return paymentNo; } public void setPaymentNo(String v) { this.paymentNo = v; }
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public String getGatewayTradeNo() { return gatewayTradeNo; } public void setGatewayTradeNo(String v) { this.gatewayTradeNo = v; }
        public String getPayTime() { return payTime; } public void setPayTime(String v) { this.payTime = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class ReconcileReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "reconcile_date") private String reconcileDate;
        public String getReconcileDate() { return reconcileDate; } public void setReconcileDate(String v) { this.reconcileDate = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class PaymentRes {
        @JacksonXmlProperty(localName = "payment_no") private String paymentNo;
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "amount") private String amount;
        @JacksonXmlProperty(localName = "channel") private String channel;
        @JacksonXmlProperty(localName = "payment_method") private String paymentMethod;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "pay_time") private String payTime;
        @JacksonXmlProperty(localName = "create_time") private String createTime;
        public String getPaymentNo() { return paymentNo; } public void setPaymentNo(String v) { this.paymentNo = v; }
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public String getAmount() { return amount; } public void setAmount(String v) { this.amount = v; }
        public String getChannel() { return channel; } public void setChannel(String v) { this.channel = v; }
        public String getPaymentMethod() { return paymentMethod; } public void setPaymentMethod(String v) { this.paymentMethod = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public String getPayTime() { return payTime; } public void setPayTime(String v) { this.payTime = v; }
        public String getCreateTime() { return createTime; } public void setCreateTime(String v) { this.createTime = v; }
    }
}
