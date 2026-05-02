# 交友系统 (dating-system)

交友平台被测系统，用于 AREX 录制回放平台的功能验证与双发比对演示。

## 项目概述

- **语言**: Java 8
- **框架**: Spring Boot 2.7.18
- **数据库**: MySQL (utf8 编码)
- **通信格式**: XML
- **默认端口**: 28090
- **app.name**: `dating-system`

## 交易码清单（15个）

| 交易码 | 名称 | 外呼子调用 | 数据库操作 |
|--------|------|-----------|-----------|
| DAT001 | 用户注册 | 风控校验服务 `/internal/dating/risk-verify` | INSERT t_user |
| DAT002 | 用户登录 | 设备指纹服务 `/internal/dating/device-fingerprint` | INSERT t_login_log, SELECT t_user |
| DAT003 | 资料更新 | 图片审核服务 `/internal/dating/image-audit` | UPDATE t_user_profile |
| DAT004 | 用户搜索 | 推荐算法服务 `/internal/dating/recommend` | INSERT t_search_history, SELECT t_user |
| DAT005 | 点赞喜欢 | 消息推送服务 `/internal/dating/push-notify` | INSERT t_like_record, UPDATE t_user_stats |
| DAT006 | 匹配推荐 | 匹配算法服务 `/internal/dating/match-calc` | INSERT t_match_record, SELECT t_user |
| DAT007 | 发送消息 | 敏感词过滤服务 `/internal/dating/sensitive-filter` | INSERT t_message, UPDATE t_conversation |
| DAT008 | 送礼物 | 支付网关服务 `/internal/dating/pay-gift` | INSERT t_gift_order, UPDATE t_wallet |
| DAT009 | VIP开通 | 会员认证服务 `/internal/dating/member-verify` | INSERT t_vip_order, UPDATE t_user |
| DAT010 | 钱包充值 | 第三方支付服务 `/internal/dating/pay-recharge` | INSERT t_recharge_order, UPDATE t_wallet |
| DAT011 | 上传照片 | 图片存储服务 `/internal/dating/storage-upload` | INSERT t_photo, UPDATE t_user_stats |
| DAT012 | 举报用户 | 内容审核服务 `/internal/dating/content-audit` | INSERT t_report, UPDATE t_user_stats |
| DAT013 | 拉黑用户 | 关系链服务 `/internal/dating/relation-block` | INSERT t_blacklist, UPDATE t_user_stats |
| DAT014 | 活动报名 | 活动管理服务 `/internal/dating/event-register` | INSERT t_event_signup, UPDATE t_event |
| DAT015 | 通知查询 | 消息中心服务 `/internal/dating/message-center` | SELECT t_notification, SELECT t_notify_config |

## 关键设计

### trace_id 流水号
- 每个交易携带 18 位随机数字 `trace_id`
- 请求未传时自动生成
- 所有外呼子调用和数据库操作均通过 `trace_id` 关联日志
- 通过 `trace_id` 可查询到该交易码的完整链路信息

### 日志系统
- 使用 SLF4J 日志框架
- 所有日志输出均带 `traceId=` 前缀
- 外呼子调用日志标记: `[外呼]`
- 数据库操作日志标记: `DB insert/update/query`
- 可通过 grep `traceId=XXX` 追踪完整交易链路

### XML 请求格式
```xml
<?xml version="1.0" encoding="UTF-8"?>
<request>
  <tran_code>DAT001</tran_code>
  <trace_id>123456789012345678</trace_id>
  <tran_time>2026-04-27 19:30:00</tran_time>
  <user_id>U10001</user_id>
  ... (交易特定字段)
</request>
```

### XML 响应格式
```xml
<?xml version="1.0" encoding="UTF-8"?>
<response>
  <tran_code>DAT001</tran_code>
  <tran_name>用户注册</tran_name>
  <trace_id>123456789012345678</trace_id>
  <tran_time>...</tran_time>
  <status>SUCCESS</status>
  <message>用户注册成功</message>
  <sub_call_flag>Y</sub_call_flag>
  <db_flag>Y</db_flag>
  ... (交易特定结果)
  <result_data>
    <user_id>U20001</user_id>
  </result_data>
</response>
```

## 快速启动

### 1. 创建数据库
```bash
mysql -u root -proot123 -e "CREATE DATABASE IF NOT EXISTS dating_system DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"
```

### 2. 编译
```bash
cd dating-system
mvn clean package -DskipTests
```

### 3. 启动（默认 SAT 模式）
```bash
java -Dapp.name=dating-system -jar dating-app/target/dating-app-1.0.0-SNAPSHOT.jar
```

### 4. 启动（UAT 模式，不同端口）
```bash
DATING_SERVER_PORT=28091 DATING_VARIANT_ID=UAT DATING_COMPARE_HINT=UAT_TARGET \
  DATING_DB_NAME=dating_system_uat \
  java -Dapp.name=dating-system -jar dating-app/target/dating-app-1.0.0-SNAPSHOT.jar
```

### 5. 测试
```bash
bash send_samples.sh
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| DATING_SERVER_PORT | 28090 | 服务端口 |
| DATING_DB_HOST | 127.0.0.1 | 数据库主机 |
| DATING_DB_PORT | 3306 | 数据库端口 |
| DATING_DB_NAME | dating_system | 数据库名 |
| DATING_DB_USER | root | 数据库用户 |
| DATING_DB_PASSWORD | root123 | 数据库密码 |
| DATING_VARIANT_ID | SAT | 变体标识 |
| DATING_COMPARE_HINT | SAT_BASELINE | 比对提示 |

## 数据库表

共 20 张表：t_user, t_user_profile, t_user_stats, t_login_log, t_search_history, t_like_record, t_match_record, t_message, t_conversation, t_gift_order, t_wallet, t_vip_order, t_recharge_order, t_photo, t_report, t_blacklist, t_event, t_event_signup, t_notification, t_notify_config

## 录制回放说明

- **入口**: POST `/api/dating/service` (XML 格式)
- **子调用**: GET `/internal/dating/*` (15 个端点)
- **数据库**: 通过 JdbcTemplate 操作 MySQL
- **启动参数**: `-Dapp.name=dating-system`（用于 AREX Agent 定位）
