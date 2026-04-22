insert into car_customer(customer_no, customer_name, tier_level, city, mobile) values
('C10001', '张一', 'STANDARD', 'SHANGHAI', '13900000001'),
('C10002', '李二', 'STANDARD', 'SUZHOU', '13900000002'),
('C10003', '王三', 'VIP', 'HANGZHOU', '13900000003');

insert into car_vehicle(plate_no, vin, owner_customer_no, model_name, energy_type, risk_score, vehicle_status) values
('沪A10001', 'VIN0000000000000001', 'C10001', 'DIDI EV S1', 'EV', 58, 'ACTIVE'),
('苏B20002', 'VIN0000000000000002', 'C10002', 'DIDI SUV X2', 'GAS', 73, 'ACTIVE'),
('浙C30003', 'VIN0000000000000003', 'C10003', 'DIDI MPV M3', 'HYBRID', 91, 'ACTIVE');

insert into car_policy(policy_no, customer_no, plate_no, premium_amount, policy_status) values
('P10001', 'C10001', '沪A10001', 1988.00, 'VALID'),
('P10002', 'C10002', '苏B20002', 2520.00, 'RENEW_REVIEW'),
('P10003', 'C10003', '浙C30003', 3390.00, 'CLAIM_REVIEW');

insert into car_claim(claim_no, plate_no, claim_amount, claim_status) values
('CL10001', '沪A10001', 2400.00, 'REGISTERED'),
('CL10002', '苏B20002', 3980.00, 'ASSESS_RECHECK'),
('CL10003', '浙C30003', 5500.00, 'OPEN');

insert into car_dispatch(dispatch_no, plate_no, city, garage_code, dispatch_status) values
('D10001', '沪A10001', 'SHANGHAI', 'G001', 'READY'),
('D10002', '苏B20002', 'SUZHOU', 'G002', 'MANUAL_ASSIGN'),
('D10003', '浙C30003', 'HANGZHOU', 'G003', 'IN_PROGRESS');
