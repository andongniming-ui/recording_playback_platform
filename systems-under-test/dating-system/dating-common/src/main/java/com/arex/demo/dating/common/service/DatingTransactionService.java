package com.arex.demo.dating.common.service;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import com.arex.demo.dating.common.config.DatingVariantProperties;
import com.arex.demo.dating.common.model.DatingTransactionDefinition;
import com.arex.demo.dating.common.model.GatewayContext;
import com.arex.demo.dating.common.model.GatewayResult;
import com.arex.demo.dating.common.repository.DatingDataRepository;

/**
 * 交友系统交易处理服务
 * 包含 15 个交易码的处理逻辑，每个交易码有：
 * 1. 唯一的外呼子调用（HTTP 请求到不同的外部服务）
 * 2. 唯一的数据库操作（操作不同的表和字段）
 * 3. 所有操作通过 trace_id 关联到日志
 */
@Service
public class DatingTransactionService {

    private static final Logger log = LoggerFactory.getLogger(DatingTransactionService.class);

    private final DatingDataRepository repository;
    private final RestTemplate restTemplate;
    private final DatingVariantProperties variantProperties;

    public DatingTransactionService(DatingDataRepository repository,
                                    RestTemplate restTemplate,
                                    DatingVariantProperties variantProperties) {
        this.repository = repository;
        this.restTemplate = restTemplate;
        this.variantProperties = variantProperties;
    }

    /**
     * 统一处理入口：根据交易码分发到对应处理方法
     */
    public GatewayResult process(DatingTransactionDefinition definition, GatewayContext context) {
        String traceId = context.getTraceId();
        String tranCode = definition.getCode();
        log.info("traceId={} ========== 交易处理开始: {} - {} ==========", traceId, tranCode, definition.getDisplayName());

        GatewayResult result;
        try {
            switch (tranCode) {
                case "DAT001": result = processUserRegister(context); break;
                case "DAT002": result = processUserLogin(context); break;
                case "DAT003": result = processProfileUpdate(context); break;
                case "DAT004": result = processUserSearch(context); break;
                case "DAT005": result = processLikeUser(context); break;
                case "DAT006": result = processMatchRecommend(context); break;
                case "DAT007": result = processSendMessage(context); break;
                case "DAT008": result = processSendGift(context); break;
                case "DAT009": result = processVipOpen(context); break;
                case "DAT010": result = processWalletRecharge(context); break;
                case "DAT011": result = processUploadPhoto(context); break;
                case "DAT012": result = processReportUser(context); break;
                case "DAT013": result = processBlockUser(context); break;
                case "DAT014": result = processEventSignup(context); break;
                case "DAT015": result = processNotifyQuery(context); break;
                default:
                    result = new GatewayResult();
                    result.setStatus("FAIL");
                    result.setMessage("未知交易码: " + tranCode);
                    return result;
            }
        } catch (Exception ex) {
            log.error("traceId={} 交易处理异常: {} - {}", traceId, tranCode, ex.getMessage(), ex);
            result = new GatewayResult();
            result.setStatus("FAIL");
            result.setMessage("交易处理异常: " + ex.getMessage());
            result.setSubCallFlag("N");
            result.setDbFlag("N");
        }

        log.info("traceId={} ========== 交易处理完成: {} - status={} ==========", traceId, tranCode, result.getStatus());
        return result;
    }

    // ==================== DAT001 用户注册 ====================
    // 外呼：风控校验服务 /internal/dating/risk-verify
    // 数据库：INSERT t_user

