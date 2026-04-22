#!/usr/bin/env bash
set -e

BASE_URL=${1:-http://127.0.0.1:18081}
ENDPOINT="$BASE_URL/api/car/service"

build_field_name() {
  case "$1" in
    car000001|car000002|car000003|car000004|car000005|car000016|car000017|car000018|car000019|car000020)
      echo "code"
      ;;
    car000006|car000007|car000008|car000009|car000010|car000021|car000022|car000023|car000024|car000025)
      echo "trs_code"
      ;;
    car000011|car000012|car000013|car000026|car000027|car000028)
      echo "service_code"
      ;;
    *)
      echo "biz_code"
      ;;
  esac
}

for i in $(seq 1 30); do
  CODE=$(printf "car%06d" "$i")
  FIELD=$(build_field_name "$CODE")
  XML=$(cat <<EOF
<request>
  <${FIELD}>${CODE}</${FIELD}>
  <request_no>REQ-${CODE}</request_no>
  <customer_no>C10001</customer_no>
  <plate_no>沪A10001</plate_no>
  <vin>VIN0000000000000001</vin>
  <policy_no>P10001</policy_no>
  <claim_no>CL10001</claim_no>
  <garage_code>G001</garage_code>
  <city>SHANGHAI</city>
</request>
EOF
)
  echo ">>> ${CODE}"
  curl -sS -H 'Content-Type: application/xml' -d "$XML" "$ENDPOINT"
  printf '\n'
done
