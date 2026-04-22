# waimai 接口分析

## 1. 项目定位

`waimai` 是一套新的被测系统样例，结构和 `didi` 类似，都是为了给 AREX 这类录制回放平台提供可观测的业务请求。

它当前包含两套应用：

- `waimai-base`：基线系统，端口 `19091`
- `waimai-compare`：对比系统，端口 `19092`
- `waimai-common`：共享的控制器、业务逻辑、仓储和内部服务

和 `didi` 的关键区别是：

- `didi` 只有一个统一业务入口 `POST /api/car/service`
- `waimai` 有两个外部网关入口：JSON 和 XML
- `waimai` 还显式暴露了 4 个内部 HTTP 接口，复杂交易会自己回调这些内部接口
- 当前 `waimai` 的启动脚本里没有 `-javaagent`，默认并不像 `didi` 那样已经挂好 AREX Agent

## 2. 接口总览

### 2.1 HTTP 接口数量

- 外部业务网关：`2` 个
- 内部子调用接口：`4` 个
- 总 HTTP 接口数：`6` 个
- 网关承载交易码：`30` 个
  - 复杂交易：`15`
  - 简单交易：`15`

### 2.2 对外网关接口

| 接口 | 方法 | Content-Type | 用途 |
|---|---|---|---|
| `/waimai/gateway/json` | `POST` | `application/json` | 主入口，推荐测试入口 |
| `/waimai/gateway/execute` | `POST` | `application/xml` | XML 主入口，适合做协议兼容测试 |

### 2.3 内部子调用接口

| 接口 | 方法 | 作用 | compare 差异点 |
|---|---|---|---|
| `/waimai/internal/pricing` | `POST` | 定价计算 | `+8%` 定价调整，可能还有额外费 |
| `/waimai/internal/discount` | `POST` | 优惠计算 | 优惠倍率从 `1.0` 变成 `1.5`，可能附加配送险 |
| `/waimai/internal/risk` | `POST` | 风控评估 | 阈值从 `80` 提到 `85` |
| `/waimai/internal/delivery-time` | `POST` | 配送时效估算 | compare 开启配送险，赔付信息不同 |

## 3. 系统差异

`base` 与 `compare` 预埋了 8 类差异：

| # | 差异项 | base | compare |
|---|---|---|---|
| 1 | 欢迎语 | `欢迎光临` | `欢迎来到外卖平台` |
| 2 | 下单确认文案 | `下单成功` | `您的订单已成功提交，请耐心等待` |
| 3 | 额外费用 | 无 | `5%` |
| 4 | 定价调整 | 无 | `+8%` |
| 5 | 风控策略 | 宽松，阈值 `80` | 严格，阈值 `85` |
| 6 | 优惠力度 | 标准 `x1.0` | 慷慨 `x1.5` |
| 7 | 配送保险 | 无 | `2%` 费率 |
| 8 | 对账模式 | `STANDARD` | `EXTRA_CHECK` |

这意味着即使同一个 `txnCode`，`base` 和 `compare` 也可能出现：

- 响应字段值不同
- 金额相关字段不同
- 文案不同
- 风控结果不同
- 子调用内容不同

## 4. 交易码统计

### 4.1 复杂交易

这些交易会触发数据库读写，部分还会调用内部 HTTP 接口，因此最适合录制回放和子调用比对。

| 交易码 | 名称 | DB 操作 | 内部 HTTP 子调用 | 主要返回字段 |
|---|---|---|---|---|
| `PLACE_ORDER` | 下单 | `INSERT orders` | `pricing` `discount` `risk` | `orderId` `pricingResult` `discountResult` `riskResult` |
| `CONFIRM_ORDER` | 确认订单 | `UPDATE orders` `UPDATE products` | `risk` | `orderId` `status` |
| `CANCEL_ORDER` | 取消订单 | `UPDATE orders` `UPDATE products` | 无 | `orderId` `status` `refundStatus` |
| `QUERY_ORDER` | 查询订单 | `SELECT orders` | `delivery-time` | `order` `deliveryEstimate` |
| `APPLY_REFUND` | 申请退款 | `INSERT refunds` | `risk` | `refundId` `riskResult` |
| `SEARCH_MERCHANT` | 搜索商户 | `SELECT merchants LIKE` | `pricing` | `merchants` `pricingHint` |
| `MERCHANT_DETAIL` | 商户详情 | `SELECT merchants` | `discount` | `merchant` `discountHint` |
| `ADD_CART` | 加入购物车 | `INSERT cart` | `pricing` | `cartAdded` `pricingHint` |
| `QUERY_CART` | 查询购物车 | `SELECT cart` | `discount` | `cartItems` `discountHint` |
| `SUBMIT_REVIEW` | 提交评价 | `INSERT reviews` | `risk` | `reviewId` `riskResult` |
| `RIDER_LOCATION` | 骑手位置 | `SELECT riders` | `delivery-time` | `riderLocation` `deliveryEstimate` |
| `RECHARGE_WALLET` | 钱包充值 | `UPDATE wallets` | `risk` | `rechargeStatus` `riskResult` |
| `WITHDRAW_WALLET` | 钱包提现 | `UPDATE wallets` | `risk` | `withdrawStatus` `riskResult` |
| `QUERY_WALLET` | 查询钱包 | `SELECT wallets` | 无 | `wallet` `reconciliation` |
| `MERCHANT_SETTLE` | 商户结算 | `INSERT settlements` | 无 | `settlementId` `reconciliation` |

