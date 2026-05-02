package com.arex.demo.dating.common.repository;

import java.math.BigDecimal;
import java.util.Collections;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import com.arex.demo.dating.common.service.TraceContext;

/**
 * 交友系统数据仓库 - 封装全部 15 个交易的数据库操作
 * 每个交易码的数据库操作均不相同，所有操作通过 trace_id 关联日志
 */
@Repository
public class DatingDataRepository {

    private static final Logger log = LoggerFactory.getLogger(DatingDataRepository.class);

    private final JdbcTemplate jdbcTemplate;

    public DatingDataRepository(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    // ==================== DAT001 用户注册：INSERT t_user ====================

    public int insertUser(String userId, String nickName, String gender, int age,
                          String city, String phone, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_user(user_id, nick_name, gender, age, city, phone, vip_level, status, trace_id) " +
                "VALUES(?, ?, ?, ?, ?, ?, 0, 'ACTIVE', ?)",
            userId, nickName, gender, age, city, phone, traceId
        );
        log.info("traceId={} DB insert insertUser: userId={}, nickName={}, affectedRows={}",
            traId, userId, nickName, affected);
        return affected;
    }

    // ==================== DAT002 用户登录：INSERT t_login_log + SELECT t_user ====================

    public int insertLoginLog(String userId, String loginIp, String deviceInfo, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_login_log(user_id, login_ip, device_info, trace_id) VALUES(?, ?, ?, ?)",
            userId, loginIp, deviceInfo, traceId
        );
        log.info("traceId={} DB insert insertLoginLog: userId={}, affectedRows={}", traId, userId, affected);
        return affected;
    }

    public Map<String, Object> findUser(String userId) {
        return first("findUser", "SELECT * FROM t_user WHERE user_id = ?", userId);
    }

    // ==================== DAT003 资料更新：UPDATE t_user_profile ====================

    public int updateUserProfile(String userId, String bio, String occupation,
                                 String incomeRange, String education, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_user_profile SET bio = ?, occupation = ?, income_range = ?, education = ?, trace_id = ? " +
                "WHERE user_id = ?",
            bio, occupation, incomeRange, education, traceId, userId
        );
        log.info("traceId={} DB update updateUserProfile: userId={}, affectedRows={}", traId, userId, affected);
        return affected;
    }

    // ==================== DAT004 用户搜索：INSERT t_search_history + SELECT t_user ====================

    public int insertSearchHistory(String userId, String searchType, String keyword,
                                   int resultCount, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_search_history(user_id, search_type, keyword, result_count, trace_id) " +
                "VALUES(?, ?, ?, ?, ?)",
            userId, searchType, keyword, resultCount, traceId
        );
        log.info("traceId={} DB insert insertSearchHistory: userId={}, keyword={}, affectedRows={}",
            traId, userId, keyword, affected);
        return affected;
    }

    public List<Map<String, Object>> searchUsers(String city, String gender) {
        String traId = TraceContext.getTraceId();
        log.info("traceId={} DB query searchUsers: city={}, gender={}", traId, city, gender);
        List<Map<String, Object>> rows;
        if (hasText(city) && hasText(gender)) {
            rows = jdbcTemplate.queryForList(
                "SELECT * FROM t_user WHERE city = ? AND gender = ? AND status = 'ACTIVE'", city, gender);
        } else if (hasText(city)) {
            rows = jdbcTemplate.queryForList(
                "SELECT * FROM t_user WHERE city = ? AND status = 'ACTIVE'", city);
        } else {
            rows = jdbcTemplate.queryForList(
                "SELECT * FROM t_user WHERE status = 'ACTIVE' LIMIT 10");
        }
        log.info("traceId={} DB query searchUsers result: count={}", traId, rows.size());
        return rows;
    }

    // ==================== DAT005 点赞喜欢：INSERT t_like_record + UPDATE t_user_stats ====================

    public int insertLikeRecord(String fromUserId, String toUserId, String likeType, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_like_record(from_user_id, to_user_id, like_type, trace_id) VALUES(?, ?, ?, ?)",
            fromUserId, toUserId, likeType, traceId
        );
        log.info("traceId={} DB insert insertLikeRecord: from={}, to={}, affectedRows={}",
            traId, fromUserId, toUserId, affected);
        return affected;
    }

    public int incrementLikeCount(String userId, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_user_stats SET like_count = like_count + 1, trace_id = ? WHERE user_id = ?",
            traceId, userId
        );
        log.info("traceId={} DB update incrementLikeCount: userId={}, affectedRows={}", traId, userId, affected);
        return affected;
    }

    public int incrementLikedCount(String userId, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_user_stats SET liked_count = liked_count + 1, trace_id = ? WHERE user_id = ?",
            traceId, userId
        );
        log.info("traceId={} DB update incrementLikedCount: userId={}, affectedRows={}", traId, userId, affected);
        return affected;
    }

    // ==================== DAT006 匹配推荐：INSERT t_match_record + SELECT t_user ====================

    public int insertMatchRecord(String userIdA, String userIdB, int matchScore,
                                 String matchSource, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_match_record(user_id_a, user_id_b, match_score, match_source, trace_id) " +
                "VALUES(?, ?, ?, ?, ?)",
            userIdA, userIdB, matchScore, matchSource, traceId
        );
        log.info("traceId={} DB insert insertMatchRecord: userA={}, userB={}, score={}, affectedRows={}",
            traId, userIdA, userIdB, matchScore, affected);
        return affected;
    }

    public List<Map<String, Object>> findPotentialMatches(String userId, String gender) {
        String traId = TraceContext.getTraceId();
        String oppositeGender = "M".equals(gender) ? "F" : "M";
        log.info("traceId={} DB query findPotentialMatches: userId={}, oppositeGender={}", traId, userId, oppositeGender);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(
            "SELECT * FROM t_user WHERE gender = ? AND user_id != ? AND status = 'ACTIVE' LIMIT 5",
            oppositeGender, userId);
        log.info("traceId={} DB query findPotentialMatches result: count={}", traId, rows.size());
        return rows;
    }

    // ==================== DAT007 发送消息：INSERT t_message + UPDATE t_conversation ====================

    public int insertMessage(String senderId, String receiverId, String content,
                             String msgType, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_message(sender_id, receiver_id, content, msg_type, trace_id) VALUES(?, ?, ?, ?, ?)",
            senderId, receiverId, content, msgType, traceId
        );
        log.info("traceId={} DB insert insertMessage: sender={}, receiver={}, affectedRows={}",
            traId, senderId, receiverId, affected);
        return affected;
    }

    public int updateConversation(String userIdA, String userIdB, int msgCount, String traceId) {
        String traId = TraceContext.getTraceId();
        // 先查是否存在会话
        List<Map<String, Object>> existing = jdbcTemplate.queryForList(
            "SELECT id FROM t_conversation WHERE (user_id_a = ? AND user_id_b = ?) OR (user_id_a = ? AND user_id_b = ?)",
            userIdA, userIdB, userIdB, userIdA);
        int affected;
        if (existing.isEmpty()) {
            affected = jdbcTemplate.update(
                "INSERT INTO t_conversation(user_id_a, user_id_b, msg_count, trace_id) VALUES(?, ?, ?, ?)",
                userIdA, userIdB, msgCount, traceId);
        } else {
            affected = jdbcTemplate.update(
                "UPDATE t_conversation SET msg_count = msg_count + 1, trace_id = ? " +
                    "WHERE (user_id_a = ? AND user_id_b = ?) OR (user_id_a = ? AND user_id_b = ?)",
                traceId, userIdA, userIdB, userIdB, userIdA);
        }
        log.info("traceId={} DB update updateConversation: userA={}, userB={}, affectedRows={}",
            traId, userIdA, userIdB, affected);
        return affected;
    }

    // ==================== DAT008 送礼物：INSERT t_gift_order + UPDATE t_wallet ====================

    public int insertGiftOrder(String fromUserId, String toUserId, String giftType,
                               BigDecimal giftAmount, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_gift_order(from_user_id, to_user_id, gift_type, gift_amount, trace_id) " +
                "VALUES(?, ?, ?, ?, ?)",
            fromUserId, toUserId, giftType, giftAmount, traceId
        );
        log.info("traceId={} DB insert insertGiftOrder: from={}, to={}, amount={}, affectedRows={}",
            traId, fromUserId, toUserId, giftAmount, affected);
        return affected;
    }

    public int deductWallet(String userId, BigDecimal amount, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_wallet SET balance = balance - ?, total_consume = total_consume + ?, trace_id = ? " +
                "WHERE user_id = ? AND balance >= ?",
            amount, amount, traceId, userId, amount
        );
        log.info("traceId={} DB update deductWallet: userId={}, amount={}, affectedRows={}",
            traId, userId, amount, affected);
        return affected;
    }

    // ==================== DAT009 VIP开通：INSERT t_vip_order + UPDATE t_user ====================

    public int insertVipOrder(String userId, int vipLevel, int durationDays,
                              BigDecimal amount, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_vip_order(user_id, vip_level, duration_days, amount, trace_id) VALUES(?, ?, ?, ?, ?)",
            userId, vipLevel, durationDays, amount, traceId
        );
        log.info("traceId={} DB insert insertVipOrder: userId={}, vipLevel={}, affectedRows={}",
            traId, userId, vipLevel, affected);
        return affected;
    }

    public int updateUserVipLevel(String userId, int vipLevel, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_user SET vip_level = ?, trace_id = ? WHERE user_id = ?",
            vipLevel, traceId, userId
        );
        log.info("traceId={} DB update updateUserVipLevel: userId={}, vipLevel={}, affectedRows={}",
            traId, userId, vipLevel, affected);
        return affected;
    }

    // ==================== DAT010 钱包充值：INSERT t_recharge_order + UPDATE t_wallet ====================

    public int insertRechargeOrder(String userId, BigDecimal amount, String payChannel, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_recharge_order(user_id, amount, pay_channel, trace_id) VALUES(?, ?, ?, ?)",
            userId, amount, payChannel, traceId
        );
        log.info("traceId={} DB insert insertRechargeOrder: userId={}, amount={}, affectedRows={}",
            traId, userId, amount, affected);
        return affected;
    }

    public int addWalletBalance(String userId, BigDecimal amount, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_wallet SET balance = balance + ?, total_recharge = total_recharge + ?, trace_id = ? " +
                "WHERE user_id = ?",
            amount, amount, traceId, userId
        );
        log.info("traceId={} DB update addWalletBalance: userId={}, amount={}, affectedRows={}",
            traId, userId, amount, affected);
        return affected;
    }

    // ==================== DAT011 上传照片：INSERT t_photo + UPDATE t_user_stats ====================

    public int insertPhoto(String userId, String photoUrl, int isAvatar, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_photo(user_id, photo_url, is_avatar, trace_id) VALUES(?, ?, ?, ?)",
            userId, photoUrl, isAvatar, traceId
        );
        log.info("traceId={} DB insert insertPhoto: userId={}, isAvatar={}, affectedRows={}",
            traId, userId, isAvatar, affected);
        return affected;
    }

    public int incrementPhotoCount(String userId, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_user_stats SET photo_count = photo_count + 1, trace_id = ? WHERE user_id = ?",
            traceId, userId
        );
        log.info("traceId={} DB update incrementPhotoCount: userId={}, affectedRows={}", traId, userId, affected);
        return affected;
    }

    // ==================== DAT012 举报用户：INSERT t_report + UPDATE t_user_stats ====================

    public int insertReport(String reporterId, String reportedId, String reportType,
                            String description, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_report(reporter_id, reported_id, report_type, description, trace_id) " +
                "VALUES(?, ?, ?, ?, ?)",
            reporterId, reportedId, reportType, description, traceId
        );
        log.info("traceId={} DB insert insertReport: reporter={}, reported={}, affectedRows={}",
            traId, reporterId, reportedId, affected);
        return affected;
    }

    public int incrementReportCount(String userId, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_user_stats SET report_count = report_count + 1, trace_id = ? WHERE user_id = ?",
            traceId, userId
        );
        log.info("traceId={} DB update incrementReportCount: userId={}, affectedRows={}", traId, userId, affected);
        return affected;
    }

    // ==================== DAT013 拉黑用户：INSERT t_blacklist + UPDATE t_user_stats ====================

    public int insertBlacklist(String userId, String blockedUserId, String reason, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_blacklist(user_id, blocked_user_id, reason, trace_id) VALUES(?, ?, ?, ?)",
            userId, blockedUserId, reason, traceId
        );
        log.info("traceId={} DB insert insertBlacklist: user={}, blocked={}, affectedRows={}",
            traId, userId, blockedUserId, affected);
        return affected;
    }

    public int incrementBlockCount(String userId, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_user_stats SET block_count = block_count + 1, trace_id = ? WHERE user_id = ?",
            traceId, userId
        );
        log.info("traceId={} DB update incrementBlockCount: userId={}, affectedRows={}", traId, userId, affected);
        return affected;
    }

    // ==================== DAT014 活动报名：INSERT t_event_signup + UPDATE t_event ====================

    public int insertEventSignup(long eventId, String userId, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "INSERT INTO t_event_signup(event_id, user_id, trace_id) VALUES(?, ?, ?)",
            eventId, userId, traceId
        );
        log.info("traceId={} DB insert insertEventSignup: eventId={}, userId={}, affectedRows={}",
            traId, eventId, userId, affected);
        return affected;
    }

    public int incrementEventParticipants(long eventId, String traceId) {
        String traId = TraceContext.getTraceId();
        int affected = jdbcTemplate.update(
            "UPDATE t_event SET current_participants = current_participants + 1, trace_id = ? WHERE id = ?",
            traceId, eventId
        );
        log.info("traceId={} DB update incrementEventParticipants: eventId={}, affectedRows={}",
            traId, eventId, affected);
        return affected;
    }

    public Map<String, Object> findEvent(long eventId) {
        return first("findEvent", "SELECT * FROM t_event WHERE id = ?", eventId);
    }

    // ==================== DAT015 通知查询：SELECT t_notification + SELECT t_notify_config ====================

    public List<Map<String, Object>> findNotifications(String userId, String notifyType) {
        String traId = TraceContext.getTraceId();
        log.info("traceId={} DB query findNotifications: userId={}, notifyType={}", traId, userId, notifyType);
        List<Map<String, Object>> rows;
        if (hasText(notifyType)) {
            rows = jdbcTemplate.queryForList(
                "SELECT * FROM t_notification WHERE user_id = ? AND notify_type = ? ORDER BY created_at DESC LIMIT 20",
                userId, notifyType);
        } else {
            rows = jdbcTemplate.queryForList(
                "SELECT * FROM t_notification WHERE user_id = ? ORDER BY created_at DESC LIMIT 20", userId);
        }
        log.info("traceId={} DB query findNotifications result: count={}", traId, rows.size());
        return rows;
    }

    public List<Map<String, Object>> findNotifyConfigs(String userId) {
        String traId = TraceContext.getTraceId();
        log.info("traceId={} DB query findNotifyConfigs: userId={}", traId, userId);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(
            "SELECT * FROM t_notify_config WHERE user_id = ?", userId);
        log.info("traceId={} DB query findNotifyConfigs result: count={}", traId, rows.size());
        return rows;
    }

    // ==================== 通用辅助方法 ====================

    public Map<String, Object> findWallet(String userId) {
        return first("findWallet", "SELECT * FROM t_wallet WHERE user_id = ?", userId);
    }

    public Map<String, Object> findUserStats(String userId) {
        return first("findUserStats", "SELECT * FROM t_user_stats WHERE user_id = ?", userId);
    }

    private Map<String, Object> first(String operation, String sql, Object arg) {
        String traId = TraceContext.getTraceId();
        log.info("traceId={} DB query {}: sql={}, arg={}", traId, operation, sql, arg);
        List<Map<String, Object>> rows = jdbcTemplate.queryForList(sql, arg);
        Map<String, Object> row = rows.isEmpty() ? Collections.<String, Object>emptyMap() : rows.get(0);
        log.info("traceId={} DB query {} result: {}", traId, operation, row);
        return row;
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }
}
