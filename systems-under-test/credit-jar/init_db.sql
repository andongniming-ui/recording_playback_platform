-- 初始化 credit-jar 所需的两个数据库
-- 执行方式：mysql -h127.0.0.1 -P3307 -uroot -proot123 < init_db.sql

-- ============================================================
-- 数据库：credit
-- ============================================================
CREATE DATABASE IF NOT EXISTS credit DEFAULT CHARACTER SET utf8;
USE credit;

CREATE TABLE IF NOT EXISTS cust_info (
  id bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'PKID',
  name varchar(255) DEFAULT NULL COMMENT '姓名',
  gender varchar(10) DEFAULT NULL COMMENT '性别，1男，2女',
  birth date DEFAULT NULL COMMENT '出生日期',
  age int(4) DEFAULT NULL COMMENT '年龄',
  idcard varchar(20) DEFAULT NULL COMMENT '身份证号',
  status varchar(2) DEFAULT NULL COMMENT '状态，0正常，1销户，2冻结',
  cretime datetime DEFAULT NULL COMMENT '创建时间',
  modtime datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='客户信息';

INSERT INTO cust_info(name, gender, birth, age, idcard, status, cretime, modtime) VALUES
('舒唛','1','1987-09-23',TIMESTAMPDIFF(YEAR,'1987-09-23',CURDATE()),'440203198709237790','0',NOW(),NOW()),
('英宝','2','2009-11-04',TIMESTAMPDIFF(YEAR,'2009-11-04',CURDATE()),'440118200911042256','0',NOW(),NOW());

-- ============================================================
-- 数据库：order
-- ============================================================
CREATE DATABASE IF NOT EXISTS `order` DEFAULT CHARACTER SET utf8;
USE `order`;

CREATE TABLE IF NOT EXISTS book (
  id bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'PKID',
  idcard varchar(255) DEFAULT NULL COMMENT '身份证',
  opendate date DEFAULT NULL COMMENT '用餐时间',
  breakfast varchar(255) DEFAULT NULL COMMENT '早餐',
  lunch varchar(255) DEFAULT NULL COMMENT '午餐',
  dinner varchar(255) DEFAULT NULL COMMENT '晚餐',
  cretime datetime DEFAULT NULL COMMENT '创建时间',
  modtime datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='订餐信息';

INSERT INTO book(idcard, opendate, breakfast, lunch, dinner, cretime, modtime) VALUES
('440203198709237790','2026-04-27','面包、牛奶','番茄鸡蛋、炒牛肉','白切鸡、冬瓜',NOW(),NOW());
