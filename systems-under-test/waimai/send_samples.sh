#!/bin/bash
BASE_URL="${1:-http://localhost:19091}"
ROUNDS="${2:-1}"
TXN_CODES=(PLACE_ORDER CONFIRM_ORDER CANCEL_ORDER QUERY_ORDER APPLY_REFUND SEARCH_MERCHANT MERCHANT_DETAIL ADD_CART QUERY_CART SUBMIT_REVIEW RIDER_LOCATION RECHARGE_WALLET WITHDRAW_WALLET QUERY_WALLET MERCHANT_SETTLE LIST_CATEGORIES LIST_PRODUCTS PRODUCT_DETAIL LIST_ADDRESS SAVE_ADDRESS LIST_COUPONS CLAIM_COUPON RIDER_LIST QUERY_DELIVERY COMPLAINT_SUBMIT COMPLAINT_DETAIL NOTIFICATION_LIST SYSTEM_CONFIG VERSION_CHECK FEEDBACK_SUBMIT)
echo "Sending ${#TXN_CODES[@]} txn x $ROUNDS rounds to $BASE_URL"
for r in $(seq 1 $ROUNDS); do echo "=== Round $r ==="; for txn in "${TXN_CODES[@]}"; do curl -s -X POST "$BASE_URL/waimai/gateway/json" -H "Content-Type: application/json" -d \"{\\\"txnCode\\\":\\\"$txn\\\",\\\"params\\\":{\\\"customerId\\\":\\\"C001\\\",\\\"merchantId\\\":\\\"M001\\\",\\\"orderId\\\":\\\"ORD_0000$r\\\",\\\"productId\\\":\\\"P001\\\",\\\"basePrice\\\":\\\"30.0\\\",\\\"originalAmount\\\":\\\"50.0\\\",\\\"riderId\\\":\\\"R001\\\"}}\" | /usr/bin/python3.6 -m json.tool 2>/dev/null | head -5; echo "  [$txn] done"; done; done
echo "All done!"
