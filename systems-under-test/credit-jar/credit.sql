-- 数据库：credit

-- 1、客户信息
create table cust_info (
  id bigint(20) not null auto_increment comment 'PKID',
  name varchar(255) default null comment '姓名',
  gender varchar(10) default null comment '性别，1男，2女',
  birth date default null comment '出生日期',
  age int(4) default null comment '年龄',
  idcard varchar(20) default null comment '身份证号',
  status varchar(2) default null comment '状态，0正常，1销户，2冻结',
  cretime datetime default null comment '创建时间',
  modtime datetime default null comment '修改时间',
  primary key (id)
) engine=innodb default charset=utf8 comment='客户信息'

-- 插入数据
insert into cust_info(name, gender, birth, age, idcard, status, cretime, modtime) values
("舒唛","1",'19870923',timestampdiff(year, '19870923', curdate()),'440203198709237790','0',now(),now()),
("英宝","2",'20091104',timestampdiff(year, '20091104', curdate()),'440118200911042256','0',now(),now())