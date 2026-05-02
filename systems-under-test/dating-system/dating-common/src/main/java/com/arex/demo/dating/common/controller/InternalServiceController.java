package com.arex.demo.dating.common.controller;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.arex.demo.dating.common.service.TraceContext;

/**
 * 内部服务控制器 - 模拟 15 个外呼子调用
 * 每个端点模拟一个不同的外部服务，返回不同的业务数据
 * AREX Agent 会拦截这些 HTTP 调用进行录制和回放
 */
@RestController
@RequestMapping("/internal/dating")
public class InternalServiceController {

    private static final Logger log = LoggerFactory.getLogger(InternalServiceController.class);

    // ==================== DAT001 风控校验服务 ====================

    @GetMapping("/risk-verify")
    public Map<String, Object> riskVerify(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "phone", required = false) String phone,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] risk-verify: userId={}, phone={}, tranCode={}", traceId, userId, phone, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        int score = ThreadLocalRandom.current().nextInt(0, 100);
        result.put("riskLevel", score < 70 ? "LOW" : score < 90 ? "MEDIUM" : "HIGH");
        result.put("riskScore", String.valueOf(score));
        result.put("passed", score < 90 ? "true" : "false");
        result.put("service", "risk-verify");
        log.info("traceId={} [外呼模拟] risk-verify response: {}", traceId, result);
        return result;
    }

    // ==================== DAT002 设备指纹服务 ====================

    @GetMapping("/device-fingerprint")
    public Map<String, Object> deviceFingerprint(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] device-fingerprint: userId={}, tranCode={}", traceId, userId, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        String[] deviceTypes = {"IOS", "ANDROID", "WEB", "H5"};
        result.put("deviceId", "DEV_" + System.currentTimeMillis() % 100000);
        result.put("deviceType", deviceTypes[ThreadLocalRandom.current().nextInt(deviceTypes.length)]);
        result.put("riskTag", ThreadLocalRandom.current().nextDouble() > 0.1 ? "NORMAL" : "SUSPICIOUS");
        result.put("service", "device-fingerprint");
        log.info("traceId={} [外呼模拟] device-fingerprint response: {}", traceId, result);
        return result;
    }

    // ==================== DAT003 图片审核服务 ====================

    @GetMapping("/image-audit")
    public Map<String, Object> imageAudit(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] image-audit: userId={}, tranCode={}", traceId, userId, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        int auditScore = ThreadLocalRandom.current().nextInt(60, 100);
        result.put("auditResult", auditScore >= 80 ? "PASS" : "REVIEW");
        result.put("auditScore", String.valueOf(auditScore));
        result.put("rejectReason", auditScore < 80 ? "图片模糊" : "");
        result.put("service", "image-audit");
        log.info("traceId={} [外呼模拟] image-audit response: {}", traceId, result);
        return result;
    }

    // ==================== DAT004 推荐算法服务 ====================

    @GetMapping("/recommend")
    public Map<String, Object> recommend(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "keyword", required = false) String keyword,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] recommend: userId={}, keyword={}, tranCode={}", traceId, userId, keyword, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        String[] algorithms = {"COLLABORATIVE", "CONTENT_BASED", "HYBRID", "DEEP_LEARNING"};
        int score = ThreadLocalRandom.current().nextInt(50, 99);
        result.put("matchScore", String.valueOf(score));
        result.put("algorithm", algorithms[ThreadLocalRandom.current().nextInt(algorithms.length)]);
        result.put("recommendReason", "同城兴趣匹配");
        result.put("service", "recommend");
        log.info("traceId={} [外呼模拟] recommend response: {}", traceId, result);
        return result;
    }

    // ==================== DAT005 消息推送服务 ====================

    @GetMapping("/push-notify")
    public Map<String, Object> pushNotify(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "targetUserId", required = false) String targetUserId,
        @RequestParam(value = "likeType", required = false) String likeType,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] push-notify: userId={}, targetUserId={}, likeType={}, tranCode={}",
            traceId, userId, targetUserId, likeType, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("pushId", "PUSH_" + System.currentTimeMillis());
        result.put("pushStatus", "SENT");
        result.put("channel", ThreadLocalRandom.current().nextDouble() > 0.3 ? "APP" : "SMS");
        result.put("service", "push-notify");
        log.info("traceId={} [外呼模拟] push-notify response: {}", traceId, result);
        return result;
    }

    // ==================== DAT006 匹配算法服务 ====================

    @GetMapping("/match-calc")
    public Map<String, Object> matchCalc(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "gender", required = false) String gender,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] match-calc: userId={}, gender={}, tranCode={}", traceId, userId, gender, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        String[] matchTypes = {"INTEREST", "LOCATION", "SOCIAL", "BEHAVIOR"};
        int score = ThreadLocalRandom.current().nextInt(60, 99);
        result.put("matchScore", String.valueOf(score));
        result.put("matchType", matchTypes[ThreadLocalRandom.current().nextInt(matchTypes.length)]);
        result.put("compatibility", score >= 80 ? "HIGH" : score >= 60 ? "MEDIUM" : "LOW");
        result.put("service", "match-calc");
        log.info("traceId={} [外呼模拟] match-calc response: {}", traceId, result);
        return result;
    }

    // ==================== DAT007 敏感词过滤服务 ====================

    @GetMapping("/sensitive-filter")
    public Map<String, Object> sensitiveFilter(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "content", required = false) String content,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] sensitive-filter: userId={}, tranCode={}", traceId, userId, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        boolean hasSensitive = ThreadLocalRandom.current().nextDouble() < 0.05;
        result.put("filtered", hasSensitive ? "Y" : "N");
        result.put("filterLevel", hasSensitive ? "REPLACE" : "NONE");
        result.put("keywords", hasSensitive ? "敏感词" : "");
        result.put("service", "sensitive-filter");
        log.info("traceId={} [外呼模拟] sensitive-filter response: {}", traceId, result);
        return result;
    }

    // ==================== DAT008 支付网关服务（礼物） ====================

    @GetMapping("/pay-gift")
    public Map<String, Object> payGift(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "targetUserId", required = false) String targetUserId,
        @RequestParam(value = "giftType", required = false) String giftType,
        @RequestParam(value = "giftAmount", required = false) String giftAmount,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] pay-gift: userId={}, targetUserId={}, giftType={}, giftAmount={}, tranCode={}",
            traceId, userId, targetUserId, giftType, giftAmount, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("payStatus", "SUCCESS");
        result.put("transactionId", "TXN_GIFT_" + System.currentTimeMillis());
        result.put("payAmount", giftAmount != null ? giftAmount : "9.90");
        result.put("service", "pay-gift");
        log.info("traceId={} [外呼模拟] pay-gift response: {}", traceId, result);
        return result;
    }

    // ==================== DAT009 会员认证服务 ====================

    @GetMapping("/member-verify")
    public Map<String, Object> memberVerify(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "vipLevel", required = false) String vipLevel,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] member-verify: userId={}, vipLevel={}, tranCode={}",
            traceId, userId, vipLevel, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        String[] levels = {"SILVER", "GOLD", "DIAMOND"};
        int level = vipLevel != null ? Integer.parseInt(vipLevel) : 1;
        result.put("verifyStatus", "VERIFIED");
        result.put("memberLevel", levels[Math.min(level - 1, levels.length - 1)]);
        result.put("privileges", "UNLIMITED_LIKE,SUPER_MATCH,EXCLUSIVE_FILTER");
        result.put("service", "member-verify");
        log.info("traceId={} [外呼模拟] member-verify response: {}", traceId, result);
        return result;
    }

    // ==================== DAT010 第三方支付服务（充值） ====================

    @GetMapping("/pay-recharge")
    public Map<String, Object> payRecharge(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "amount", required = false) String amount,
        @RequestParam(value = "payChannel", required = false) String payChannel,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] pay-recharge: userId={}, amount={}, payChannel={}, tranCode={}",
            traceId, userId, amount, payChannel, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("payStatus", "SUCCESS");
        result.put("transactionId", "TXN_RECHARGE_" + System.currentTimeMillis());
        result.put("payAmount", amount != null ? amount : "100.00");
        result.put("service", "pay-recharge");
        log.info("traceId={} [外呼模拟] pay-recharge response: {}", traceId, result);
        return result;
    }

    // ==================== DAT011 图片存储服务 ====================

    @GetMapping("/storage-upload")
    public Map<String, Object> storageUpload(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "photoUrl", required = false) String photoUrl,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] storage-upload: userId={}, photoUrl={}, tranCode={}",
            traceId, userId, photoUrl, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("storageUrl", "/cdn/photo/" + System.currentTimeMillis() + ".jpg");
        result.put("fileId", "FILE_" + System.currentTimeMillis());
        result.put("compressResult", "DONE");
        result.put("service", "storage-upload");
        log.info("traceId={} [外呼模拟] storage-upload response: {}", traceId, result);
        return result;
    }

    // ==================== DAT012 内容审核服务 ====================

    @GetMapping("/content-audit")
    public Map<String, Object> contentAudit(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "targetUserId", required = false) String targetUserId,
        @RequestParam(value = "reportType", required = false) String reportType,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] content-audit: userId={}, targetUserId={}, reportType={}, tranCode={}",
            traceId, userId, targetUserId, reportType, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("auditResult", "REVIEWING");
        result.put("violationType", reportType != null ? reportType : "UNKNOWN");
        result.put("auditScore", String.valueOf(ThreadLocalRandom.current().nextInt(40, 80)));
        result.put("service", "content-audit");
        log.info("traceId={} [外呼模拟] content-audit response: {}", traceId, result);
        return result;
    }

    // ==================== DAT013 关系链服务 ====================

    @GetMapping("/relation-block")
    public Map<String, Object> relationBlock(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "targetUserId", required = false) String targetUserId,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] relation-block: userId={}, targetUserId={}, tranCode={}",
            traceId, userId, targetUserId, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("blockStatus", "BLOCKED");
        result.put("relationType", "STRANGER");
        result.put("affectedCount", "1");
        result.put("service", "relation-block");
        log.info("traceId={} [外呼模拟] relation-block response: {}", traceId, result);
        return result;
    }

    // ==================== DAT014 活动管理服务 ====================

    @GetMapping("/event-register")
    public Map<String, Object> eventRegister(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "eventId", required = false) String eventId,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] event-register: userId={}, eventId={}, tranCode={}",
            traceId, userId, eventId, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        result.put("registerStatus", "REGISTERED");
        result.put("eventCapacity", "50");
        result.put("remainingSlots", String.valueOf(ThreadLocalRandom.current().nextInt(10, 40)));
        result.put("service", "event-register");
        log.info("traceId={} [外呼模拟] event-register response: {}", traceId, result);
        return result;
    }

    // ==================== DAT015 消息中心服务 ====================

    @GetMapping("/message-center")
    public Map<String, Object> messageCenter(
        @RequestParam(value = "traceId", required = false) String traceId,
        @RequestParam(value = "userId", required = false) String userId,
        @RequestParam(value = "notifyType", required = false) String notifyType,
        @RequestParam(value = "tranCode", required = false) String tranCode) {
        log.info("traceId={} [外呼模拟] message-center: userId={}, notifyType={}, tranCode={}",
            traceId, userId, notifyType, tranCode);
        Map<String, Object> result = new HashMap<String, Object>();
        int msgCount = ThreadLocalRandom.current().nextInt(1, 20);
        int unreadCount = ThreadLocalRandom.current().nextInt(0, Math.max(msgCount, 1));
        result.put("msgCount", String.valueOf(msgCount));
        result.put("unreadCount", String.valueOf(unreadCount));
        result.put("latestMsg", "您有新的匹配通知");
        result.put("service", "message-center");
        log.info("traceId={} [外呼模拟] message-center response: {}", traceId, result);
        return result;
    }
}
