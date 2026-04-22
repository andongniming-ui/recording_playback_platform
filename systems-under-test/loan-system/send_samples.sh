#!/bin/bash
BASE_URL="${1:-http://localhost:28081}"
ROUNDS="${2:-1}"

echo "=== Loan System Sample Requests ==="
echo "Target: $BASE_URL | Rounds: $ROUNDS"

TXN_CODES=("LOAN_QUALIFY" "LOAN_CREDIT" "LOAN_INCOME" "LOAN_QUOTA" "LOAN_ADMIT")
CUSTOMERS=("C001" "C002" "C003" "C004" "C005" "C006" "C007" "C008" "C009" "C010")
PRODUCTS=("P001")

for r in $(seq 1 $ROUNDS); do
    echo ""
    echo "=== Round $r ==="
    for txn in "${TXN_CODES[@]}"; do
        for cust in "${CUSTOMERS[@]}"; do
            for prod in "${PRODUCTS[@]}"; do
                echo -n "  [$txn] customer=$cust product=$prod => "
                curl -s -X POST "$BASE_URL/loan/gateway/json"                     -H "Content-Type: application/json"                     -d "{\"txnCode\":\"$txn\",\"params\":{\"customerId\":\"$cust\",\"productId\":\"$prod\"}}"                     | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status','?'), '|', d.get('elapsed','?'), 'ms', '|', str(d.get('body',{}))[:80])" 2>/dev/null || echo "FAILED"
            done
        done
    done
done
echo ""
echo "=== Done ==="
