# credit-system

模拟“准入 + 授信”场景的单系统样例，适合做录制回放、子调用采集和数据库调用采集。

## 服务

| 服务 | 端口 | 说明 |
|---|---:|---|
| credit-core | 29081 | 主服务，提供准入和授信接口 |
| credit-mock | 29083 | 模拟外部征信、反欺诈、多头借贷、联系人稳定性 |

## 交易码

- `CRD_ADMIT`：准入
- `CRD_LIMIT`：授信

## 快速启动

```bash
# 1. 建库
mysql -u root -proot123 -P 3307 < create_databases.sql

# 2. 编译
cd /home/recording_playback_platform/systems-under-test/credit-system && mvn package -DskipTests -q

# 3. 启动 mock
cd credit-mock && chmod +x start.sh && ./start.sh

# 4. 启动主服务
cd credit-core && chmod +x start.sh && ./start.sh

# 5. 打样例流量
chmod +x send_samples.sh && ./send_samples.sh http://127.0.0.1:29081
```

## Postman / ApiPost

导入下面 3 个文件：

- `postman/credit-system.postman_collection.json`
- `postman/credit-system.local.postman_environment.json`
- `postman/credit-system.remote-template.postman_environment.json`

使用方式：

1. 本地调试时，选 `credit-system.local`
2. 远程调试时，复制 `credit-system.remote-template`，把 `baseUrl` 改成实际地址
3. 集合里已经带前置脚本，会自动生成：
   - `traId`
   - `requestTime`
   - `requestNo`
4. 直接发送请求即可，不需要手工改流水号和时间

推荐先跑这 4 条：

- `CRD_ADMIT C10001 P001 标准通过`
- `CRD_ADMIT C10007 P001 黑名单拒绝`
- `CRD_LIMIT C10001 P001 标准授信`
- `CRD_LIMIT C10005 P002 高风险降额`

这几条分别覆盖：

- 标准中链路
- 黑名单短链路
- 标准授信链路
- 大额 + 多头借贷 + 降额长链路

如果你用的是 ApiPost，直接导入 Postman 2.1 集合即可。

## 主接口

- `POST /credit/gateway`

XML 请求，两个交易码共用同一个入口。

## 外部 mock

- `GET /mock/credit-score?customerId=...`
- `GET /mock/fraud?customerId=...`
- `GET /mock/multi-loan?customerId=...`
- `GET /mock/contact-stability?customerId=...`
- `GET /mock/health`

## 内部子调用

- `GET /internal/credit/risk`
- `GET /internal/credit/pricing`

## 场景特征

- `CRD_ADMIT` 和 `CRD_LIMIT` 都会查本地 MySQL
- 不同客户 / 产品 / 金额会触发不同的子调用和数据库调用
- 黑名单、收入不足、年龄超限会形成短链路
- 新客、现金贷、大额申请会形成长链路

## 代表性链路

### 准入

- `C10001 + P001`
  - 标准通过
  - 子调用：`credit-score`、`fraud`、`internal risk`
- `C10003 + P001`
  - 新客加强校验
  - 额外子调用：`contact-stability`
- `C10007 + P001`
  - 黑名单拒绝
  - 只走客户、产品、黑名单查询
- `C10009 + P001`
  - 收入不足拒绝
  - 短链路

### 授信

- `C10001 + P001`
  - 标准授信
  - 子调用：`credit-score`、`fraud`、`internal risk`、`internal pricing`
- `C10005 + P002`
  - 高风险降额
  - 额外子调用：`multi-loan`
  - 额外数据库：`credit_income_proof`、`credit_employment`、`credit_risk_strategy_log`
