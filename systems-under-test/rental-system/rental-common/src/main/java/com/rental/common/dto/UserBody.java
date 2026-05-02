package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

public class UserBody {
    @JacksonXmlRootElement(localName = "body")
    public static class RegisterReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "username") private String username;
        @JacksonXmlProperty(localName = "password") private String password;
        @JacksonXmlProperty(localName = "real_name") private String realName;
        @JacksonXmlProperty(localName = "phone") private String phone;
        @JacksonXmlProperty(localName = "email") private String email;
        @JacksonXmlProperty(localName = "id_card") private String idCard;
        @JacksonXmlProperty(localName = "driver_license") private String driverLicense;
        public String getUsername() { return username; } public void setUsername(String v) { this.username = v; }
        public String getPassword() { return password; } public void setPassword(String v) { this.password = v; }
        public String getRealName() { return realName; } public void setRealName(String v) { this.realName = v; }
        public String getPhone() { return phone; } public void setPhone(String v) { this.phone = v; }
        public String getEmail() { return email; } public void setEmail(String v) { this.email = v; }
        public String getIdCard() { return idCard; } public void setIdCard(String v) { this.idCard = v; }
        public String getDriverLicense() { return driverLicense; } public void setDriverLicense(String v) { this.driverLicense = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class LoginReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "username") private String username;
        @JacksonXmlProperty(localName = "password") private String password;
        public String getUsername() { return username; } public void setUsername(String v) { this.username = v; }
        public String getPassword() { return password; } public void setPassword(String v) { this.password = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class QueryReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "username") private String username;
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public String getUsername() { return username; } public void setUsername(String v) { this.username = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class UpdateReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "real_name") private String realName;
        @JacksonXmlProperty(localName = "phone") private String phone;
        @JacksonXmlProperty(localName = "email") private String email;
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public String getRealName() { return realName; } public void setRealName(String v) { this.realName = v; }
        public String getPhone() { return phone; } public void setPhone(String v) { this.phone = v; }
        public String getEmail() { return email; } public void setEmail(String v) { this.email = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class UserRes {
        @JacksonXmlProperty(localName = "user_id") private Long userId;
        @JacksonXmlProperty(localName = "username") private String username;
        @JacksonXmlProperty(localName = "real_name") private String realName;
        @JacksonXmlProperty(localName = "phone") private String phone;
        @JacksonXmlProperty(localName = "email") private String email;
        @JacksonXmlProperty(localName = "id_card") private String idCard;
        @JacksonXmlProperty(localName = "driver_license") private String driverLicense;
        @JacksonXmlProperty(localName = "membership_level") private String membershipLevel;
        @JacksonXmlProperty(localName = "balance") private String balance;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "create_time") private String createTime;
        public Long getUserId() { return userId; } public void setUserId(Long v) { this.userId = v; }
        public String getUsername() { return username; } public void setUsername(String v) { this.username = v; }
        public String getRealName() { return realName; } public void setRealName(String v) { this.realName = v; }
        public String getPhone() { return phone; } public void setPhone(String v) { this.phone = v; }
        public String getEmail() { return email; } public void setEmail(String v) { this.email = v; }
        public String getIdCard() { return idCard; } public void setIdCard(String v) { this.idCard = v; }
        public String getDriverLicense() { return driverLicense; } public void setDriverLicense(String v) { this.driverLicense = v; }
        public String getMembershipLevel() { return membershipLevel; } public void setMembershipLevel(String v) { this.membershipLevel = v; }
        public String getBalance() { return balance; } public void setBalance(String v) { this.balance = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public String getCreateTime() { return createTime; } public void setCreateTime(String v) { this.createTime = v; }
    }
}
