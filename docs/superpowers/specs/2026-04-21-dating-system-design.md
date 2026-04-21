# 婚恋交友系统设计文档

**日期：** 2026-04-21
**技术栈：** Java JDK8 + Spring Boot + MySQL + MyBatis + XML 请求
**目标：** 为 AREX Recorder 提供一套婚恋交友场景的双系统被测样例，支持录制回放比对

---

## 一、整体架构

### 目录结构

```
arex-recorder/
└── dating/
    ├── dating-system-a/          # 基线系统，端口 8083
    │   ├── pom.xml
    │   ├── src/main/java/com/arex/demo/dating/
    │   │   ├── DatingSystemAApplication.java
    │   │   ├── filter/TraceFilter.java
    │   │   ├── context/TraceContext.java
    │   │   ├── controller/GatewayController.java
    │   │   ├── router/TransactionRouter.java
    │   │   ├── handler/          # 30个 Handler，每个交易码一个
    │   │   ├── service/          # 业务逻辑
    │   │   ├── repository/       # MyBatis Mapper
    │   │   ├── mock/             # 内嵌 MockServer（模拟外呼）
    │   │   ├── logger/TraceLogger.java
    │   │   └── model/            # 请求/响应/实体模型
    │   ├── src/main/resources/
    │   │   ├── application.yml
    │   │   ├── mapper/           # MyBatis XML
    │   │   └── logback.xml
    │   └── start.sh
    ├── dating-system-b/          # 比对系统，端口 8084，结构与 a 相同
    │   └── ...（代码与 a 几乎相同，差异在 6 个 Handler 的具体实现）
    ├── postman/
    │   ├── dating-systems.postman_collection.json
    │   ├── dating-system-a.postman_environment.json
    │   └── dating-system-b.postman_environment.json
    ├── create_databases.sql      # 建库建表 + 种子数据
    └── README.md
```

### 请求链路

```
HTTP POST /api/dating/service  (Content-Type: application/xml)
  → TraceFilter
      ├── 生成 18 位流水号，注入 TraceContext（ThreadLocal）
      └── 记录请求开始时间
  → GatewayController
      ├── 解析 XML 请求体
      └── 提取 trans_code / service_code / biz_code
  → TransactionRouter
      └── 按 trans_code 找到对应 Handler
  → XxxHandler.execute()
      ├── 查询/写入数据库（通过 Repository，TraceLogger 自动记录）
      ├── 调用外部服务（通过 RestTemplate，TraceLogger 自动记录）
      └── 构造 XML 响应
  → TraceFilter
      └── 记录总耗时，写日志文件
```

### 两套系统隔离边界

| 维度 | System-A | System-B |
|------|---------|---------|
| 包名 | `com.arex.demo.dating` | `com.arex.demo.dating` |
| 端口 | 8083 | 8084 |
| MockServer 端口 | 9083 | 9084 |
| 数据库 | `dating_a` | `dating_b` |
| 日志文件 | `dating-system-a.log` | `dating-system-b.log` |

与 didi 系统完全独立，无任何代码/配置共享，包名、端口、数据库均不重叠。

---

## 二、30 个交易码清单

### 交易码字段

请求 XML 中以下任意字段均可识别交易码：
- `trans_code`
- `service_code`
- `biz_code`

### 复杂交易（15个）— 含数据库操作 + 外呼子调用

| 交易码 | 业务名称 | 数据库操作 | 外呼子调用 |
|--------|---------|-----------|-----------|
| `dating000001` | 用户注册 | INSERT user | 实名认证服务 |
| `dating000002` | 实名认证提交 | UPDATE user | 实名认证服务 |
| `dating000003` | 会员开通 | INSERT order_info, UPDATE user | 支付服务 |
| `dating000004` | 会员续费 | INSERT order_info, UPDATE user | 支付服务 |
| `dating000005` | 发起匹配请求 | INSERT match_request | 短信通知服务 |
| `dating000006` | 确认匹配 | UPDATE match_request, INSERT chat_session | 短信通知服务 |
| `dating000007` | 发送私信 | INSERT message | 短信通知服务 |
| `dating000008` | 预约线下约会 | INSERT appointment | 短信通知服务 |
| `dating000009` | 约会确认 | UPDATE appointment | 短信通知服务 |
| `dating000010` | 约会取消 | UPDATE appointment | 短信通知服务 |
| `dating000011` | 提交约会评价 | INSERT review, UPDATE user_score | 短信通知服务 |
| `dating000012` | 购买超级喜欢 | INSERT order_info | 支付服务 |
| `dating000013` | 举报用户 | INSERT report | 短信通知服务（通知审核员）|
| `dating000014` | 注销账户 | UPDATE user（软删除）| 短信通知服务 |
| `dating000015` | 提现佣金 | INSERT withdraw_order | 支付服务 |

### 轻量交易（15个）— 数据库查询或直接返回