### 4.2 简单交易

这些交易不会访问 DB，也不会触发内部 HTTP 子调用，属于主响应直接返回。

| 交易码 | 名称 | 主要返回字段 | 是否有动态值 |
|---|---|---|---|
| `LIST_CATEGORIES` | 分类列表 | `categories` | 否 |
| `LIST_PRODUCTS` | 商品列表 | `products` | 否 |
| `PRODUCT_DETAIL` | 商品详情 | `productName` `price` | 否 |
| `LIST_ADDRESS` | 地址列表 | `addresses` | 否 |
| `SAVE_ADDRESS` | 保存地址 | `saved` `addressId` | 是 |
| `LIST_COUPONS` | 优惠券列表 | `coupons` | 否 |
| `CLAIM_COUPON` | 领取优惠券 | `claimed` `couponId` | 是 |
| `RIDER_LIST` | 骑手列表 | `riders` | 否 |
| `QUERY_DELIVERY` | 查询配送 | `status` `eta` | 否 |
| `COMPLAINT_SUBMIT` | 提交投诉 | `complaintId` `status` | 是 |
| `COMPLAINT_DETAIL` | 投诉详情 | `complaintId` `result` | 否 |
| `NOTIFICATION_LIST` | 通知列表 | `notifications` | 否 |
| `SYSTEM_CONFIG` | 系统配置 | `config` | 否 |
| `VERSION_CHECK` | 版本检查 | `latestVersion` `needUpdate` | 否 |
| `FEEDBACK_SUBMIT` | 提交反馈 | `feedbackId` `status` | 是 |

## 5. 请求参数

### 5.1 通用 JSON 网关请求

```json
{
  "txnCode": "PLACE_ORDER",
  "params": {
    "customerId": "C001",
    "merchantId": "M001",
    "orderId": "ORD_00001",
    "productId": "P001",
    "productName": "宫保鸡丁",
    "basePrice": "30.0",
    "originalAmount": "50.0",
    "amount": "100.0",
    "keyword": "快餐",
    "quantity": "1",
    "rating": "5",
    "riderId": "R001",
    "complaintId": "CPT_0001"
  }
}
```

### 5.2 通用 XML 网关请求

```xml
<request>
  <txnCode>PLACE_ORDER</txnCode>
  <params>
    <customerId>C001</customerId>
    <merchantId>M001</merchantId>
    <orderId>ORD_00001</orderId>
    <productId>P001</productId>
    <basePrice>30.0</basePrice>
    <originalAmount>50.0</originalAmount>
    <amount>100.0</amount>
    <riderId>R001</riderId>
  </params>
</request>
```

### 5.3 默认样例数据

可直接使用这些种子数据做回放：

- 客户：`C001`、`C002`
- 商户：`M001`、`M002`、`M003`
- 商品：`P001`、`P002`、`P003`、`P004`
- 骑手：`R001`、`R002`

## 6. 响应与比对关注点

### 6.1 所有网关响应都会带

- `traId`
- `requestTime`
- `txnCode`
- `status`
- `data`

### 6.2 明显的动态字段

这些字段在录制回放时天然容易产生差异：

- `traId`
- `requestTime`
- `orderId`
- `refundId`
- `reviewId`
- `settlementId`
- `addressId`
- `couponId`
- `complaintId`
- `feedbackId`

### 6.3 非确定性字段

这两个内部接口还会引入随机性：

- `/waimai/internal/risk`
  - `riskScore` 使用随机数
  - `pass` 受阈值和随机分数影响
- `/waimai/internal/delivery-time`
  - `estimatedMinutes` 使用随机数

如果后面你要把 `waimai` 接到 AREX 里，这两个接口的返回值会是重点差异来源。

## 7. 启动与访问

### 7.1 数据库

- `waimai_alpha`
- `waimai_beta`

初始化脚本：

```bash
mysql -u root -proot123 -P 3307 < waimai/create_databases.sql
```

### 7.2 启动

```bash
cd waimai/waimai-base && ./start.sh
cd waimai/waimai-compare && ./start.sh
```

### 7.3 默认访问地址

- base：`http://localhost:19091`
- compare：`http://localhost:19092`

## 8. Postman 文件

我已经生成好可直接导入的文件：

- `waimai/postman/waimai.postman_collection.json`
- `waimai/postman/waimai-base.local.postman_environment.json`
- `waimai/postman/waimai-compare.local.postman_environment.json`

导入方式：

1. 先导入 collection
2. 再导入 base 或 compare 环境
3. 选择环境后直接发送请求

推荐优先使用：

- `Gateway JSON / Complex Txns`
- `Gateway JSON / Simple Txns`

这样和后续录制回放的使用方式最接近。
