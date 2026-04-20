# didi

这个目录下是两个可直接接入 AREX Recorder 的 Java 被测系统样例：

- `didi-system-a`
- `didi-system-b`

两套系统共用同一份业务代码，都是 JDK8 + Spring Boot + MySQL，只有端口、库名、种子数据和差异配置不同，便于录制后做回放比对。

## 设计目标

- 同一个接口地址：`POST /api/car/service`
- XML 请求
- 30 个逻辑交易码接口：`car000001` 到 `car000030`
- 其中前 15 个交易码带数据库访问和 HTTP 子调用
- 后 15 个交易码是轻量直返接口
- 两套系统专门预埋差异，方便平台在回放比对时打出 diff

## 交易码分布

### 复杂交易，含数据库 + 子调用

- `car000001` 车险试算
- `car000002` 车险出单
- `car000003` 车险续保
- `car000004` 理赔报案
- `car000005` 理赔定损
- `car000006` 道路救援派单
- `car000007` 维修估价
- `car000008` 维修确认
- `car000009` 二手车估值
- `car000010` 车贷预审
- `car000011` 车贷放款确认
- `car000012` 延保查询
- `car000013` 违章代办
- `car000014` 电池健康检测
- `car000015` 充电订单创建

### 轻量交易，主要用于补齐 30 个逻辑接口

- `car000016` 车辆画像查询
- `car000017` 配件库存查询
- `car000018` 保养套餐查询
- `car000019` 门店营业时间查询
- `car000020` 试驾预约提交
- `car000021` 新能源补贴测算
- `car000022` 停车费试算
- `car000023` 车机版本查询
- `car000024` 会员权益校验
- `car000025` 预约洗车
- `car000026` 牌照归属地查询
- `car000027` 充电站列表查询
- `car000028` 积分兑换测算
- `car000029` 优惠券核销校验
- `car000030` 售后评价提交

## 交易码字段

不是所有请求都用同一个字段，系统支持以下字段识别交易码：

- `code`
- `trs_code`
- `service_code`
- `biz_code`
- `trans_code`

也就是说，请求里只要出现上述任意一个字段并带有 `carxxxxxx`，就会按对应逻辑处理。

## 两套系统的专门差异

为了让 AREX 回放比对容易命中，这几个交易码默认会出现可见差异：

- `car000003`
- `car000006`
- `car000011`
- `car000018`
- `car000024`
- `car000029`

差异来源包括：

- 不同的响应文案后缀
- 不同的报价金额
- 不同的风控等级 / 决策
- 不同的 dispatch 城市
- 不同的数据库种子数据

## MySQL 准备

先执行：

```sql
source /home/test/arex-recorder/didi/create_databases.sql;
```

默认配置：

- MySQL 地址：`127.0.0.1:3306`
- 用户名：`root`
- 密码：`root123`
- A 库：`didi_alpha`
- B 库：`didi_beta`

如果你本地已经有 `3306` 的 MySQL 服务，这反而是可以直接复用的，不冲突。  
我已经把数据库连接改成环境变量可配，默认只是连到你现有的 `3306`：

- `DIDI_DB_HOST`
- `DIDI_DB_PORT`
- `DIDI_DB_NAME`
- `DIDI_DB_USER`
- `DIDI_DB_PASSWORD`
- `DIDI_SQL_INIT_MODE`

例如：

```bash
export DIDI_DB_HOST=127.0.0.1
export DIDI_DB_PORT=3306
export DIDI_DB_USER=root
export DIDI_DB_PASSWORD=你的密码
```

如果你不想每次启动都重建表，可以额外设置：

```bash
export DIDI_SQL_INIT_MODE=never
```

## 启动

### 系统 A

```bash
cd /home/test/arex-recorder/didi/didi-system-a
chmod +x start.sh
./start.sh
```

端口：`18081`

### 系统 B

```bash
cd /home/test/arex-recorder/didi/didi-system-b
chmod +x start.sh
./start.sh
```

端口：`18082`

## 与 AREX Recorder 的匹配情况

这两个系统和当前 `/home/test/arex-recorder` 是能匹配起来的，原因是：

- 有标准 `start.sh`，能被平台的 `ssh_script` 模式发现并注入 `-javaagent`
- 入口是标准 Spring Boot HTTP 接口，XML 请求可直接录制
- 复杂交易会走 `JdbcTemplate`，能产生数据库子调用
- 复杂交易还会用 `RestTemplate` 调本机 `/internal/didi/risk` 和 `/internal/didi/pricing`，能产生 HTTP 子调用
- 两套系统的接口地址一致，响应又有受控差异，适合用来做录制回放比对

建议你在 `arex-recorder` 里这样配应用：

### 应用 A

- `name`: `didi-system-a`
- `launch_mode`: `ssh_script`
- `service_port`: `18081`
- `jvm_process_name`: `didi-system-a-1.0.0.jar`
- `arex_app_id`: `didi-car-sat`

### 应用 B

- `name`: `didi-system-b`
- `launch_mode`: `ssh_script`
- `service_port`: `18082`
- `jvm_process_name`: `didi-system-b-1.0.0.jar`
- `arex_app_id`: `didi-car-uat`

注意：

- `jvm_process_name` 最好填 jar 名，这样平台 `pgrep -f` 更容易找到进程
- 录制时先录 `didi-system-a`
- 回放目标指向 `didi-system-b`
- 如果你启用 `use_sub_invocation_mocks`，这套工程也能提供下游 HTTP / DB 子调用样本

## 请求示例

```xml
<request>
  <code>car000001</code>
  <request_no>REQ-car000001</request_no>
  <customer_no>C10001</customer_no>
  <plate_no>沪A10001</plate_no>
  <vin>VIN0000000000000001</vin>
  <policy_no>P10001</policy_no>
  <claim_no>CL10001</claim_no>
  <garage_code>G001</garage_code>
  <city>SHANGHAI</city>
</request>
```

再比如：

```xml
<request>
  <trs_code>car000006</trs_code>
  <request_no>REQ-car000006</request_no>
  <customer_no>C10002</customer_no>
  <plate_no>苏B20002</plate_no>
  <garage_code>G002</garage_code>
  <city>SUZHOU</city>
</request>
```

## 批量打流量

目录里附了一个脚本：

```bash
cd /home/test/arex-recorder/didi
chmod +x send_samples.sh
./send_samples.sh http://127.0.0.1:18081
./send_samples.sh http://127.0.0.1:18082
```

这个脚本会循环发送 30 个交易码请求，比较适合拿来做录制样本。

## 适配 AREX Recorder 的原因

- 系统目录下都有 `start.sh`，方便平台按宿主机脚本模式接入
- 复杂交易使用了 `JdbcTemplate` 查 MySQL
- 复杂交易内部还会通过 `RestTemplate` 调自己暴露的 `/internal/didi/risk` 和 `/internal/didi/pricing`
- 所以录制时既能产生数据库访问，也能产生 HTTP 子调用
