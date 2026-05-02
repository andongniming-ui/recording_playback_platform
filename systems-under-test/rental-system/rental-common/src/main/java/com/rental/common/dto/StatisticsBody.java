package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

public class StatisticsBody {

    @JacksonXmlRootElement(localName = "body")
    public static class DailyReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "stat_date") private String statDate;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        public String getStatDate() { return statDate; } public void setStatDate(String v) { this.statDate = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class RevenueReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "start_date") private String startDate;
        @JacksonXmlProperty(localName = "end_date") private String endDate;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        public String getStartDate() { return startDate; } public void setStartDate(String v) { this.startDate = v; }
        public String getEndDate() { return endDate; } public void setEndDate(String v) { this.endDate = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class UtilizationReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "stat_date") private String statDate;
        public String getStatDate() { return statDate; } public void setStatDate(String v) { this.statDate = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class UserReportReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "start_date") private String startDate;
        @JacksonXmlProperty(localName = "end_date") private String endDate;
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public String getStartDate() { return startDate; } public void setStartDate(String v) { this.startDate = v; }
        public String getEndDate() { return endDate; } public void setEndDate(String v) { this.endDate = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class DailyStatRes {
        @JacksonXmlProperty(localName = "stat_date") private String statDate;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "store_name") private String storeName;
        @JacksonXmlProperty(localName = "total_orders") private Integer totalOrders;
        @JacksonXmlProperty(localName = "active_orders") private Integer activeOrders;
        @JacksonXmlProperty(localName = "completed_orders") private Integer completedOrders;
        @JacksonXmlProperty(localName = "cancelled_orders") private Integer cancelledOrders;
        @JacksonXmlProperty(localName = "total_revenue") private String totalRevenue;
        @JacksonXmlProperty(localName = "create_time") private String createTime;
        public String getStatDate() { return statDate; } public void setStatDate(String v) { this.statDate = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public String getStoreName() { return storeName; } public void setStoreName(String v) { this.storeName = v; }
        public Integer getTotalOrders() { return totalOrders; } public void setTotalOrders(Integer v) { this.totalOrders = v; }
        public Integer getActiveOrders() { return activeOrders; } public void setActiveOrders(Integer v) { this.activeOrders = v; }
        public Integer getCompletedOrders() { return completedOrders; } public void setCompletedOrders(Integer v) { this.completedOrders = v; }
        public Integer getCancelledOrders() { return cancelledOrders; } public void setCancelledOrders(Integer v) { this.cancelledOrders = v; }
        public String getTotalRevenue() { return totalRevenue; } public void setTotalRevenue(String v) { this.totalRevenue = v; }
        public String getCreateTime() { return createTime; } public void setCreateTime(String v) { this.createTime = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class RevenueRes {
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "store_name") private String storeName;
        @JacksonXmlProperty(localName = "total_orders") private Integer totalOrders;
        @JacksonXmlProperty(localName = "total_revenue") private String totalRevenue;
        @JacksonXmlProperty(localName = "avg_order_amount") private String avgOrderAmount;
        @JacksonXmlProperty(localName = "period") private String period;
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public String getStoreName() { return storeName; } public void setStoreName(String v) { this.storeName = v; }
        public Integer getTotalOrders() { return totalOrders; } public void setTotalOrders(Integer v) { this.totalOrders = v; }
        public String getTotalRevenue() { return totalRevenue; } public void setTotalRevenue(String v) { this.totalRevenue = v; }
        public String getAvgOrderAmount() { return avgOrderAmount; } public void setAvgOrderAmount(String v) { this.avgOrderAmount = v; }
        public String getPeriod() { return period; } public void setPeriod(String v) { this.period = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class UtilizationRes {
        @JacksonXmlProperty(localName = "stat_date") private String statDate;
        @JacksonXmlProperty(localName = "total_vehicles") private Integer totalVehicles;
        @JacksonXmlProperty(localName = "rented_vehicles") private Integer rentedVehicles;
        @JacksonXmlProperty(localName = "available_vehicles") private Integer availableVehicles;
        @JacksonXmlProperty(localName = "utilization_rate") private String utilizationRate;
        public String getStatDate() { return statDate; } public void setStatDate(String v) { this.statDate = v; }
        public Integer getTotalVehicles() { return totalVehicles; } public void setTotalVehicles(Integer v) { this.totalVehicles = v; }
        public Integer getRentedVehicles() { return rentedVehicles; } public void setRentedVehicles(Integer v) { this.rentedVehicles = v; }
        public Integer getAvailableVehicles() { return availableVehicles; } public void setAvailableVehicles(Integer v) { this.availableVehicles = v; }
        public String getUtilizationRate() { return utilizationRate; } public void setUtilizationRate(String v) { this.utilizationRate = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class UserReportRes {
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "username") private String username;
        @JacksonXmlProperty(localName = "real_name") private String realName;
        @JacksonXmlProperty(localName = "total_rentals") private Integer totalRentals;
        @JacksonXmlProperty(localName = "total_spent") private String totalSpent;
        @JacksonXmlProperty(localName = "favorite_brand") private String favoriteBrand;
        @JacksonXmlProperty(localName = "avg_rental_days") private String avgRentalDays;
        @JacksonXmlProperty(localName = "membership_level") private String membershipLevel;
        @JacksonXmlProperty(localName = "period") private String period;
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public String getUsername() { return username; } public void setUsername(String v) { this.username = v; }
        public String getRealName() { return realName; } public void setRealName(String v) { this.realName = v; }
        public Integer getTotalRentals() { return totalRentals; } public void setTotalRentals(Integer v) { this.totalRentals = v; }
        public String getTotalSpent() { return totalSpent; } public void setTotalSpent(String v) { this.totalSpent = v; }
        public String getFavoriteBrand() { return favoriteBrand; } public void setFavoriteBrand(String v) { this.favoriteBrand = v; }
        public String getAvgRentalDays() { return avgRentalDays; } public void setAvgRentalDays(String v) { this.avgRentalDays = v; }
        public String getMembershipLevel() { return membershipLevel; } public void setMembershipLevel(String v) { this.membershipLevel = v; }
        public String getPeriod() { return period; } public void setPeriod(String v) { this.period = v; }
    }
}
