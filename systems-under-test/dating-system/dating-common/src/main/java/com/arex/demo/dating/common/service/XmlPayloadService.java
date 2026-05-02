package com.arex.demo.dating.common.service;

import java.io.StringReader;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ThreadLocalRandom;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import com.arex.demo.dating.common.model.DatingTransactionDefinition;
import com.arex.demo.dating.common.model.GatewayContext;
import com.arex.demo.dating.common.model.GatewayResult;

/**
 * XML 报文解析与构建服务
 * 负责从 XML 请求报文中提取字段，以及构建 XML 响应报文
 */
@Service
public class XmlPayloadService {

    private static final Logger log = LoggerFactory.getLogger(XmlPayloadService.class);

    private static final List<String> TX_FIELDS = Arrays.asList(
        "tran_code", "trs_code", "service_code", "biz_code", "trans_code", "code"
    );

    /**
     * 解析 XML 请求报文，提取关键字段到 GatewayContext
     */
    public GatewayContext parse(String xml) {
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            factory.setNamespaceAware(false);
            factory.setExpandEntityReferences(false);
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document document = builder.parse(new InputSource(new StringReader(xml)));

            GatewayContext context = new GatewayContext();
            context.setRawXml(xml);

            // 解析交易码
            for (String field : TX_FIELDS) {
                String value = textOf(document, field);
                if (hasText(value)) {
                    context.setTranCode(value.trim());
                    context.setRequestField(field);
                    break;
                }
            }

            // 解析 trace_id（18位随机数字），如果请求未传则自动生成
            context.setTraceId(firstNonBlank(
                textOf(document, "trace_id"),
                textOf(document, "traceId"),
                generateTraceId()
            ));

            // 解析交易时间
            context.setTranTime(firstNonBlank(
                textOf(document, "tran_time"),
                textOf(document, "tranTime"),
                String.valueOf(System.currentTimeMillis())
            ));

            // 解析通用字段
            context.setUserId(firstNonBlank(
                textOf(document, "user_id"),
                textOf(document, "userId")
            ));
            context.setTargetUserId(firstNonBlank(
                textOf(document, "target_user_id"),
                textOf(document, "targetUserId")
            ));
            context.setPhone(textOf(document, "phone"));
            context.setGender(textOf(document, "gender"));
            context.setAge(textOf(document, "age"));
            context.setCity(textOf(document, "city"));
            context.setSearchKeyword(textOf(document, "search_keyword"));
            context.setSearchType(textOf(document, "search_type"));
            context.setLikeType(textOf(document, "like_type"));
            context.setMsgContent(textOf(document, "msg_content"));
            context.setMsgType(textOf(document, "msg_type"));
            context.setGiftType(textOf(document, "gift_type"));
            context.setGiftAmount(textOf(document, "gift_amount"));
            context.setVipLevel(textOf(document, "vip_level"));
            context.setDurationDays(textOf(document, "duration_days"));
            context.setRechargeAmount(textOf(document, "recharge_amount"));
            context.setPayChannel(textOf(document, "pay_channel"));
            context.setPhotoUrl(textOf(document, "photo_url"));
            context.setIsAvatar(textOf(document, "is_avatar"));
            context.setReportType(textOf(document, "report_type"));
            context.setReportDesc(textOf(document, "report_desc"));
            context.setBlockReason(textOf(document, "block_reason"));
            context.setEventId(textOf(document, "event_id"));
            context.setNotifyType(textOf(document, "notify_type"));

            log.info("traceId={} Parsed XML request: tranCode={}, userId={}, targetUserId={}",
                context.getTraceId(), context.getTranCode(), context.getUserId(), context.getTargetUserId());

            return context;
        } catch (Exception ex) {
            throw new IllegalArgumentException("invalid xml payload: " + ex.getMessage(), ex);
        }
    }

    /**
     * 构建 XML 响应报文
     */
    public String buildResponseXml(GatewayContext context,
                                   DatingTransactionDefinition definition,
                                   GatewayResult result) {
        StringBuilder builder = new StringBuilder();
        builder.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
        builder.append("<response>");
        append(builder, "tran_code", definition.getCode());
        append(builder, "tran_name", definition.getDisplayName());
        append(builder, "request_field", context.getRequestField());
        append(builder, "trace_id", context.getTraceId());
        append(builder, "tran_time", context.getTranTime());
        append(builder, "status", result.getStatus());
        append(builder, "message", result.getMessage());
        append(builder, "sub_call_flag", result.getSubCallFlag());
        append(builder, "db_flag", result.getDbFlag());

        // 交易特定字段
        if (hasText(result.getRiskLevel())) {
            append(builder, "risk_level", result.getRiskLevel());
        }
        if (hasText(result.getRiskScore())) {
            append(builder, "risk_score", result.getRiskScore());
        }
        if (hasText(result.getAuditResult())) {
            append(builder, "audit_result", result.getAuditResult());
        }
        if (hasText(result.getMatchScore())) {
            append(builder, "match_score", result.getMatchScore());
        }
        if (hasText(result.getFilterLevel())) {
            append(builder, "filter_level", result.getFilterLevel());
        }
        if (hasText(result.getPayStatus())) {
            append(builder, "pay_status", result.getPayStatus());
        }
        if (hasText(result.getVerifyStatus())) {
            append(builder, "verify_status", result.getVerifyStatus());
        }
        if (hasText(result.getStorageUrl())) {
            append(builder, "storage_url", result.getStorageUrl());
        }
        if (hasText(result.getViolationType())) {
            append(builder, "violation_type", result.getViolationType());
        }
        if (hasText(result.getBlockStatus())) {
            append(builder, "block_status", result.getBlockStatus());
        }
        if (hasText(result.getRegisterStatus())) {
            append(builder, "register_status", result.getRegisterStatus());
        }
        if (hasText(result.getMsgCount())) {
            append(builder, "msg_count", result.getMsgCount());
        }
        if (hasText(result.getUnreadCount())) {
            append(builder, "unread_count", result.getUnreadCount());
        }

        // result_data 区域
        if (!result.getResultData().isEmpty()) {
            builder.append("<result_data>");
            for (Map.Entry<String, String> entry : result.getResultData().entrySet()) {
                append(builder, entry.getKey(), entry.getValue());
            }
            builder.append("</result_data>");
        }

        builder.append("</response>");
        return builder.toString();
    }

    /**
     * 生成 18 位随机数字 trace_id
     */
    private String generateTraceId() {
        StringBuilder sb = new StringBuilder(18);
        sb.append(ThreadLocalRandom.current().nextInt(1, 10));
        for (int i = 1; i < 18; i++) {
            sb.append(ThreadLocalRandom.current().nextInt(10));
        }
        return sb.toString();
    }

    private void append(StringBuilder builder, String tagName, String value) {
        builder.append("<").append(tagName).append(">");
        builder.append(escapeXml(value));
        builder.append("</").append(tagName).append(">");
    }

    private String escapeXml(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&apos;");
    }

    private String textOf(Document document, String tagName) {
        NodeList list = document.getElementsByTagName(tagName);
        if (list == null || list.getLength() == 0 || list.item(0) == null || list.item(0).getTextContent() == null) {
            return null;
        }
        return list.item(0).getTextContent();
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }

    private String firstNonBlank(String first, String second) {
        return hasText(first) ? first : second;
    }

    private String firstNonBlank(String first, String second, String third) {
        if (hasText(first)) {
            return first;
        }
        if (hasText(second)) {
            return second;
        }
        return third;
    }
}
