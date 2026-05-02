package com.rental.common.model;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "payment")
public class RentalPayment {
    private Long id;
    private String paymentNo;
    private String orderNo;
    private java.math.BigDecimal amount;
    private String channel;
    private String paymentMethod;
    private Integer status;
    private java.util.Date payTime;
    private java.util.Date createTime;
    private java.util.Date updateTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getPaymentNo() { return paymentNo; }
    public void setPaymentNo(String paymentNo) { this.paymentNo = paymentNo; }
    public String getOrderNo() { return orderNo; }
    public void setOrderNo(String orderNo) { this.orderNo = orderNo; }
    public java.math.BigDecimal getAmount() { return amount; }
    public void setAmount(java.math.BigDecimal amount) { this.amount = amount; }
    public String getChannel() { return channel; }
    public void setChannel(String channel) { this.channel = channel; }
    public String getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public java.util.Date getPayTime() { return payTime; }
    public void setPayTime(java.util.Date payTime) { this.payTime = payTime; }
    public java.util.Date getCreateTime() { return createTime; }
    public void setCreateTime(java.util.Date createTime) { this.createTime = createTime; }
    public java.util.Date getUpdateTime() { return updateTime; }
    public void setUpdateTime(java.util.Date updateTime) { this.updateTime = updateTime; }
}
