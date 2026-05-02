package com.rental.common.model;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "order")
public class RentalOrder {
    private Long id;
    private String orderNo;
    private Long userId;
    private Long vehicleId;
    private Long storeId;
    private java.util.Date startTime;
    private java.util.Date endTime;
    private java.math.BigDecimal estimatedFee;
    private java.math.BigDecimal deposit;
    private java.math.BigDecimal actualFee;
    private Integer status;
    private java.util.Date createTime;
    private java.util.Date updateTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getOrderNo() { return orderNo; }
    public void setOrderNo(String orderNo) { this.orderNo = orderNo; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public Long getVehicleId() { return vehicleId; }
    public void setVehicleId(Long vehicleId) { this.vehicleId = vehicleId; }
    public Long getStoreId() { return storeId; }
    public void setStoreId(Long storeId) { this.storeId = storeId; }
    public java.util.Date getStartTime() { return startTime; }
    public void setStartTime(java.util.Date startTime) { this.startTime = startTime; }
    public java.util.Date getEndTime() { return endTime; }
    public void setEndTime(java.util.Date endTime) { this.endTime = endTime; }
    public java.math.BigDecimal getEstimatedFee() { return estimatedFee; }
    public void setEstimatedFee(java.math.BigDecimal estimatedFee) { this.estimatedFee = estimatedFee; }
    public java.math.BigDecimal getDeposit() { return deposit; }
    public void setDeposit(java.math.BigDecimal deposit) { this.deposit = deposit; }
    public java.math.BigDecimal getActualFee() { return actualFee; }
    public void setActualFee(java.math.BigDecimal actualFee) { this.actualFee = actualFee; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public java.util.Date getCreateTime() { return createTime; }
    public void setCreateTime(java.util.Date createTime) { this.createTime = createTime; }
    public java.util.Date getUpdateTime() { return updateTime; }
    public void setUpdateTime(java.util.Date updateTime) { this.updateTime = updateTime; }
}
