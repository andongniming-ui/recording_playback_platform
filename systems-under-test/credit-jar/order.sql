-- 数据库：order

-- 1、订餐信息
create table book (
  id bigint(20) not null auto_increment comment 'PKID',
  idcard varchar(255) default null comment '身份证',
  opendate date default null comment '用餐时间',
  breakfast varchar(255) default null comment '早餐',
  lunch varchar(255) default null comment '午餐',
  dinner varchar(255) default null comment '晚餐',
  cretime datetime default null comment '创建时间',
  modtime datetime default null comment '修改时间',
  primary key (id)
) engine=innodb default charset=utf8 comment='订餐信息'

-- 插入信息
insert into book(idcard, opendate, breakfast, lunch, dinner, cretime, modtime) values
('440203198709237790', '2026-04-27', '面包、牛奶', '番茄鸡蛋、炒牛肉', '白切鸡、冬瓜', now(), now());