# 个人信贷评估系统 (Loan System)

虚构个人信贷评估场景，用于 AREX 录制回放双发比对测试。

## 架构

| 服务 | 端口 | 说明 |
|------|------|------|
| loan-old | 28081 | 老系统（正确逻辑） |
| loan-new | 28082 | 新系统（含4处预埋Bug） |
| loan-mock | 28083 | Mock征信服务 |

## 5个交易码

| 交易码 | 名称 | 类型 | 涉及 |
|--------|------|------|------|
| LOAN_QUALIFY | 客户基础资质校验 | DB查询 | 年龄/证件/状态 |
| LOAN_CREDIT | 征信分查询与风险评级 | HTTP外呼+DB | Mock征信+黑名单 |
| LOAN_INCOME | 收入规则校验 | DB查询 | 收入门槛/负债比 |
| LOAN_QUOTA | 授信额度测算 | DB查询 | 月收入×系数×调整因子 |
| LOAN_ADMIT | 综合准入评估 | 汇总全部 | 调用4个子接口 |

## 4处预埋Bug（开发者知晓，测试侧不提前知晓）

| # | Bug描述 | 影响交易码 | 触发条件 |
|---|--------|-----------|---------|
| 1 | 年龄上限 <=60 改为 <60 | LOAN_QUALIFY, LOAN_ADMIT | 客户年龄恰好=60（C002） |
| 2 | 征信低风险 >=80 改为 >80 | LOAN_CREDIT, LOAN_ADMIT | 征信分恰好=80（C006） |
| 3 | 负债收入比阈值 0.50→0.55 | LOAN_INCOME, LOAN_ADMIT | 负债比在0.50~0.55之间（C006） |
| 4 | 额度调整系数 0.80→0.75 | LOAN_QUOTA, LOAN_ADMIT | 所有通过客户额度偏低 |

## 边界值测试数据

| 客户 | 年龄 | 收入 | 负债 | 负债比 | 征信分 | 状态 | 预期差异 |
|------|------|------|------|--------|--------|------|---------|
| C001 | 35 | 15000 | 3000 | 0.20 | 78 | ACTIVE | Bug4额度差 |
| C002 | **60** | 8000 | 4000 | 0.50 | 65 | ACTIVE | **Bug1年龄** |
| C003 | **18** | 5000 | 2500 | 0.50 | 82 | ACTIVE | Bug4额度差 |
| C004 | 61 | 12000 | 6000 | 0.50 | 45 | ACTIVE | 无(本就不过) |
| C005 | 40 | 20000 | 10000 | 0.50 | 88 | FROZEN | 无(状态不过) |
| C006 | 45 | 10000 | 5300 | **0.53** | **80** | ACTIVE | **Bug2+Bug3+Bug4** |
| C007 | 35 | **4999** | 1000 | 0.20 | 55 | ACTIVE | 无(收入不过) |
| C008 | 30 | **5000** | 1000 | 0.20 | 72 | ACTIVE | Bug4额度差 |
| C009 | 28 | 25000 | 5000 | 0.20 | 92 | ACTIVE | Bug4额度差 |
| C010 | 33 | 10000 | 2000 | 0.20 | 30 | ACTIVE | 无(黑名单) |

## 快速启动

```bash
# 1. 建库
mysql -u root -proot123 -P 3307 < create_databases.sql

# 2. 编译
cd /home/recording_playback_platform/systems-under-test/loan-system && mvn package -DskipTests -q

# 3. 启动 Mock 征信服务
cd loan-mock && chmod +x start.sh && ./start.sh

# 4. 启动老系统
cd loan-old && chmod +x start.sh && ./start.sh

# 5. 启动新系统
cd loan-new && chmod +x start.sh && ./start.sh

# 6. 打测试流量
chmod +x send_samples.sh && ./send_samples.sh http://localhost:28081
```

## 接口

### 主入口
- `POST /loan/gateway` - XML网关
- `POST /loan/gateway/json` - JSON网关

### 内部子调用（AREX录制点）
- `POST /loan/internal/qualify` - 资质校验
- `POST /loan/internal/credit` - 征信查询
- `POST /loan/internal/income` - 收入校验
- `POST /loan/internal/quota` - 额度测算

### Mock服务
- `GET /mock/credit?customerId=xxx` - 模拟征信查询

## 日志格式

每次请求记录：交易码、流水号(traId)、入参摘要、出参摘要、耗时(ms)

```
[a1b2c3d4e5f6] txnCode=LOAN_QUALIFY | params={customerId=C002, productId=P001}
[a1b2c3d4e5f6] Qualify result: false | age=60 mode=EXCLUSIVE | elapsed=15ms
```

## -Dapp.name 说明

启动参数 `-Dapp.name=loan-system` 是双发比对工具必需的，用于定位进程。
老系统和新系统均使用相同的 `-Dapp.name=loan-system`。
