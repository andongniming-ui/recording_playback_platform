#!/bin/bash
# Sample requests for Rental System APIs.
# Defaults to rental-base; set TARGET=http://127.0.0.1:20082 to hit rental-compare.

set -u

BASE="${BASE:-http://127.0.0.1:20081}"
COMPARE="${COMPARE:-http://127.0.0.1:20082}"
TARGET="${TARGET:-$BASE}"
CT="Content-Type: application/xml"
ACCEPT="Accept: application/xml"

serial() {
    echo "$(date +%Y%m%d%H%M%S)$(printf "%04d" $((RANDOM % 10000)))"
}

xml_value() {
    local name="$1"
    sed -n "s:.*<$name>\\([^<]*\\)</$name>.*:\\1:p" | head -n 1
}

post() {
    local title="$1"
    local path="$2"
    local body="$3"
    echo ""
    echo "$title POST $path"
    LAST_RESPONSE="$(curl -sS -X POST "$TARGET$path" -H "X-Serial-No: $(serial)" -H "$CT" -H "$ACCEPT" -d "$body")"
    printf '%s\n' "$LAST_RESPONSE" | head -c 900
    echo ""
}

echo "=========================================="
echo "Rental System API Sample Requests"
echo "TARGET=$TARGET"
echo "BASE=$BASE"
echo "COMPARE=$COMPARE"
echo "=========================================="

post "1." "/api/user/register" '<body><trans_code>USER001</trans_code><username>testuser</username><password>test123</password><real_name>Test User</real_name><phone>13800001006</phone><email>test@email.com</email><id_card>110101199506061239</id_card><driver_license>DL20240006</driver_license></body>'
post "2." "/api/user/login" '<body><trans_code>USER002</trans_code><username>zhangsan</username><password>pass123</password></body>'
post "3." "/api/user/query" '<body><trans_code>USER003</trans_code><user_id>1</user_id></body>'
post "4." "/api/user/update" '<body><trans_code>USER004</trans_code><user_id>1</user_id><phone>13800001999</phone><email>updated@email.com</email></body>'

post "5." "/api/vehicle/add" '<body><trans_code>VEH001</trans_code><plate_number>HU-B00001</plate_number><brand>BMW</brand><model>X5</model><color>Black</color><year>2024</year><seats>5</seats><displacement>3.0T</displacement><price_per_day>800.00</price_per_day><store_id>1</store_id><mileage>5000</mileage><insurance_expire>2027-12-31</insurance_expire></body>'
post "6." "/api/vehicle/query" '<body><trans_code>VEH002</trans_code><vehicle_id>1</vehicle_id></body>'
post "7." "/api/vehicle/update" '<body><trans_code>VEH003</trans_code><vehicle_id>1</vehicle_id><price_per_day>380.00</price_per_day><status>1</status></body>'
post "8." "/api/vehicle/delete" '<body><trans_code>VEH004</trans_code><vehicle_id>999</vehicle_id></body>'
post "9." "/api/vehicle/list" '<body><trans_code>VEH005</trans_code><store_id>1</store_id><status>1</status></body>'
post "10." "/api/vehicle/insurance" '<body><trans_code>VEH006</trans_code><vehicle_id>1</vehicle_id></body>'

post "11." "/api/store/add" '<body><trans_code>STO001</trans_code><store_name>Shanghai Pudong Store</store_name><address>No.100 Century Avenue, Pudong, Shanghai</address><phone>021-12345678</phone><business_hours>08:00-22:00</business_hours></body>'
post "12." "/api/store/query" '<body><trans_code>STO002</trans_code><store_id>1</store_id></body>'
post "13." "/api/store/list" '<body><trans_code>STO003</trans_code><status>1</status></body>'

post "14." "/api/order/create" '<body><trans_code>ORD001</trans_code><user_id>1</user_id><vehicle_id>1</vehicle_id><store_id>1</store_id><start_time>2026-04-29 10:00:00</start_time><end_time>2026-05-01 10:00:00</end_time></body>'
ORDER_NO="$(printf '%s' "$LAST_RESPONSE" | xml_value order_no)"
if [ -z "$ORDER_NO" ]; then
    echo "WARN: order/create did not return order_no; dependent order/payment samples will use a missing order."
    ORDER_NO="ORD_MISSING"
else
    echo "Captured ORDER_NO=$ORDER_NO"