    private GatewayResult processUserRegister(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = hasText(context.getUserId()) ? context.getUserId() : "U" + System.currentTimeMillis() % 100000;
        String phone = hasText(context.getPhone()) ? context.getPhone() : "1380000" + userId.substring(1);
        String gender = hasText(context.getGender()) ? context.getGender() : "M";
        int age = hasText(context.getAge()) ? Integer.parseInt(context.getAge()) : 25;
        String city = hasText(context.getCity()) ? context.getCity() : "BEIJING";

        // 1. 外呼：风控校验服务
        Map<String, Object> riskResult = fetch(
            "/internal/dating/risk-verify",
            "traceId", traceId,
            "userId", userId,
            "phone", phone,
            "tranCode", "DAT001"
        );
        String riskLevel = stringValue(riskResult, "riskLevel", "LOW");
        String riskScore = stringValue(riskResult, "riskScore", "10");
        log.info("traceId={} [外呼] 风控校验结果: riskLevel={}, riskScore={}", traceId, riskLevel, riskScore);

        // 2. 数据库：INSERT t_user
        repository.insertUser(userId, "用户" + userId, gender, age, city, phone, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("用户注册成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setRiskLevel(riskLevel);
        result.setRiskScore(riskScore);
        result.addResultData("user_id", userId);
        result.addResultData("nick_name", "用户" + userId);
        return result;
    }

    // ==================== DAT002 用户登录 ====================
    // 外呼：设备指纹服务 /internal/dating/device-fingerprint
    // 数据库：INSERT t_login_log + SELECT t_user

    private GatewayResult processUserLogin(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();

        // 1. 外呼：设备指纹服务
        Map<String, Object> deviceResult = fetch(
            "/internal/dating/device-fingerprint",
            "traceId", traceId,
            "userId", userId,
            "tranCode", "DAT002"
        );
        String deviceId = stringValue(deviceResult, "deviceId", "DEV_DEFAULT");
        String deviceType = stringValue(deviceResult, "deviceType", "IOS");
        String riskTag = stringValue(deviceResult, "riskTag", "NORMAL");
        log.info("traceId={} [外呼] 设备指纹结果: deviceId={}, deviceType={}, riskTag={}",
            traceId, deviceId, deviceType, riskTag);

        // 2. 数据库：INSERT t_login_log + SELECT t_user
        repository.insertLoginLog(userId, "127.0.0.1", deviceType + "_" + deviceId, traceId);
        Map<String, Object> user = repository.findUser(userId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("用户登录成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.addResultData("user_id", userId);
        result.addResultData("nick_name", stringValue(user, "nick_name", ""));
        result.addResultData("vip_level", stringValue(user, "vip_level", "0"));
        result.addResultData("device_type", deviceType);
        result.addResultData("risk_tag", riskTag);
        return result;
    }

    // ==================== DAT003 资料更新 ====================
    // 外呼：图片审核服务 /internal/dating/image-audit
    // 数据库：UPDATE t_user_profile

    private GatewayResult processProfileUpdate(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String bio = hasText(context.getMsgContent()) ? context.getMsgContent() : "更新了个人简介";
        String occupation = hasText(context.getSearchKeyword()) ? context.getSearchKeyword() : "工程师";

        // 1. 外呼：图片审核服务
        Map<String, Object> auditResult = fetch(
            "/internal/dating/image-audit",
            "traceId", traceId,
            "userId", userId,
            "tranCode", "DAT003"
        );
        String auditStatus = stringValue(auditResult, "auditResult", "PASS");
        String auditScore = stringValue(auditResult, "auditScore", "95");
        String rejectReason = stringValue(auditResult, "rejectReason", "");
        log.info("traceId={} [外呼] 图片审核结果: auditResult={}, auditScore={}", traceId, auditStatus, auditScore);

        // 2. 数据库：UPDATE t_user_profile
        repository.updateUserProfile(userId, bio, occupation, "20-30K", "本科", traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("资料更新成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setAuditResult(auditStatus);
        result.addResultData("audit_score", auditScore);
        result.addResultData("reject_reason", rejectReason);
        return result;
    }

    // ==================== DAT004 用户搜索 ====================
    // 外呼：推荐算法服务 /internal/dating/recommend
    // 数据库：INSERT t_search_history + SELECT t_user

    private GatewayResult processUserSearch(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String keyword = hasText(context.getSearchKeyword()) ? context.getSearchKeyword() : "全部";
        String searchType = hasText(context.getSearchType()) ? context.getSearchType() : "CITY";
        String city = hasText(context.getCity()) ? context.getCity() : "BEIJING";
        String gender = hasText(context.getGender()) ? context.getGender() : "F";

        // 1. 外呼：推荐算法服务
        Map<String, Object> recommendResult = fetch(
            "/internal/dating/recommend",
            "traceId", traceId,
            "userId", userId,
            "keyword", keyword,
            "tranCode", "DAT004"
        );
        String matchScore = stringValue(recommendResult, "matchScore", "75");
        String algorithm = stringValue(recommendResult, "algorithm", "COLLABORATIVE");
        String recommendReason = stringValue(recommendResult, "recommendReason", "同城推荐");
        log.info("traceId={} [外呼] 推荐算法结果: matchScore={}, algorithm={}", traceId, matchScore, algorithm);

        // 2. 数据库：INSERT t_search_history + SELECT t_user
        java.util.List<Map<String, Object>> searchResults = repository.searchUsers(city, gender);
        repository.insertSearchHistory(userId, searchType, keyword, searchResults.size(), traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("用户搜索完成");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setMatchScore(matchScore);
        result.addResultData("search_count", String.valueOf(searchResults.size()));
        result.addResultData("algorithm", algorithm);
        result.addResultData("recommend_reason", recommendReason);
        return result;
    }

    // ==================== DAT005 点赞喜欢 ====================
    // 外呼：消息推送服务 /internal/dating/push-notify
    // 数据库：INSERT t_like_record + UPDATE t_user_stats

    private GatewayResult processLikeUser(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String targetUserId = hasText(context.getTargetUserId()) ? context.getTargetUserId() : "U10002";
        String likeType = hasText(context.getLikeType()) ? context.getLikeType() : "LIKE";

        // 1. 外呼：消息推送服务
        Map<String, Object> pushResult = fetch(
            "/internal/dating/push-notify",
            "traceId", traceId,
            "userId", userId,
            "targetUserId", targetUserId,
            "likeType", likeType,
            "tranCode", "DAT005"
        );
        String pushId = stringValue(pushResult, "pushId", "PUSH_" + System.currentTimeMillis());
        String pushStatus = stringValue(pushResult, "pushStatus", "SENT");
        String channel = stringValue(pushResult, "channel", "APP");
        log.info("traceId={} [外呼] 消息推送结果: pushId={}, pushStatus={}, channel={}", traceId, pushId, pushStatus, channel);

        // 2. 数据库：INSERT t_like_record + UPDATE t_user_stats
        repository.insertLikeRecord(userId, targetUserId, likeType, traceId);
        repository.incrementLikeCount(userId, traceId);
        repository.incrementLikedCount(targetUserId, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("点赞成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.addResultData("push_id", pushId);
        result.addResultData("push_status", pushStatus);
        return result;
    }

    // ==================== DAT006 匹配推荐 ====================
    // 外呼：匹配算法服务 /internal/dating/match-calc
    // 数据库：INSERT t_match_record + SELECT t_user

    private GatewayResult processMatchRecommend(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();

        // 先查当前用户信息
        Map<String, Object> user = repository.findUser(userId);
        String gender = stringValue(user, "gender", "M");

        // 1. 外呼：匹配算法服务
        Map<String, Object> matchResult = fetch(
            "/internal/dating/match-calc",
            "traceId", traceId,
            "userId", userId,
            "gender", gender,
            "tranCode", "DAT006"
        );
        String matchScore = stringValue(matchResult, "matchScore", "82");
        String matchType = stringValue(matchResult, "matchType", "INTEREST");
        String compatibility = stringValue(matchResult, "compatibility", "HIGH");
        log.info("traceId={} [外呼] 匹配算法结果: matchScore={}, matchType={}, compatibility={}",
            traceId, matchScore, matchType, compatibility);

        // 2. 数据库：INSERT t_match_record + SELECT t_user
        java.util.List<Map<String, Object>> potentials = repository.findPotentialMatches(userId, gender);
        String matchedUserId = potentials.isEmpty() ? "U10002" : stringValue(potentials.get(0), "user_id", "U10002");
        repository.insertMatchRecord(userId, matchedUserId, Integer.parseInt(matchScore), matchType, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("匹配推荐完成");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setMatchScore(matchScore);
        result.addResultData("matched_user_id", matchedUserId);
        result.addResultData("match_type", matchType);
        result.addResultData("compatibility", compatibility);
        return result;
    }

    // ==================== DAT007 发送消息 ====================
    // 外呼：敏感词过滤服务 /internal/dating/sensitive-filter
    // 数据库：INSERT t_message + UPDATE t_conversation

    private GatewayResult processSendMessage(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String targetUserId = hasText(context.getTargetUserId()) ? context.getTargetUserId() : "U10002";
        String content = hasText(context.getMsgContent()) ? context.getMsgContent() : "你好，很高兴认识你！";
        String msgType = hasText(context.getMsgType()) ? context.getMsgType() : "TEXT";

        // 1. 外呼：敏感词过滤服务
        Map<String, Object> filterResult = fetch(
            "/internal/dating/sensitive-filter",
            "traceId", traceId,
            "userId", userId,
            "content", content,
            "tranCode", "DAT007"
        );
        String filtered = stringValue(filterResult, "filtered", "N");
        String filterLevel = stringValue(filterResult, "filterLevel", "NONE");
        String keywords = stringValue(filterResult, "keywords", "");
        log.info("traceId={} [外呼] 敏感词过滤结果: filtered={}, filterLevel={}", traceId, filtered, filterLevel);

        // 如果过滤等级为 REJECT 则拒绝发送
        if ("REJECT".equals(filterLevel)) {
            GatewayResult result = new GatewayResult();
            result.setStatus("REJECT");
            result.setMessage("消息包含违规内容，发送被拒绝");
            result.setSubCallFlag("Y");
            result.setDbFlag("N");
            result.setFilterLevel(filterLevel);
            return result;
        }

        // 2. 数据库：INSERT t_message + UPDATE t_conversation
        String filteredContent = "Y".equals(filtered) ? "[已过滤]" : content;
        repository.insertMessage(userId, targetUserId, filteredContent, msgType, traceId);
        repository.updateConversation(userId, targetUserId, 1, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("消息发送成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setFilterLevel(filterLevel);
        result.addResultData("filtered", filtered);
        result.addResultData("keywords", keywords);
        return result;
    }

    // ==================== DAT008 送礼物 ====================
    // 外呼：支付网关服务 /internal/dating/pay-gift
    // 数据库：INSERT t_gift_order + UPDATE t_wallet

    private GatewayResult processSendGift(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String targetUserId = hasText(context.getTargetUserId()) ? context.getTargetUserId() : "U10002";
        String giftType = hasText(context.getGiftType()) ? context.getGiftType() : "ROSE";
        BigDecimal giftAmount = hasText(context.getGiftAmount()) ? new BigDecimal(context.getGiftAmount()) : new BigDecimal("9.90");

        // 1. 外呼：支付网关服务
        Map<String, Object> payResult = fetch(
            "/internal/dating/pay-gift",
            "traceId", traceId,
            "userId", userId,
            "targetUserId", targetUserId,
            "giftType", giftType,
            "giftAmount", giftAmount.toPlainString(),
            "tranCode", "DAT008"
        );
        String payStatus = stringValue(payResult, "payStatus", "SUCCESS");
        String transactionId = stringValue(payResult, "transactionId", "TXN_" + System.currentTimeMillis());
        String payAmount = stringValue(payResult, "payAmount", giftAmount.toPlainString());
        log.info("traceId={} [外呼] 支付网关结果: payStatus={}, transactionId={}", traceId, payStatus, transactionId);

        // 2. 数据库：INSERT t_gift_order + UPDATE t_wallet
        repository.insertGiftOrder(userId, targetUserId, giftType, giftAmount, traceId);
        repository.deductWallet(userId, giftAmount, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("礼物发送成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setPayStatus(payStatus);
        result.addResultData("transaction_id", transactionId);
        result.addResultData("gift_type", giftType);
        result.addResultData("pay_amount", payAmount);
        return result;
    }

    // ==================== DAT009 VIP开通 ====================
    // 外呼：会员认证服务 /internal/dating/member-verify
    // 数据库：INSERT t_vip_order + UPDATE t_user

    private GatewayResult processVipOpen(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        int vipLevel = hasText(context.getVipLevel()) ? Integer.parseInt(context.getVipLevel()) : 1;
        int durationDays = hasText(context.getDurationDays()) ? Integer.parseInt(context.getDurationDays()) : 30;
        BigDecimal amount = new BigDecimal("30.00").multiply(new BigDecimal(vipLevel));

        // 1. 外呼：会员认证服务
        Map<String, Object> verifyResult = fetch(
            "/internal/dating/member-verify",
            "traceId", traceId,
            "userId", userId,
            "vipLevel", String.valueOf(vipLevel),
            "tranCode", "DAT009"
        );
        String verifyStatus = stringValue(verifyResult, "verifyStatus", "VERIFIED");
        String memberLevel = stringValue(verifyResult, "memberLevel", "SILVER");
        String privileges = stringValue(verifyResult, "privileges", "UNLIMITED_LIKE,SUPER_MATCH");
        log.info("traceId={} [外呼] 会员认证结果: verifyStatus={}, memberLevel={}", traceId, verifyStatus, memberLevel);

        // 2. 数据库：INSERT t_vip_order + UPDATE t_user
        repository.insertVipOrder(userId, vipLevel, durationDays, amount, traceId);
        repository.updateUserVipLevel(userId, vipLevel, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("VIP开通成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setVerifyStatus(verifyStatus);
        result.addResultData("vip_level", String.valueOf(vipLevel));
        result.addResultData("member_level", memberLevel);
        result.addResultData("privileges", privileges);
        return result;
    }

    // ==================== DAT010 钱包充值 ====================
    // 外呼：第三方支付服务 /internal/dating/pay-recharge
    // 数据库：INSERT t_recharge_order + UPDATE t_wallet

    private GatewayResult processWalletRecharge(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        BigDecimal amount = hasText(context.getRechargeAmount()) ? new BigDecimal(context.getRechargeAmount()) : new BigDecimal("100.00");
        String payChannel = hasText(context.getPayChannel()) ? context.getPayChannel() : "ALIPAY";

        // 1. 外呼：第三方支付服务
        Map<String, Object> payResult = fetch(
            "/internal/dating/pay-recharge",
            "traceId", traceId,
            "userId", userId,
            "amount", amount.toPlainString(),
            "payChannel", payChannel,
            "tranCode", "DAT010"
        );
        String payStatus = stringValue(payResult, "payStatus", "SUCCESS");
        String transactionId = stringValue(payResult, "transactionId", "TXN_" + System.currentTimeMillis());
        String payAmount = stringValue(payResult, "payAmount", amount.toPlainString());
        log.info("traceId={} [外呼] 第三方支付结果: payStatus={}, transactionId={}", traceId, payStatus, transactionId);

        // 2. 数据库：INSERT t_recharge_order + UPDATE t_wallet
        repository.insertRechargeOrder(userId, amount, payChannel, traceId);
        repository.addWalletBalance(userId, amount, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("钱包充值成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setPayStatus(payStatus);
        result.addResultData("transaction_id", transactionId);
        result.addResultData("pay_channel", payChannel);
        result.addResultData("pay_amount", payAmount);
        return result;
    }

    // ==================== DAT011 上传照片 ====================
    // 外呼：图片存储服务 /internal/dating/storage-upload
    // 数据库：INSERT t_photo + UPDATE t_user_stats

    private GatewayResult processUploadPhoto(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String photoUrl = hasText(context.getPhotoUrl()) ? context.getPhotoUrl() : "/photo/" + System.currentTimeMillis() + ".jpg";
        int isAvatar = hasText(context.getIsAvatar()) ? Integer.parseInt(context.getIsAvatar()) : 0;

        // 1. 外呼：图片存储服务
        Map<String, Object> storageResult = fetch(
            "/internal/dating/storage-upload",
            "traceId", traceId,
            "userId", userId,
            "photoUrl", photoUrl,
            "tranCode", "DAT011"
        );
        String storageUrl = stringValue(storageResult, "storageUrl", photoUrl);
        String fileId = stringValue(storageResult, "fileId", "FILE_" + System.currentTimeMillis());
        String compressResult = stringValue(storageResult, "compressResult", "DONE");
        log.info("traceId={} [外呼] 图片存储结果: storageUrl={}, fileId={}", traceId, storageUrl, fileId);

        // 2. 数据库：INSERT t_photo + UPDATE t_user_stats
        repository.insertPhoto(userId, storageUrl, isAvatar, traceId);
        repository.incrementPhotoCount(userId, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("照片上传成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setStorageUrl(storageUrl);
        result.addResultData("file_id", fileId);
        result.addResultData("compress_result", compressResult);
        return result;
    }

    // ==================== DAT012 举报用户 ====================
    // 外呼：内容审核服务 /internal/dating/content-audit
    // 数据库：INSERT t_report + UPDATE t_user_stats

    private GatewayResult processReportUser(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String targetUserId = hasText(context.getTargetUserId()) ? context.getTargetUserId() : "U10003";
        String reportType = hasText(context.getReportType()) ? context.getReportType() : "HARASSMENT";
        String description = hasText(context.getReportDesc()) ? context.getReportDesc() : "用户行为不当";

        // 1. 外呼：内容审核服务
        Map<String, Object> auditResult = fetch(
            "/internal/dating/content-audit",
            "traceId", traceId,
            "userId", userId,
            "targetUserId", targetUserId,
            "reportType", reportType,
            "tranCode", "DAT012"
        );
        String auditStatus = stringValue(auditResult, "auditResult", "REVIEWING");
        String violationType = stringValue(auditResult, "violationType", reportType);
        String auditScore = stringValue(auditResult, "auditScore", "60");
        log.info("traceId={} [外呼] 内容审核结果: auditResult={}, violationType={}", traceId, auditStatus, violationType);

        // 2. 数据库：INSERT t_report + UPDATE t_user_stats
        repository.insertReport(userId, targetUserId, reportType, description, traceId);
        repository.incrementReportCount(targetUserId, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("举报提交成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setAuditResult(auditStatus);
        result.setViolationType(violationType);
        result.addResultData("audit_score", auditScore);
        return result;
    }

    // ==================== DAT013 拉黑用户 ====================
    // 外呼：关系链服务 /internal/dating/relation-block
    // 数据库：INSERT t_blacklist + UPDATE t_user_stats

    private GatewayResult processBlockUser(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String targetUserId = hasText(context.getTargetUserId()) ? context.getTargetUserId() : "U10003";
        String reason = hasText(context.getBlockReason()) ? context.getBlockReason() : "不想看到";

        // 1. 外呼：关系链服务
        Map<String, Object> relationResult = fetch(
            "/internal/dating/relation-block",
            "traceId", traceId,
            "userId", userId,
            "targetUserId", targetUserId,
            "tranCode", "DAT013"
        );
        String blockStatus = stringValue(relationResult, "blockStatus", "BLOCKED");
        String relationType = stringValue(relationResult, "relationType", "STRANGER");
        String affectedCount = stringValue(relationResult, "affectedCount", "1");
        log.info("traceId={} [外呼] 关系链结果: blockStatus={}, relationType={}", traceId, blockStatus, relationType);

        // 2. 数据库：INSERT t_blacklist + UPDATE t_user_stats
        repository.insertBlacklist(userId, targetUserId, reason, traceId);
        repository.incrementBlockCount(userId, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("拉黑成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setBlockStatus(blockStatus);
        result.addResultData("relation_type", relationType);
        result.addResultData("affected_count", affectedCount);
        return result;
    }

    // ==================== DAT014 活动报名 ====================
    // 外呼：活动管理服务 /internal/dating/event-register
    // 数据库：INSERT t_event_signup + UPDATE t_event

    private GatewayResult processEventSignup(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        long eventId = hasText(context.getEventId()) ? Long.parseLong(context.getEventId()) : 1L;

        // 1. 外呼：活动管理服务
        Map<String, Object> eventResult = fetch(
            "/internal/dating/event-register",
            "traceId", traceId,
            "userId", userId,
            "eventId", String.valueOf(eventId),
            "tranCode", "DAT014"
        );
        String registerStatus = stringValue(eventResult, "registerStatus", "REGISTERED");
        String eventCapacity = stringValue(eventResult, "eventCapacity", "50");
        String remainingSlots = stringValue(eventResult, "remainingSlots", "27");
        log.info("traceId={} [外呼] 活动管理结果: registerStatus={}, remainingSlots={}", traceId, registerStatus, remainingSlots);

        // 2. 数据库：INSERT t_event_signup + UPDATE t_event
        repository.insertEventSignup(eventId, userId, traceId);
        repository.incrementEventParticipants(eventId, traceId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("活动报名成功");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setRegisterStatus(registerStatus);
        result.addResultData("event_id", String.valueOf(eventId));
        result.addResultData("event_capacity", eventCapacity);
        result.addResultData("remaining_slots", remainingSlots);
        return result;
    }

    // ==================== DAT015 通知查询 ====================
    // 外呼：消息中心服务 /internal/dating/message-center
    // 数据库：SELECT t_notification + SELECT t_notify_config

    private GatewayResult processNotifyQuery(GatewayContext context) {
        String traceId = context.getTraceId();
        String userId = context.getUserId();
        String notifyType = hasText(context.getNotifyType()) ? context.getNotifyType() : "";

        // 1. 外呼：消息中心服务
        Map<String, Object> msgResult = fetch(
            "/internal/dating/message-center",
            "traceId", traceId,
            "userId", userId,
            "notifyType", notifyType,
            "tranCode", "DAT015"
        );
        String msgCount = stringValue(msgResult, "msgCount", "5");
        String unreadCount = stringValue(msgResult, "unreadCount", "2");
        String latestMsg = stringValue(msgResult, "latestMsg", "您有新的匹配");
        log.info("traceId={} [外呼] 消息中心结果: msgCount={}, unreadCount={}", traceId, msgCount, unreadCount);

        // 2. 数据库：SELECT t_notification + SELECT t_notify_config
        java.util.List<Map<String, Object>> notifications = repository.findNotifications(userId, notifyType);
        java.util.List<Map<String, Object>> configs = repository.findNotifyConfigs(userId);

        GatewayResult result = new GatewayResult();
        result.setStatus("SUCCESS");
        result.setMessage("通知查询完成");
        result.setSubCallFlag("Y");
        result.setDbFlag("Y");
        result.setMsgCount(msgCount);
        result.setUnreadCount(unreadCount);
        result.addResultData("notification_count", String.valueOf(notifications.size()));
        result.addResultData("config_count", String.valueOf(configs.size()));
        result.addResultData("latest_msg", latestMsg);
        return result;
    }

    // ==================== 外呼辅助方法 ====================

    @SuppressWarnings("unchecked")
    private Map<String, Object> fetch(String path, String... keyValues) {
        String traceId = TraceContext.getTraceId();
        UriComponentsBuilder builder = UriComponentsBuilder
            .fromHttpUrl(variantProperties.getInternalBaseUrl() + path);
        for (int i = 0; i < keyValues.length; i += 2) {
            builder.queryParam(keyValues[i], keyValues[i + 1]);
        }
        String url = builder.toUriString();
        log.info("traceId={} [外呼] HTTP sub-call request: {}", traceId, url);
        try {
            ResponseEntity<Map> entity = restTemplate.getForEntity(url, Map.class);
            Map<String, Object> body = entity.getBody() == null ? Collections.<String, Object>emptyMap() : entity.getBody();
            log.info("traceId={} [外呼] HTTP sub-call response: status={}, body={}", traceId, entity.getStatusCodeValue(), body);
            return body;
        } catch (Exception ex) {
            log.error("traceId={} [外呼] HTTP sub-call failed: url={}, error={}", traceId, url, ex.getMessage());
            return Collections.emptyMap();
        }
    }

    private String stringValue(Map<String, Object> map, String key, String fallback) {
        Object raw = map.get(key);
        return raw == null ? fallback : String.valueOf(raw);
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }
}
