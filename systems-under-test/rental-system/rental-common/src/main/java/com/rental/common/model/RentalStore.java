package com.rental.common.model;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "store")
public class RentalStore {
    private Long id;
    private String storeName;
    private String address;
    private String phone;
    private String businessHours;
    private Integer status;
    private java.util.Date createTime;
    private java.util.Date updateTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getStoreName() { return storeName; }
    public void setStoreName(String storeName) { this.storeName = storeName; }
    public String getAddress() { return address; }
    public void setAddress(String address) { this.address = address; }
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    public String getBusinessHours() { return businessHours; }
    public void setBusinessHours(String businessHours) { this.businessHours = businessHours; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public java.util.Date getCreateTime() { return createTime; }
    public void setCreateTime(java.util.Date createTime) { this.createTime = createTime; }
    public java.util.Date getUpdateTime() { return updateTime; }
    public void setUpdateTime(java.util.Date updateTime) { this.updateTime = updateTime; }
}
