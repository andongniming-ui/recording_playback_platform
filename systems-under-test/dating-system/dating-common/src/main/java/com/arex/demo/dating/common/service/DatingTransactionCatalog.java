package com.arex.demo.dating.common.service;

import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.stereotype.Component;

import com.arex.demo.dating.common.model.DatingTransactionDefinition;

/**
 * 交友系统交易码目录 - 注册全部 15 个交易码
 * 每个交易码拥有不同的外呼路径（子调用）和数据库操作
 */
@Component
public class DatingTransactionCatalog {

    private final Map<String, DatingTransactionDefinition> definitions = new LinkedHashMap<String, DatingTransactionDefinition>();

    public DatingTransactionCatalog() {
        // 1. DAT001 - 用户注册：外呼→风控校验，DB→INSERT t_user
        register("DAT001", "tran_code", "用户注册",
            "/internal/dating/risk-verify",
            "新用户注册，调用风控校验服务，写入用户表");

        // 2. DAT002 - 用户登录：外呼→设备指纹，DB→INSERT t_login_log + SELECT t_user
        register("DAT002", "tran_code", "用户登录",
            "/internal/dating/device-fingerprint",
            "用户登录，调用设备指纹服务，记录登录日志并查询用户信息");

        // 3. DAT003 - 资料更新：外呼→图片审核，DB→UPDATE t_user_profile
        register("DAT003", "tran_code", "资料更新",
            "/internal/dating/image-audit",
            "更新用户资料，调用图片审核服务，修改资料表");

        // 4. DAT004 - 用户搜索：外呼→推荐算法，DB→INSERT t_search_history + SELECT t_user
        register("DAT004", "tran_code", "用户搜索",
            "/internal/dating/recommend",
            "搜索用户，调用推荐算法服务，记录搜索历史并查询用户");

        // 5. DAT005 - 点赞喜欢：外呼→消息推送，DB→INSERT t_like_record + UPDATE t_user_stats
        register("DAT005", "tran_code", "点赞喜欢",
            "/internal/dating/push-notify",
            "点赞喜欢，调用消息推送服务，记录点赞并更新统计");

        // 6. DAT006 - 匹配推荐：外呼→匹配算法，DB→INSERT t_match_record + SELECT t_user
        register("DAT006", "tran_code", "匹配推荐",
            "/internal/dating/match-calc",
            "匹配推荐，调用匹配算法服务，记录匹配并查询用户");

        // 7. DAT007 - 发送消息：外呼→敏感词过滤，DB→INSERT t_message + UPDATE t_conversation
        register("DAT007", "tran_code", "发送消息",
            "/internal/dating/sensitive-filter",
            "发送消息，调用敏感词过滤服务，记录消息并更新会话");

        // 8. DAT008 - 送礼物：外呼→支付网关，DB→INSERT t_gift_order + UPDATE t_wallet
        register("DAT008", "tran_code", "送礼物",
            "/internal/dating/pay-gift",
            "送礼物，调用支付网关服务，记录订单并扣减钱包");

        // 9. DAT009 - VIP开通：外呼→会员认证，DB→INSERT t_vip_order + UPDATE t_user
        register("DAT009", "tran_code", "VIP开通",
            "/internal/dating/member-verify",
            "VIP开通，调用会员认证服务，记录VIP订单并升级用户等级");

        // 10. DAT010 - 钱包充值：外呼→第三方支付，DB→INSERT t_recharge_order + UPDATE t_wallet
        register("DAT010", "tran_code", "钱包充值",
            "/internal/dating/pay-recharge",
            "钱包充值，调用第三方支付服务，记录充值订单并更新钱包");

        // 11. DAT011 - 上传照片：外呼→图片存储，DB→INSERT t_photo + UPDATE t_user_stats
        register("DAT011", "tran_code", "上传照片",
            "/internal/dating/storage-upload",
            "上传照片，调用图片存储服务，记录照片并更新统计");

        // 12. DAT012 - 举报用户：外呼→内容审核，DB→INSERT t_report + UPDATE t_user_stats
        register("DAT012", "tran_code", "举报用户",
            "/internal/dating/content-audit",
            "举报用户，调用内容审核服务，记录举报并更新统计");

        // 13. DAT013 - 拉黑用户：外呼→关系链，DB→INSERT t_blacklist + UPDATE t_user_stats
        register("DAT013", "tran_code", "拉黑用户",
            "/internal/dating/relation-block",
            "拉黑用户，调用关系链服务，记录黑名单并更新统计");

        // 14. DAT014 - 活动报名：外呼→活动管理，DB→INSERT t_event_signup + UPDATE t_event
        register("DAT014", "tran_code", "活动报名",
            "/internal/dating/event-register",
            "活动报名，调用活动管理服务，记录报名并更新活动人数");

        // 15. DAT015 - 通知查询：外呼→消息中心，DB→SELECT t_notification + SELECT t_notify_config
        register("DAT015", "tran_code", "通知查询",
            "/internal/dating/message-center",
            "通知查询，调用消息中心服务，查询通知及配置");
    }

    public DatingTransactionDefinition find(String code) {
        return definitions.get(code);
    }

    public Collection<DatingTransactionDefinition> all() {
        return definitions.values();
    }

    private void register(String code, String requestField, String displayName,
                          String subCallPath, String description) {
        definitions.put(code, new DatingTransactionDefinition(code, requestField, displayName, subCallPath, description));
    }
}
