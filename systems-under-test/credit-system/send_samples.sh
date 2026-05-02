#!/bin/bash
set -e

BASE_URL="${1:-http://127.0.0.1:29081}"

send() {
  local name="$1"
  local xml="$2"
  echo ">>> ${name}"
  curl -sS -H 'Content-Type: application/xml' -d "${xml}" "${BASE_URL}/credit/gateway"
  echo
  echo
}

send "CRD_ADMIT C10001 P001" \
'<request><txn_code>CRD_ADMIT</txn_code><tra_id>202604240001001</tra_id><request_time>20260424000100123</request_time><request_no>REQ-ADMIT-0001</request_no><customer_id>C10001</customer_id><product_id>P001</product_id><id_no>310101199001011234</id_no><mobile>13800000001</mobile><apply_amount>80000</apply_amount><apply_term>12</apply_term><apply_city>SHANGHAI</apply_city></request>'

send "CRD_LIMIT C10001 P001" \
'<request><txn_code>CRD_LIMIT</txn_code><tra_id>202604240001002</tra_id><request_time>20260424000100223</request_time><request_no>REQ-LIMIT-0001</request_no><customer_id>C10001</customer_id><product_id>P001</product_id><apply_amount>80000</apply_amount><apply_term>12</apply_term></request>'

send "CRD_ADMIT C10003 P001" \
'<request><txn_code>CRD_ADMIT</txn_code><tra_id>202604240001003</tra_id><request_time>20260424000100323</request_time><request_no>REQ-ADMIT-0003</request_no><customer_id>C10003</customer_id><product_id>P001</product_id><id_no>310101200301011234</id_no><mobile>13800000003</mobile><apply_amount>50000</apply_amount><apply_term>12</apply_term><apply_city>SHANGHAI</apply_city></request>'

send "CRD_LIMIT C10005 P002" \
'<request><txn_code>CRD_LIMIT</txn_code><tra_id>202604240001004</tra_id><request_time>20260424000100423</request_time><request_no>REQ-LIMIT-0005</request_no><customer_id>C10005</customer_id><product_id>P002</product_id><apply_amount>120000</apply_amount><apply_term>12</apply_term></request>'

send "CRD_ADMIT C10007 P001" \
'<request><txn_code>CRD_ADMIT</txn_code><tra_id>202604240001005</tra_id><request_time>20260424000100523</request_time><request_no>REQ-ADMIT-0007</request_no><customer_id>C10007</customer_id><product_id>P001</product_id><id_no>310101198401011234</id_no><mobile>13800000007</mobile><apply_amount>60000</apply_amount><apply_term>12</apply_term><apply_city>SHANGHAI</apply_city></request>'
