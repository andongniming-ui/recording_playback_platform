package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

public class OrderBody {

    @JacksonXmlRootElement(localName = "body")
    public static class CreateReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "start_time") private String startTime;
        @JacksonXmlProperty(localName = "end_time") private String endTime;
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public String getStartTime() { return startTime; } public void setStartTime(String v) { this.startTime = v; }
        public String getEndTime() { return endTime; } public void setEndTime(String v) { this.endTime = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class QueryReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class CancelReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "cancel_reason") private String cancelReason;
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public String getCancelReason() { return cancelReason; } public void setCancelReason(String v) { this.cancelReason = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class CompleteReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "actual_return_time") private String actualReturnTime;
        @JacksonXmlProperty(localName = "damage_desc") private String damageDesc;
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public String getActualReturnTime() { return actualReturnTime; } public void setActualReturnTime(String v) { this.actualReturnTime = v; }
        public String getDamageDesc() { return damageDesc; } public void setDamageDesc(String v) { this.damageDesc = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class ListReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "status") private Integer status;
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class FeeReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "start_time") private String startTime;
        @JacksonXmlProperty(localName = "end_time") private String endTime;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public String getStartTime() { return startTime; } public void setStartTime(String v) { this.startTime = v; }
        public String getEndTime() { return endTime; } public void setEndTime(String v) { this.endTime = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class ExtendReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "new_end_time") private String newEndTime;
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public String getNewEndTime() { return newEndTime; } public void setNewEndTime(String v) { this.newEndTime = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class DetailReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class OrderRes {
        @JacksonXmlProperty(localName = "order_no") private String orderNo;
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "start_time") private String startTime;
        @JacksonXmlProperty(localName = "end_time") private String endTime;
        @JacksonXmlProperty(localName = "estimated_fee") private String estimatedFee;
        @JacksonXmlProperty(localName = "deposit") private String deposit;
        @JacksonXmlProperty(localName = "actual_fee") private String actualFee;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "create_time") private String createTime;
        @JacksonXmlProperty(localName = "vehicle_info") private VehicleBody.VehicleRes vehicleInfo;
        @JacksonXmlProperty(localName = "user_info") private UserBody.UserRes userInfo;
        @JacksonXmlProperty(localName = "insurance_info") private VehicleBody.InsuranceRes insuranceInfo;
        public String getOrderNo() { return orderNo; } public void setOrderNo(String v) { this.orderNo = v; }
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public String getStartTime() { return startTime; } public void setStartTime(String v) { this.startTime = v; }
        public String getEndTime() { return endTime; } public void setEndTime(String v) { this.endTime = v; }
        public String getEstimatedFee() { return estimatedFee; } public void setEstimatedFee(String v) { this.estimatedFee = v; }
        public String getDeposit() { return deposit; } public void setDeposit(String v) { this.deposit = v; }
        public String getActualFee() { return actualFee; } public void setActualFee(String v) { this.actualFee = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public String getCreateTime() { return createTime; } public void setCreateTime(String v) { this.createTime = v; }
        public VehicleBody.VehicleRes getVehicleInfo() { return vehicleInfo; } public void setVehicleInfo(VehicleBody.VehicleRes v) { this.vehicleInfo = v; }
        public UserBody.UserRes getUserInfo() { return userInfo; } public void setUserInfo(UserBody.UserRes v) { this.userInfo = v; }
        public VehicleBody.InsuranceRes getInsuranceInfo() { return insuranceInfo; } public void setInsuranceInfo(VehicleBody.InsuranceRes v) { this.insuranceInfo = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class OrderListRes {
        @JacksonXmlProperty(localName = "orders") private java.util.List<OrderRes> orders;
        @JacksonXmlProperty(localName = "total") private Integer total;
        public java.util.List<OrderRes> getOrders() { return orders; } public void setOrders(java.util.List<OrderRes> v) { this.orders = v; }
        public Integer getTotal() { return total; } public void setTotal(Integer v) { this.total = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class FeeRes {
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "days") private Integer days;
        @JacksonXmlProperty(localName = "daily_rate") private String dailyRate;
        @JacksonXmlProperty(localName = "basic_fee") private String basicFee;
        @JacksonXmlProperty(localName = "service_fee") private String serviceFee;
        @JacksonXmlProperty(localName = "insurance_fee") private String insuranceFee;
        @JacksonXmlProperty(localName = "total_fee") private String totalFee;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public Integer getDays() { return days; } public void setDays(Integer v) { this.days = v; }
        public String getDailyRate() { return dailyRate; } public void setDailyRate(String v) { this.dailyRate = v; }
        public String getBasicFee() { return basicFee; } public void setBasicFee(String v) { this.basicFee = v; }
        public String getServiceFee() { return serviceFee; } public void setServiceFee(String v) { this.serviceFee = v; }
        public String getInsuranceFee() { return insuranceFee; } public void setInsuranceFee(String v) { this.insuranceFee = v; }
        public String getTotalFee() { return totalFee; } public void setTotalFee(String v) { this.totalFee = v; }
    }
}
