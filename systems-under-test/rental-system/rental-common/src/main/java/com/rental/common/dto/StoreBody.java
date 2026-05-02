package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

public class StoreBody {

    @JacksonXmlRootElement(localName = "body")
    public static class AddReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "store_name") private String storeName;
        @JacksonXmlProperty(localName = "address") private String address;
        @JacksonXmlProperty(localName = "phone") private String phone;
        @JacksonXmlProperty(localName = "business_hours") private String businessHours;
        public String getStoreName() { return storeName; } public void setStoreName(String v) { this.storeName = v; }
        public String getAddress() { return address; } public void setAddress(String v) { this.address = v; }
        public String getPhone() { return phone; } public void setPhone(String v) { this.phone = v; }
        public String getBusinessHours() { return businessHours; } public void setBusinessHours(String v) { this.businessHours = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class QueryReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class ListReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "status") private Integer status;
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class StoreRes {
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "store_name") private String storeName;
        @JacksonXmlProperty(localName = "address") private String address;
        @JacksonXmlProperty(localName = "phone") private String phone;
        @JacksonXmlProperty(localName = "business_hours") private String businessHours;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "vehicle_count") private Integer vehicleCount;
        @JacksonXmlProperty(localName = "create_time") private String createTime;
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public String getStoreName() { return storeName; } public void setStoreName(String v) { this.storeName = v; }
        public String getAddress() { return address; } public void setAddress(String v) { this.address = v; }
        public String getPhone() { return phone; } public void setPhone(String v) { this.phone = v; }
        public String getBusinessHours() { return businessHours; } public void setBusinessHours(String v) { this.businessHours = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public Integer getVehicleCount() { return vehicleCount; } public void setVehicleCount(Integer v) { this.vehicleCount = v; }
        public String getCreateTime() { return createTime; } public void setCreateTime(String v) { this.createTime = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class StoreListRes {
        @JacksonXmlProperty(localName = "stores") private java.util.List<StoreRes> stores;
        @JacksonXmlProperty(localName = "total") private Integer total;
        public java.util.List<StoreRes> getStores() { return stores; } public void setStores(java.util.List<StoreRes> v) { this.stores = v; }
        public Integer getTotal() { return total; } public void setTotal(Integer v) { this.total = v; }
    }
}