| 交易码 | 业务名称 |
|--------|---------|
| `dating000016` | 查询用户资料 |
| `dating000017` | 查询匹配列表 |
| `dating000018` | 查询会员权益 |
| `dating000019` | 查询约会记录 |
| `dating000020` | 查询消息列表 |
| `dating000021` | 查询评价记录 |
| `dating000022` | 查询附近用户 |
| `dating000023` | 查询黑名单 |
| `dating000024` | 查询充值记录 |
| `dating000025` | 查询超级喜欢余量 |
| `dating000026` | 修改用户偏好 |
| `dating000027` | 设置隐私权限 |
| `dating000028` | 查询系统公告 |
| `dating000029` | 查询活动列表 |
| `dating000030` | 提交意见反馈 |

---

## 三、数据模型

### 业务表

```sql
-- 用户表
CREATE TABLE user (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_no     VARCHAR(32) NOT NULL UNIQUE,   -- 用户编号
    name        VARCHAR(64),
    gender      TINYINT,                        -- 1男 2女
    age         INT,
    city        VARCHAR(64),
    phone       VARCHAR(20),
    id_card     VARCHAR(18),
    verified    TINYINT DEFAULT 0,              -- 实名认证状态
    member_level TINYINT DEFAULT 0,             -- 0普通 1普通会员 2超级会员
    member_expire DATETIME,
    score       INT DEFAULT 0,                  -- 信用评分
    status      TINYINT DEFAULT 1,              -- 1正常 0注销
    created_at  DATETIME,
    updated_at  DATETIME
);

-- 匹配请求表
CREATE TABLE match_request (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_user_no VARCHAR(32),
    to_user_no   VARCHAR(32),
    status       TINYINT DEFAULT 0,   -- 0待确认 1已确认 2已拒绝
    created_at   DATETIME,
    updated_at   DATETIME
);

-- 聊天会话表
CREATE TABLE chat_session (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_no  VARCHAR(32) NOT NULL UNIQUE,
    user_a      VARCHAR(32),
    user_b      VARCHAR(32),
    status      TINYINT DEFAULT 1,
    created_at  DATETIME
);

-- 消息表
CREATE TABLE message (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    session_no  VARCHAR(32),
    sender_no   VARCHAR(32),
    content     TEXT,
    created_at  DATETIME
);

-- 约会预约表
CREATE TABLE appointment (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    appt_no     VARCHAR(32) NOT NULL UNIQUE,
    user_a      VARCHAR(32),
    user_b      VARCHAR(32),
    appt_time   DATETIME,
    location    VARCHAR(128),
    status      TINYINT DEFAULT 0,    -- 0待确认 1已确认 2已取消 3已完成
    created_at  DATETIME,
    updated_at  DATETIME
);

-- 评价表
CREATE TABLE review (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    appt_no      VARCHAR(32),
    reviewer_no  VARCHAR(32),
    reviewee_no  VARCHAR(32),
    score        INT,
    content      VARCHAR(512),
    created_at   DATETIME
);

-- 订单表
CREATE TABLE order_info (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no    VARCHAR(32) NOT NULL UNIQUE,
    user_no     VARCHAR(32),
    order_type  VARCHAR(32),    -- MEMBER / SUPER_LIKE / WITHDRAW
    amount      DECIMAL(10,2),
    status      TINYINT DEFAULT 0,   -- 0处理中 1成功 2失败
    created_at  DATETIME,
    updated_at  DATETIME
);

-- 举报表
CREATE TABLE report (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    reporter_no  VARCHAR(32),
    reported_no  VARCHAR(32),
    reason       VARCHAR(256),
    status       TINYINT DEFAULT 0,   -- 0待处理 1已处理
    created_at   DATETIME
);

-- 提现表
CREATE TABLE withdraw_order (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    withdraw_no VARCHAR(32) NOT NULL UNIQUE,
    user_no     VARCHAR(32),
    amount      DECIMAL(10,2),
    status      TINYINT DEFAULT 0,
    created_at  DATETIME,
    updated_at  DATETIME
);
```

### 日志表

```sql
-- 交易流水日志表
CREATE TABLE trace_log (
    id          BIGINT PRIMARY KEY AUTO_INCREMENT,
    trace_no    VARCHAR(18) NOT NULL,   -- 18位流水号
    trans_code  VARCHAR(32),
    log_type    VARCHAR(20),            -- DB_SELECT / DB_INSERT / DB_UPDATE / DB_DELETE / HTTP_CALL
    operation   VARCHAR(128),           -- 操作描述，如 "INSERT user" / "CALL sms-service"
    request     TEXT,                   -- 入参摘要
    response    TEXT,                   -- 出参摘要
    elapsed_ms  INT,                    -- 耗时（毫秒）
    status      VARCHAR(10),            -- SUCCESS / FAIL
    created_at  DATETIME
);

CREATE INDEX idx_trace_no ON trace_log(trace_no);
```

### 数据库差异（用于触发查询结果差异）

- `dating_a`：标准种子数据
- `dating_b`：`user` 表多 2 条附近用户数据（触发 `dating000022` 差异）；`order_info` 表多 1 条历史充值记录（触发 `dating000024` 差异）

---

