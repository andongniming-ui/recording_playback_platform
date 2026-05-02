package com.arex.demo.dating.common.model;

import java.util.HashMap;
import java.util.Map;

/**
 * 网关请求上下文 - 从 XML 报文中解析出的关键字段
 */
public class GatewayContext {

    private String rawXml;
    private String tranCode;
    private String requestField;
    private String traceId;
    private String tranTime;
    private String userId;
    private String targetUserId;
    private String phone;
    private String gender;
    private String age;
    private String city;
    private String searchKeyword;
    private String searchType;
    private String likeType;
    private String msgContent;
    private String msgType;
    private String giftType;
    private String giftAmount;
    private String vipLevel;
    private String durationDays;
    private String rechargeAmount;
    private String payChannel;
    private String photoUrl;
    private String isAvatar;
    private String reportType;
    private String reportDesc;
    private String blockReason;
    private String eventId;
    private String notifyType;
    private final Map<String, String> extraFields = new HashMap<String, String>();

    public String getRawXml() {
        return rawXml;
    }

    public void setRawXml(String rawXml) {
        this.rawXml = rawXml;
    }

    public String getTranCode() {
        return tranCode;
    }

    public void setTranCode(String tranCode) {
        this.tranCode = tranCode;
    }

    public String getRequestField() {
        return requestField;
    }

    public void setRequestField(String requestField) {
        this.requestField = requestField;
    }

    public String getTraceId() {
        return traceId;
    }

    public void setTraceId(String traceId) {
        this.traceId = traceId;
    }

    public String getTranTime() {
        return tranTime;
    }

    public void setTranTime(String tranTime) {
        this.tranTime = tranTime;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getTargetUserId() {
        return targetUserId;
    }

    public void setTargetUserId(String targetUserId) {
        this.targetUserId = targetUserId;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getGender() {
        return gender;
    }

    public void setGender(String gender) {
        this.gender = gender;
    }

    public String getAge() {
        return age;
    }

    public void setAge(String age) {
        this.age = age;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    public String getSearchKeyword() {
        return searchKeyword;
    }

    public void setSearchKeyword(String searchKeyword) {
        this.searchKeyword = searchKeyword;
    }

    public String getSearchType() {
        return searchType;
    }

    public void setSearchType(String searchType) {
        this.searchType = searchType;
    }

    public String getLikeType() {
        return likeType;
    }

    public void setLikeType(String likeType) {
        this.likeType = likeType;
    }

    public String getMsgContent() {
        return msgContent;
    }

    public void setMsgContent(String msgContent) {
        this.msgContent = msgContent;
    }

    public String getMsgType() {
        return msgType;
    }

    public void setMsgType(String msgType) {
        this.msgType = msgType;
    }

    public String getGiftType() {
        return giftType;
    }

    public void setGiftType(String giftType) {
        this.giftType = giftType;
    }

    public String getGiftAmount() {
        return giftAmount;
    }

    public void setGiftAmount(String giftAmount) {
        this.giftAmount = giftAmount;
    }

    public String getVipLevel() {
        return vipLevel;
    }

    public void setVipLevel(String vipLevel) {
        this.vipLevel = vipLevel;
    }

    public String getDurationDays() {
        return durationDays;
    }

    public void setDurationDays(String durationDays) {
        this.durationDays = durationDays;
    }

    public String getRechargeAmount() {
        return rechargeAmount;
    }

    public void setRechargeAmount(String rechargeAmount) {
        this.rechargeAmount = rechargeAmount;
    }

    public String getPayChannel() {
        return payChannel;
    }

    public void setPayChannel(String payChannel) {
        this.payChannel = payChannel;
    }

    public String getPhotoUrl() {
        return photoUrl;
    }

    public void setPhotoUrl(String photoUrl) {
        this.photoUrl = photoUrl;
    }

    public String getIsAvatar() {
        return isAvatar;
    }

    public void setIsAvatar(String isAvatar) {
        this.isAvatar = isAvatar;
    }

    public String getReportType() {
        return reportType;
    }

    public void setReportType(String reportType) {
        this.reportType = reportType;
    }

    public String getReportDesc() {
        return reportDesc;
    }

    public void setReportDesc(String reportDesc) {
        this.reportDesc = reportDesc;
    }

    public String getBlockReason() {
        return blockReason;
    }

    public void setBlockReason(String blockReason) {
        this.blockReason = blockReason;
    }

    public String getEventId() {
        return eventId;
    }

    public void setEventId(String eventId) {
        this.eventId = eventId;
    }

    public String getNotifyType() {
        return notifyType;
    }

    public void setNotifyType(String notifyType) {
        this.notifyType = notifyType;
    }

    public Map<String, String> getExtraFields() {
        return extraFields;
    }

    public void addExtraField(String key, String value) {
        extraFields.put(key, value);
    }
}
