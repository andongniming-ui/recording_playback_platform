CREATE TABLE IF NOT EXISTS credit_customer (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(32) NOT NULL UNIQUE,
  customer_name VARCHAR(64) NOT NULL,
  id_no VARCHAR(32) NOT NULL,
  mobile VARCHAR(32) NOT NULL,
  age INT NOT NULL,
  marital_status VARCHAR(16),
  education_level VARCHAR(32),
  occupation VARCHAR(64),
  company_type VARCHAR(32),
  monthly_income DECIMAL(12,2) NOT NULL,
  monthly_expense DECIMAL(12,2) DEFAULT 0,
  city VARCHAR(32),
  customer_status VARCHAR(16) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_product_rule (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  product_id VARCHAR(32) NOT NULL UNIQUE,
  product_name VARCHAR(64) NOT NULL,
  min_age INT NOT NULL,
  max_age INT NOT NULL,
  min_income DECIMAL(12,2) NOT NULL,
  max_debt_ratio DECIMAL(6,4) NOT NULL,
  min_credit_score INT NOT NULL,
  max_overdue_days INT NOT NULL,
  base_limit_factor DECIMAL(8,4) NOT NULL,
  risk_adjust_factor_low DECIMAL(8,4) NOT NULL,
  risk_adjust_factor_medium DECIMAL(8,4) NOT NULL,
  risk_adjust_factor_high DECIMAL(8,4) NOT NULL,
  min_limit DECIMAL(12,2) NOT NULL,
  max_limit DECIMAL(12,2) NOT NULL,
  annual_rate DECIMAL(8,4) NOT NULL,
  term_options VARCHAR(64),
  status VARCHAR(16) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_blacklist (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(32) NOT NULL,
  black_type VARCHAR(32) NOT NULL,
  reason VARCHAR(256),
  status VARCHAR(16) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_history (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(32) NOT NULL UNIQUE,
  total_credit_limit DECIMAL(12,2) DEFAULT 0,
  current_balance DECIMAL(12,2) DEFAULT 0,
  current_overdue_amount DECIMAL(12,2) DEFAULT 0,
  overdue_times_12m INT DEFAULT 0,
  max_overdue_days_12m INT DEFAULT 0,
  loan_count_in_use INT DEFAULT 0,
  settled_loan_count INT DEFAULT 0,
  last_loan_date DATE,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_income_proof (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(32) NOT NULL UNIQUE,
  salary_verified VARCHAR(16) NOT NULL,
  tax_verified VARCHAR(16) NOT NULL,
  provident_fund_verified VARCHAR(16) NOT NULL,
  verified_income DECIMAL(12,2) DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_employment (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  customer_id VARCHAR(32) NOT NULL UNIQUE,
  employment_status VARCHAR(16) NOT NULL,
  company_name VARCHAR(128),
  industry VARCHAR(64),
  work_years INT DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_apply_audit (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  txn_code VARCHAR(32) NOT NULL,
  tra_id VARCHAR(64) NOT NULL,
  request_time VARCHAR(32) NOT NULL,
  request_no VARCHAR(64) NOT NULL,
  customer_id VARCHAR(32) NOT NULL,
  product_id VARCHAR(32) NOT NULL,
  apply_amount DECIMAL(12,2),
  apply_term INT,
  credit_score INT,
  fraud_level VARCHAR(16),
  multi_loan_count INT,
  risk_level VARCHAR(16),
  admit_result VARCHAR(16),
  approved_limit DECIMAL(12,2),
  limit_grade VARCHAR(16),
  pricing_rate DECIMAL(8,4),
  decision_reason VARCHAR(512),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_external_cache (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  tra_id VARCHAR(64) NOT NULL,
  customer_id VARCHAR(32) NOT NULL,
  ext_type VARCHAR(32) NOT NULL,
  ext_request TEXT,
  ext_response TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS credit_risk_strategy_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  tra_id VARCHAR(64) NOT NULL,
  customer_id VARCHAR(32) NOT NULL,
  product_id VARCHAR(32) NOT NULL,
  strategy_name VARCHAR(64) NOT NULL,
  strategy_result VARCHAR(32) NOT NULL,
  strategy_detail VARCHAR(512),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
