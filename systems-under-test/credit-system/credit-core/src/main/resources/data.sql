DELETE FROM credit_risk_strategy_log;
DELETE FROM credit_external_cache;
DELETE FROM credit_apply_audit;
DELETE FROM credit_employment;
DELETE FROM credit_income_proof;
DELETE FROM credit_history;
DELETE FROM credit_blacklist;
DELETE FROM credit_product_rule;
DELETE FROM credit_customer;

INSERT INTO credit_product_rule (
  product_id, product_name, min_age, max_age, min_income, max_debt_ratio,
  min_credit_score, max_overdue_days, base_limit_factor,
  risk_adjust_factor_low, risk_adjust_factor_medium, risk_adjust_factor_high,
  min_limit, max_limit, annual_rate, term_options, status
) VALUES
('P001', '消费分期贷', 22, 55, 5000.00, 0.6500, 60, 30, 4.0000, 1.0000, 0.8000, 0.5000, 5000.00, 80000.00, 10.8000, '6,12,24', 'ACTIVE'),
('P002', '现金周转贷', 25, 50, 8000.00, 0.5500, 65, 15, 3.5000, 0.9500, 0.7000, 0.4000, 10000.00, 120000.00, 12.6000, '6,12', 'ACTIVE');

INSERT INTO credit_customer (
  customer_id, customer_name, id_no, mobile, age, marital_status, education_level, occupation,
  company_type, monthly_income, monthly_expense, city, customer_status
) VALUES
('C10001', '张一', '310101199001011234', '13800000001', 35, 'MARRIED', 'BACHELOR', 'ENGINEER', 'PRIVATE', 18000.00, 6000.00, 'SHANGHAI', 'ACTIVE'),
('C10002', '李二', '310101198401011235', '13800000002', 42, 'MARRIED', 'MASTER', 'MANAGER', 'STATE_OWNED', 26000.00, 8000.00, 'SHANGHAI', 'ACTIVE'),
('C10003', '王三', '310101200301011236', '13800000003', 23, 'SINGLE', 'COLLEGE', 'SALES', 'PRIVATE', 7000.00, 2500.00, 'SHANGHAI', 'ACTIVE'),
('C10004', '赵四', '310101200201011237', '13800000004', 24, 'SINGLE', 'COLLEGE', 'OPERATOR', 'PRIVATE', 6500.00, 2400.00, 'HANGZHOU', 'ACTIVE'),
('C10005', '钱五', '310101199501011238', '13800000005', 31, 'MARRIED', 'BACHELOR', 'SUPERVISOR', 'PRIVATE', 12000.00, 4200.00, 'SHENZHEN', 'ACTIVE'),
('C10006', '孙六', '310101198801011239', '13800000006', 38, 'MARRIED', 'BACHELOR', 'DESIGNER', 'PRIVATE', 15000.00, 5000.00, 'SHANGHAI', 'ACTIVE'),
('C10007', '周七', '310101198401011240', '13800000007', 40, 'MARRIED', 'BACHELOR', 'FINANCE', 'PRIVATE', 20000.00, 7000.00, 'BEIJING', 'ACTIVE'),
('C10008', '吴八', '310101199301011241', '13800000008', 33, 'MARRIED', 'BACHELOR', 'CONSULTANT', 'PRIVATE', 9000.00, 3500.00, 'SHANGHAI', 'ACTIVE'),
('C10009', '郑九', '310101199701011242', '13800000009', 29, 'SINGLE', 'COLLEGE', 'SERVICE', 'PRIVATE', 4500.00, 1800.00, 'SUZHOU', 'ACTIVE'),
('C10010', '王十', '310101196901011243', '13800000010', 57, 'MARRIED', 'BACHELOR', 'PROCUREMENT', 'PRIVATE', 15000.00, 4000.00, 'SHANGHAI', 'ACTIVE');

INSERT INTO credit_history (
  customer_id, total_credit_limit, current_balance, current_overdue_amount,
  overdue_times_12m, max_overdue_days_12m, loan_count_in_use, settled_loan_count, last_loan_date
) VALUES
('C10001', 60000.00, 12000.00, 0.00, 0, 0, 1, 3, '2026-03-15'),
('C10002', 100000.00, 15000.00, 0.00, 0, 0, 1, 5, '2026-02-28'),
('C10003', 20000.00, 2000.00, 0.00, 0, 0, 0, 1, '2026-01-10'),
('C10004', 15000.00, 3500.00, 0.00, 1, 5, 1, 0, '2026-03-01'),
('C10005', 45000.00, 26000.00, 0.00, 1, 12, 4, 2, '2026-04-01'),
('C10006', 50000.00, 18000.00, 0.00, 2, 15, 5, 3, '2026-03-20'),
('C10007', 30000.00, 8000.00, 0.00, 0, 0, 1, 2, '2026-02-12'),
('C10008', 28000.00, 9000.00, 0.00, 0, 0, 2, 1, '2026-02-18'),
('C10009', 10000.00, 1000.00, 0.00, 0, 0, 0, 0, NULL),
('C10010', 32000.00, 5000.00, 0.00, 0, 0, 1, 2, '2026-01-18');

INSERT INTO credit_income_proof (
  customer_id, salary_verified, tax_verified, provident_fund_verified, verified_income
) VALUES
('C10001', 'Y', 'Y', 'Y', 18000.00),
('C10002', 'Y', 'Y', 'Y', 26000.00),
('C10003', 'Y', 'N', 'N', 7000.00),
('C10004', 'Y', 'N', 'N', 6500.00),
('C10005', 'Y', 'Y', 'N', 12000.00),
('C10006', 'Y', 'Y', 'Y', 15000.00),
('C10007', 'Y', 'Y', 'Y', 20000.00),
('C10008', 'Y', 'N', 'N', 9000.00),
('C10009', 'N', 'N', 'N', 4500.00),
('C10010', 'Y', 'Y', 'Y', 15000.00);

INSERT INTO credit_employment (
  customer_id, employment_status, company_name, industry, work_years
) VALUES
('C10001', 'EMPLOYED', '星海科技', 'INTERNET', 8),
('C10002', 'EMPLOYED', '城投集团', 'FINANCE', 12),
('C10003', 'EMPLOYED', '新锐零售', 'RETAIL', 1),
('C10004', 'EMPLOYED', '云腾服务', 'SERVICE', 1),
('C10005', 'EMPLOYED', '中南制造', 'MANUFACTURE', 4),
('C10006', 'EMPLOYED', '创美设计', 'DESIGN', 6),
('C10007', 'EMPLOYED', '瑞诚资本', 'FINANCE', 10),
('C10008', 'EMPLOYED', '蓝海咨询', 'CONSULTING', 5),
('C10009', 'FLEXIBLE', '个体经营', 'SERVICE', 1),
('C10010', 'EMPLOYED', '申城采购', 'TRADE', 20);

INSERT INTO credit_blacklist (customer_id, black_type, reason, status) VALUES
('C10007', 'INTERNAL', '命中内部黑名单', 'ACTIVE');
