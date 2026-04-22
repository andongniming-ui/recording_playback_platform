# 外卖被测系统 (Waimai)

模拟外卖平台的微服务系统，用于 AREX 录制回放对比测试。

## 架构
- **waimai-base** (端口 19091) — 基线系统
- **waimai-compare** (端口 19092) — 对比系统，含8个预埋差异
- **waimai-common** — 共享业务代码

## 差异清单

| # | 差异点 | base | compare |
|---|--------|------|---------|
| 1 | 文案(greeting) | 欢迎光临 | 欢迎来到外卖平台 |
| 2 | 下单确认消息 | 下单成功 | 您的订单已成功提交，请耐心等待 |
| 3 | 额外费用 | 无 | 5%额外费 |
| 4 | 定价调整 | 无 | +8% |
| 5 | 风控策略 | 宽松(80) | 严格(85) |
| 6 | 优惠力度 | 标准x1 | 慷慨x1.5 |
| 7 | 配送保险 | 无 | 2%费率 |
| 8 | 对账模式 | 标准 | 额外校验 |

## 快速启动

```bash
mysql -u root -proot123 -P 3307 < create_databases.sql
cd /home/recording_playback_platform/systems-under-test/waimai && mvn package -DskipTests -q
cd waimai-base && chmod +x start.sh && ./start.sh
cd ../waimai-compare && chmod +x start.sh && ./start.sh
chmod +x send_samples.sh && ./send_samples.sh http://localhost:19091 1
```

## 接口
- POST /waimai/gateway/json — JSON 网关
- POST /waimai/gateway/execute — XML 网关
- POST /waimai/internal/pricing — 定价
- POST /waimai/internal/discount — 优惠
- POST /waimai/internal/risk — 风控
- POST /waimai/internal/delivery-time — 配送预估

## 文档与 Postman

- 详细接口清单：`systems-under-test/waimai/接口清单.md`
- 接口分析：`systems-under-test/waimai/INTERFACE_ANALYSIS.md`
- Postman Collection：`systems-under-test/waimai/postman/waimai.postman_collection.json`
- Postman 环境：
  - `systems-under-test/waimai/postman/waimai-base.local.postman_environment.json`
  - `systems-under-test/waimai/postman/waimai-compare.local.postman_environment.json`

导入建议：

1. 先导入 Collection
2. 再导入 `base` 或 `compare` 环境
3. 优先从 `Gateway JSON / Complex Txns` 开始测试

说明：

- `waimai` 的 `traId` 由服务端自动生成，不像 `didi` 那样通过请求参数透传
- 如果后续要接入 AREX 录制回放，还需要像 `didi` 一样在启动脚本里挂 `-javaagent`

## 30个交易码

复杂(15): PLACE_ORDER, CONFIRM_ORDER, CANCEL_ORDER, QUERY_ORDER, APPLY_REFUND, SEARCH_MERCHANT, MERCHANT_DETAIL, ADD_CART, QUERY_CART, SUBMIT_REVIEW, RIDER_LOCATION, RECHARGE_WALLET, WITHDRAW_WALLET, QUERY_WALLET, MERCHANT_SETTLE

简单(15): LIST_CATEGORIES, LIST_PRODUCTS, PRODUCT_DETAIL, LIST_ADDRESS, SAVE_ADDRESS, LIST_COUPONS, CLAIM_COUPON, RIDER_LIST, QUERY_DELIVERY, COMPLAINT_SUBMIT, COMPLAINT_DETAIL, NOTIFICATION_LIST, SYSTEM_CONFIG, VERSION_CHECK, FEEDBACK_SUBMIT
