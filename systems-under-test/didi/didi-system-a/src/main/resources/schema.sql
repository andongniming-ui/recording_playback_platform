drop table if exists car_order_audit;
drop table if exists car_dispatch;
drop table if exists car_claim;
drop table if exists car_policy;
drop table if exists car_vehicle;
drop table if exists car_customer;

create table car_customer (
    customer_no varchar(32) primary key,
    customer_name varchar(64) not null,
    tier_level varchar(16) not null,
    city varchar(32) not null,
    mobile varchar(32) not null
);

create table car_vehicle (
    plate_no varchar(32) primary key,
    vin varchar(32) not null,
    owner_customer_no varchar(32) not null,
    model_name varchar(64) not null,
    energy_type varchar(16) not null,
    risk_score int not null,
    vehicle_status varchar(32) not null
);

create table car_policy (
    policy_no varchar(32) primary key,
    customer_no varchar(32) not null,
    plate_no varchar(32) not null,
    premium_amount decimal(12,2) not null,
    policy_status varchar(32) not null
);

create table car_claim (
    claim_no varchar(32) primary key,
    plate_no varchar(32) not null,
    claim_amount decimal(12,2) not null,
    claim_status varchar(32) not null
);

create table car_dispatch (
    dispatch_no varchar(32) primary key,
    plate_no varchar(32) not null,
    city varchar(32) not null,
    garage_code varchar(32) not null,
    dispatch_status varchar(32) not null
);

create table car_order_audit (
    id bigint primary key auto_increment,
    txn_code varchar(16) not null,
    request_no varchar(64),
    customer_no varchar(32),
    plate_no varchar(32),
    risk_level varchar(16),
    quoted_amount decimal(12,2),
    variant_id varchar(16),
    created_at timestamp default current_timestamp
);