## 四、两套系统的差异设计

以下 6 个交易码在 system-a 和 system-b 之间预埋可见差异：

### 字段值差异

| 交易码 | 交易名称 | 差异说明 |
|--------|---------|---------|
| `dating000003` | 会员开通 | system-b 返回的 `memberExpire` 字段比 system-a 多 1 天 |
| `dating000018` | 查询会员权益 | system-b 的 `benefitList` 多一项 `"专属客服"` |

### 子调用差异

| 交易码 | 交易名称 | 差异说明 |
|--------|---------|---------|
| `dating000006` | 确认匹配 | system-b 调用短信服务 2 次（双方各一条），system-a 只调用 1 次 |
| `dating000011` | 提交约会评价 | system-b 跳过短信通知子调用，system-a 正常调用 |

### 数据库行为差异

| 交易码 | 交易名称 | 差异说明 |
|--------|---------|---------|
| `dating000022` | 查询附近用户 | system-b 种子数据多 2 个用户，返回列表长度不同 |
| `dating000024` | 查询充值记录 | system-b 种子数据多 1 笔历史订单，金额汇总不同 |

---

## 五、流水号与日志系统

### 流水号规则

- **格式：** 18位纯数字
- **组成：** 时间戳14位（`yyyyMMddHHmmss`）+ 随机4位数字（1000-9999）
- **示例：** `202504211435220847`
- **生命周期：** 在 `TraceFilter` 生成，通过 `ThreadLocal<TraceContext>` 传递，请求结束后清除

### TraceContext

```java
public class TraceContext {
    private static final ThreadLocal<TraceContext> HOLDER = new ThreadLocal<>();

    private String traceNo;      // 18位流水号
    private String transCode;    // 交易码
    private String requestTime;  // 请求时间 yyyy-MM-dd HH:mm:ss

    // get/set/init/clear 方法
}
```

### TraceLogger（日志写入工具类）

```java
public class TraceLogger {
    // 记录数据库操作
    void logDb(String logType, String operation, String request, String response, long elapsedMs, String status);
    // 记录HTTP外呼
    void logHttp(String serviceName, String request, String response, long elapsedMs, String status);
}
```

所有 Repository 和外呼调用均通过 TraceLogger 自动写 `trace_log` 表。

### 日志写入时机

| 时机 | log_type | operation 示例 |
|------|---------|---------------|
| 数据库查询 | `DB_SELECT` | `SELECT user WHERE user_no=xxx` |
| 数据库插入 | `DB_INSERT` | `INSERT user` |
| 数据库更新 | `DB_UPDATE` | `UPDATE user SET verified=1` |
| 数据库删除 | `DB_DELETE` | `DELETE message` |
| HTTP 外呼 | `HTTP_CALL` | `CALL sms-service /send` |

### 日志文件格式（logback）

```
[TRACE] traceNo=202504211435220847 transCode=dating000001 type=DB_INSERT op="INSERT user" elapsed=12ms status=SUCCESS
```

- 文件名：`dating-system-a.log` / `dating-system-b.log`
- 按天滚动，保留 30 天

### 内嵌 MockServer（外呼模拟）

三个外呼服务随 Spring Boot 启动时内嵌启动：

| 服务 | System-A 地址 | System-B 地址 | 路径 |
|------|-------------|-------------|------|
| 短信通知 | `localhost:9083` | `localhost:9084` | `POST /mock/sms/send` |
| 实名认证 | `localhost:9083` | `localhost:9084` | `POST /mock/identity/verify` |
| 支付服务 | `localhost:9083` | `localhost:9084` | `POST /mock/payment/charge` |

MockServer 接收请求后返回预设的成功响应，无实际业务逻辑。

---

## 六、XML 请求/响应示例

### 请求格式

```xml
<request>
    <trace_no></trace_no>           <!-- 留空，由系统生成 -->
    <request_time>2026-04-21 14:35:22</request_time>
    <trans_code>dating000001</trans_code>
    <body>
        <name>张三</name>
        <gender>1</gender>
        <age>28</age>
        <city>上海</city>
        <phone>13800138000</phone>
        <id_card>310101199801011234</id_card>
    </body>
</request>
```

### 响应格式

```xml
<response>
    <trace_no>202504211435220847</trace_no>
    <request_time>2026-04-21 14:35:22</request_time>
    <response_time>2026-04-21 14:35:22</response_time>
    <trans_code>dating000001</trans_code>
    <code>0000</code>
    <msg>成功</msg>
    <body>
        <user_no>U202504210001</user_no>
        <name>张三</name>
    </body>
</response>
```

---

## 七、非功能要求

- **端口：** system-a 8083 / MockServer 9083；system-b 8084 / MockServer 9084
- **包名：** `com.arex.demo.dating`（与 didi 的 `com.arex.demo.didi` 完全独立）
- **数据库：** `dating_a` / `dating_b`，与 `didi_a` / `didi_b` 无交集
- **启动脚本：** 每套系统各自提供 `start.sh`
- **Postman：** 提供 30 个接口的请求示例集合
