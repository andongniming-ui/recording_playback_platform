-- 初始化测试数据

-- 用户主表
INSERT INTO t_user (user_id, nick_name, gender, age, city, phone, vip_level, status) VALUES
('U10001', '张三', 'M', 28, 'BEIJING', '13800001001', 1, 'ACTIVE'),
('U10002', '李四', 'F', 25, 'SHANGHAI', '13800001002', 0, 'ACTIVE'),
('U10003', '王五', 'M', 30, 'GUANGZHOU', '13800001003', 2, 'ACTIVE'),
('U10004', '赵六', 'F', 27, 'SHENZHEN', '13800001004', 0, 'ACTIVE'),
('U10005', '孙七', 'M', 32, 'HANGZHOU', '13800001005', 1, 'ACTIVE'),
('U10006', '周八', 'F', 24, 'CHENGDU', '13800001006', 0, 'ACTIVE'),
('U10007', '吴九', 'M', 29, 'WUHAN', '13800001007', 3, 'ACTIVE'),
('U10008', '郑十', 'F', 26, 'NANJING', '13800001008', 0, 'ACTIVE'),
('U10009', '陈一一', 'M', 31, 'XIAMEN', '13800001009', 1, 'ACTIVE'),
('U10010', '林二二', 'F', 23, 'CHONGQING', '13800001010', 0, 'ACTIVE');

-- 用户资料表
INSERT INTO t_user_profile (profile_id, user_id, avatar_url, bio, occupation, income_range, education, height) VALUES
('P10001', 'U10001', '/avatar/u10001.jpg', '阳光开朗，热爱生活', '工程师', '20-30K', '本科', 175),
('P10002', 'U10002', '/avatar/u10002.jpg', '温柔体贴，喜欢旅行', '设计师', '15-25K', '硕士', 163),
('P10003', 'U10003', '/avatar/u10003.jpg', '稳重踏实，追求品质', '经理', '30-50K', '硕士', 180),
('P10004', 'U10004', '/avatar/u10004.jpg', '活泼可爱，喜欢美食', '教师', '10-20K', '本科', 160),
('P10005', 'U10005', '/avatar/u10005.jpg', '幽默风趣，爱好运动', '医生', '25-40K', '博士', 178);

-- 用户统计表
INSERT INTO t_user_stats (user_id, like_count, liked_count, match_count, photo_count, report_count, block_count) VALUES
('U10001', 15, 32, 8, 5, 0, 1),
('U10002', 20, 45, 12, 8, 0, 0),
('U10003', 10, 28, 6, 3, 0, 2),
('U10004', 18, 50, 15, 10, 0, 0),
('U10005', 12, 35, 9, 6, 0, 1),
('U10006', 8, 22, 5, 4, 0, 0),
('U10007', 25, 60, 18, 12, 0, 3),
('U10008', 16, 40, 10, 7, 0, 0),
('U10009', 14, 30, 7, 5, 0, 1),
('U10010', 22, 55, 14, 9, 0, 0);

-- 钱包表
INSERT INTO t_wallet (user_id, balance, total_recharge, total_consume) VALUES
('U10001', 500.00, 1000.00, 500.00),
('U10002', 200.00, 500.00, 300.00),
('U10003', 1500.00, 2000.00, 500.00),
('U10004', 100.00, 300.00, 200.00),
('U10005', 800.00, 1500.00, 700.00),
('U10006', 50.00, 100.00, 50.00),
('U10007', 3000.00, 5000.00, 2000.00),
('U10008', 300.00, 600.00, 300.00),
('U10009', 600.00, 1200.00, 600.00),
('U10010', 150.00, 400.00, 250.00);

-- 活动表
INSERT INTO t_event (id, event_name, event_type, max_participants, current_participants, event_date, status) VALUES
(1, '春季户外联谊', 'OUTDOOR', 50, 23, '2026-05-15', 'OPEN'),
(2, '美食探店聚会', 'FOOD', 30, 18, '2026-05-20', 'OPEN'),
(3, '电影之夜', 'MOVIE', 40, 12, '2026-05-25', 'OPEN'),
(4, '周末骑行俱乐部', 'SPORTS', 20, 8, '2026-06-01', 'OPEN'),
(5, '读书分享会', 'CULTURE', 25, 15, '2026-06-10', 'OPEN');

-- 通知配置
INSERT INTO t_notify_config (id, user_id, notify_type, enabled) VALUES
(1, 'U10001', 'LIKE', 1),
(2, 'U10001', 'MATCH', 1),
(3, 'U10001', 'MESSAGE', 1),
(4, 'U10002', 'LIKE', 1),
(5, 'U10002', 'MATCH', 1),
(6, 'U10002', 'MESSAGE', 0),
(7, 'U10003', 'LIKE', 1),
(8, 'U10003', 'MATCH', 0),
(9, 'U10003', 'MESSAGE', 1);
