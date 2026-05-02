#!/bin/bash
# 交友系统 - 交易码测试脚本
# 用法: bash send_samples.sh [host] [port]

HOST=${1:-127.0.0.1}
PORT=${2:-28090}
BASE_URL="http://${HOST}:${PORT}/api/dating/service"

echo "============================================"
echo "  交友系统 (dating-system) 交易码测试脚本"
echo "  目标: ${BASE_URL}"
echo "============================================"
echo ""

# 生成18位随机trace_id
gen_trace_id() {
    echo $(cat /dev/urandom | tr -dc '0-9' | head -c 18)
}

# DAT001 用户注册
echo "--- DAT001 用户注册 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT001</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U20001</user_id>
  <phone>13900002001</phone>
  <gender>M</gender>
  <age>28</age>
  <city>BEIJING</city>
</request>"
echo -e "\n"

# DAT002 用户登录
echo "--- DAT002 用户登录 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT002</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
</request>"
echo -e "\n"

# DAT003 资料更新
echo "--- DAT003 资料更新 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT003</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <msg_content>热爱旅行和摄影</msg_content>
  <search_keyword>摄影师</search_keyword>
</request>"
echo -e "\n"

# DAT004 用户搜索
echo "--- DAT004 用户搜索 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT004</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <search_keyword>SHANGHAI</search_keyword>
  <search_type>CITY</search_type>
  <gender>F</gender>
  <city>SHANGHAI</city>
</request>"
echo -e "\n"

# DAT005 点赞喜欢
echo "--- DAT005 点赞喜欢 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT005</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <target_user_id>U10002</target_user_id>
  <like_type>SUPERLIKE</like_type>
</request>"
echo -e "\n"

# DAT006 匹配推荐
echo "--- DAT006 匹配推荐 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT006</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
</request>"
echo -e "\n"

# DAT007 发送消息
echo "--- DAT007 发送消息 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT007</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <target_user_id>U10002</target_user_id>
  <msg_content>你好，很高兴认识你！</msg_content>
  <msg_type>TEXT</msg_type>
</request>"
echo -e "\n"

# DAT008 送礼物
echo "--- DAT008 送礼物 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT008</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <target_user_id>U10002</target_user_id>
  <gift_type>ROSE</gift_type>
  <gift_amount>9.90</gift_amount>
</request>"
echo -e "\n"

# DAT009 VIP开通
echo "--- DAT009 VIP开通 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT009</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10002</user_id>
  <vip_level>1</vip_level>
  <duration_days>30</duration_days>
</request>"
echo -e "\n"

# DAT010 钱包充值
echo "--- DAT010 钱包充值 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT010</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <recharge_amount>100.00</recharge_amount>
  <pay_channel>ALIPAY</pay_channel>
</request>"
echo -e "\n"

# DAT011 上传照片
echo "--- DAT011 上传照片 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT011</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <photo_url>/upload/photo_001.jpg</photo_url>
  <is_avatar>1</is_avatar>
</request>"
echo -e "\n"

# DAT012 举报用户
echo "--- DAT012 举报用户 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT012</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <target_user_id>U10003</target_user_id>
  <report_type>HARASSMENT</report_type>
  <report_desc>发送不当消息</report_desc>
</request>"
echo -e "\n"

# DAT013 拉黑用户
echo "--- DAT013 拉黑用户 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT013</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <target_user_id>U10003</target_user_id>
  <block_reason>不想看到此用户</block_reason>
</request>"
echo -e "\n"

# DAT014 活动报名
echo "--- DAT014 活动报名 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT014</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <event_id>1</event_id>
</request>"
echo -e "\n"

# DAT015 通知查询
echo "--- DAT015 通知查询 ---"
TRACE_ID=$(gen_trace_id)
curl -s -X POST "${BASE_URL}" \
  -H "Content-Type: application/xml" \
  -d "<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<request>
  <tran_code>DAT015</tran_code>
  <trace_id>${TRACE_ID}</trace_id>
  <user_id>U10001</user_id>
  <notify_type>LIKE</notify_type>
</request>"
echo -e "\n"

echo "============================================"
echo "  全部 15 个交易码测试完成"
echo "============================================"