fi

post "15." "/api/order/query" "<body><trans_code>ORD002</trans_code><order_no>$ORDER_NO</order_no></body>"
post "16." "/api/order/list" '<body><trans_code>ORD005</trans_code><user_id>1</user_id><status>1</status></body>'
post "17." "/api/order/calculate-fee" '<body><trans_code>ORD006</trans_code><vehicle_id>2</vehicle_id><start_time>2026-04-29 10:00:00</start_time><end_time>2026-05-01 10:00:00</end_time></body>'
post "18." "/api/order/detail" "<body><trans_code>ORD008</trans_code><order_no>$ORDER_NO</order_no></body>"
post "19." "/api/order/extend" "<body><trans_code>ORD007</trans_code><order_no>$ORDER_NO</order_no><new_end_time>2026-05-03 10:00:00</new_end_time></body>"

post "20." "/api/payment/create" "<body><trans_code>PAY001</trans_code><order_no>$ORDER_NO</order_no><amount>760.00</amount><payment_method>WECHAT</payment_method></body>"
PAYMENT_NO="$(printf '%s' "$LAST_RESPONSE" | xml_value payment_no)"
if [ -z "$PAYMENT_NO" ]; then
    echo "WARN: payment/create did not return payment_no; dependent payment samples will use a missing payment."
    PAYMENT_NO="PAY_MISSING"
else
    echo "Captured PAYMENT_NO=$PAYMENT_NO"
fi

post "21." "/api/payment/query" "<body><trans_code>PAY002</trans_code><payment_no>$PAYMENT_NO</payment_no></body>"
post "22." "/api/payment/callback" "<body><trans_code>PAY004</trans_code><payment_no>$PAYMENT_NO</payment_no><order_no>$ORDER_NO</order_no><status>2</status><gateway_trade_no>GT123456789</gateway_trade_no><pay_time>2026-04-29 10:05:00</pay_time></body>"
post "23." "/api/payment/reconcile" '<body><trans_code>PAY005</trans_code><reconcile_date>2026-04-29</reconcile_date></body>'
post "24." "/api/payment/refund" "<body><trans_code>PAY003</trans_code><payment_no>$PAYMENT_NO</payment_no><refund_amount>100.00</refund_amount><refund_reason>重复支付</refund_reason></body>"

post "25." "/api/order/create" '<body><trans_code>ORD001</trans_code><user_id>2</user_id><vehicle_id>2</vehicle_id><store_id>1</store_id><start_time>2026-04-29 11:00:00</start_time><end_time>2026-04-30 11:00:00</end_time></body>'
COMPLETE_ORDER_NO="$(printf '%s' "$LAST_RESPONSE" | xml_value order_no)"
if [ -z "$COMPLETE_ORDER_NO" ]; then
    echo "WARN: second order/create did not return order_no; order/complete will use a missing order."
    COMPLETE_ORDER_NO="ORD_MISSING"
else
    echo "Captured COMPLETE_ORDER_NO=$COMPLETE_ORDER_NO"
fi

post "26." "/api/order/complete" "<body><trans_code>ORD004</trans_code><order_no>$COMPLETE_ORDER_NO</order_no><actual_return_time>2026-04-30 11:00:00</actual_return_time><damage_desc></damage_desc></body>"
post "27." "/api/order/cancel" "<body><trans_code>ORD003</trans_code><order_no>$ORDER_NO</order_no><cancel_reason>行程取消</cancel_reason></body>"

post "28." "/api/statistics/daily" '<body><trans_code>STAT001</trans_code><store_id>1</store_id><stat_date>2026-04-29</stat_date></body>'
post "29." "/api/statistics/revenue" '<body><trans_code>STAT002</trans_code><start_date>2026-04-01</start_date><end_date>2026-04-30</end_date><store_id>1</store_id></body>'
post "30." "/api/statistics/utilization" '<body><trans_code>STAT003</trans_code><stat_date>2026-04-29</stat_date></body>'
post "31." "/api/statistics/user-report" '<body><trans_code>STAT004</trans_code><user_id>1</user_id><start_date>2026-04-01</start_date><end_date>2026-04-30</end_date></body>'

echo ""
echo "=========================================="
echo "Done. To hit compare:"
echo "  TARGET=$COMPARE ./send_samples.sh"
echo "=========================================="
