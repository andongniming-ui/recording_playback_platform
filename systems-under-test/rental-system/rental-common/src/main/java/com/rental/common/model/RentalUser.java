package com.rental.common.model;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "user")
public class RentalUser {
    private Long id;
    private String username;
    private String password;
    private String realName;
    private String phone;
    private String email;
    private String idCard;
    private String driverLicense;
    private String membershipLevel;
    private java.math.BigDecimal balance;
    private Integer status;
    private java.util.Date createTime;
    private java.util.Date updateTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }
    public String getPassword() { return password; }
    public void setPassword(String password) { this.password = password; }
    public String getRealName() { return realName; }
    public void setRealName(String realName) { this.realName = realName; }
    public String getPhone() { return phone; }
    public void setPhone(String phone) { this.phone = phone; }
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    public String getIdCard() { return idCard; }
    public void setIdCard(String idCard) { this.idCard = idCard; }
    public String getDriverLicense() { return driverLicense; }
    public void setDriverLicense(String driverLicense) { this.driverLicense = driverLicense; }
    public String getMembershipLevel() { return membershipLevel; }
    public void setMembershipLevel(String membershipLevel) { this.membershipLevel = membershipLevel; }
    public java.math.BigDecimal getBalance() { return balance; }
    public void setBalance(java.math.BigDecimal balance) { this.balance = balance; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public java.util.Date getCreateTime() { return createTime; }
    public void setCreateTime(java.util.Date createTime) { this.createTime = createTime; }
    public java.util.Date getUpdateTime() { return updateTime; }
    public void setUpdateTime(java.util.Date updateTime) { this.updateTime = updateTime; }
}
