-- ============================================================
-- 交友系统数据库初始化脚本 (dating_system)
-- ============================================================

DROP TABLE IF EXISTS t_notify_config;
DROP TABLE IF EXISTS t_notification;
DROP TABLE IF EXISTS t_event_signup;
DROP TABLE IF EXISTS t_event;
DROP TABLE IF EXISTS t_blacklist;
DROP TABLE IF EXISTS t_report;
DROP TABLE IF EXISTS t_photo;
DROP TABLE IF EXISTS t_recharge_order;
DROP TABLE IF EXISTS t_vip_order;
DROP TABLE IF EXISTS t_gift_order;
DROP TABLE IF EXISTS t_conversation;
DROP TABLE IF EXISTS t_message;
DROP TABLE IF EXISTS t_match_record;
DROP TABLE IF EXISTS t_like_record;
DROP TABLE IF EXISTS t_search_history;
DROP TABLE IF EXISTS t_login_log;
DROP TABLE IF EXISTS t_wallet;
DROP TABLE IF EXISTS t_user_stats;
DROP TABLE IF EXISTS t_user_profile;
DROP TABLE IF EXISTS t_user;

-- 用户主表
CREATE TABLE t_user (
    user_id       VARCHAR(32) PRIMARY KEY,
    nick_name     VARCHAR(64) NOT NULL,
    gender        VARCHAR(8) NOT NULL DEFAULT 'M',
    age           INT NOT NULL DEFAULT 25,
    city          VARCHAR(32) NOT NULL DEFAULT 'BEIJING',
    phone         VARCHAR(32) NOT NULL,
    vip_level     INT NOT NULL DEFAULT 0,
    status        VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 用户资料表
CREATE TABLE t_user_profile (
    profile_id    VARCHAR(32) PRIMARY KEY,
    user_id       VARCHAR(32) NOT NULL,
    avatar_url    VARCHAR(256),
    bio           VARCHAR(512),
    occupation    VARCHAR(64),
    income_range  VARCHAR(32),
    education     VARCHAR(32),
    height        INT,
    trace_id      VARCHAR(64),
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 用户统计表
CREATE TABLE t_user_stats (
    user_id       VARCHAR(32) PRIMARY KEY,
    like_count    INT NOT NULL DEFAULT 0,
    liked_count   INT NOT NULL DEFAULT 0,
    match_count   INT NOT NULL DEFAULT 0,
    photo_count   INT NOT NULL DEFAULT 0,
    report_count  INT NOT NULL DEFAULT 0,
    block_count   INT NOT NULL DEFAULT 0,
    trace_id      VARCHAR(64),
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 登录日志表
CREATE TABLE t_login_log (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    login_ip      VARCHAR(64),
    device_info   VARCHAR(128),
    login_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 搜索历史表
CREATE TABLE t_search_history (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    search_type   VARCHAR(32),
    keyword       VARCHAR(128),
    result_count  INT DEFAULT 0,
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 点赞记录表
CREATE TABLE t_like_record (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_user_id  VARCHAR(32) NOT NULL,
    to_user_id    VARCHAR(32) NOT NULL,
    like_type     VARCHAR(16) NOT NULL DEFAULT 'LIKE',
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 匹配记录表
CREATE TABLE t_match_record (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id_a     VARCHAR(32) NOT NULL,
    user_id_b     VARCHAR(32) NOT NULL,
    match_score   INT NOT NULL DEFAULT 0,
    match_source  VARCHAR(32),
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 消息表
CREATE TABLE t_message (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    sender_id     VARCHAR(32) NOT NULL,
    receiver_id   VARCHAR(32) NOT NULL,
    content       VARCHAR(1024),
    msg_type      VARCHAR(16) NOT NULL DEFAULT 'TEXT',
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 会话表
CREATE TABLE t_conversation (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id_a     VARCHAR(32) NOT NULL,
    user_id_b     VARCHAR(32) NOT NULL,
    last_msg_id   BIGINT,
    msg_count     INT NOT NULL DEFAULT 0,
    trace_id      VARCHAR(64),
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 礼物订单表
CREATE TABLE t_gift_order (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    from_user_id  VARCHAR(32) NOT NULL,
    to_user_id    VARCHAR(32) NOT NULL,
    gift_type     VARCHAR(32) NOT NULL,
    gift_amount   DECIMAL(12,2) NOT NULL DEFAULT 0,
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 钱包表
CREATE TABLE t_wallet (
    user_id        VARCHAR(32) PRIMARY KEY,
    balance        DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_recharge DECIMAL(12,2) NOT NULL DEFAULT 0,
    total_consume  DECIMAL(12,2) NOT NULL DEFAULT 0,
    trace_id       VARCHAR(64),
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- VIP订单表
CREATE TABLE t_vip_order (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    vip_level     INT NOT NULL DEFAULT 1,
    duration_days INT NOT NULL DEFAULT 30,
    amount        DECIMAL(12,2) NOT NULL DEFAULT 0,
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 充值订单表
CREATE TABLE t_recharge_order (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    amount        DECIMAL(12,2) NOT NULL DEFAULT 0,
    pay_channel   VARCHAR(32),
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 照片表
CREATE TABLE t_photo (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    photo_url     VARCHAR(256),
    is_avatar     TINYINT NOT NULL DEFAULT 0,
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 举报记录表
CREATE TABLE t_report (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    reporter_id   VARCHAR(32) NOT NULL,
    reported_id   VARCHAR(32) NOT NULL,
    report_type   VARCHAR(32),
    description   VARCHAR(512),
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 黑名单表
CREATE TABLE t_blacklist (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    blocked_user_id VARCHAR(32) NOT NULL,
    reason        VARCHAR(128),
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 活动表
CREATE TABLE t_event (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    event_name      VARCHAR(128) NOT NULL,
    event_type      VARCHAR(32),
    max_participants INT NOT NULL DEFAULT 100,
    current_participants INT NOT NULL DEFAULT 0,
    event_date      DATE,
    status          VARCHAR(16) NOT NULL DEFAULT 'OPEN',
    trace_id        VARCHAR(64),
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 活动报名表
CREATE TABLE t_event_signup (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    event_id      BIGINT NOT NULL,
    user_id       VARCHAR(32) NOT NULL,
    signup_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通知表
CREATE TABLE t_notification (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    notify_type   VARCHAR(32),
    title         VARCHAR(128),
    content       VARCHAR(512),
    is_read       TINYINT NOT NULL DEFAULT 0,
    trace_id      VARCHAR(64),
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通知配置表
CREATE TABLE t_notify_config (
    id            BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id       VARCHAR(32) NOT NULL,
    notify_type   VARCHAR(32),
    enabled       TINYINT NOT NULL DEFAULT 1,
    trace_id      VARCHAR(64),
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
