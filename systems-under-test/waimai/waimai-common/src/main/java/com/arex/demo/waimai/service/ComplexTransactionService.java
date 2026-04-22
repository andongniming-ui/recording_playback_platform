package com.arex.demo.waimai.service;
import com.arex.demo.waimai.config.WaimaiVariantProperties;
import com.arex.demo.waimai.repository.WaimaiDataRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.util.*;

@Service
public class ComplexTransactionService {
    private static final Logger log = LoggerFactory.getLogger(ComplexTransactionService.class);
    @Autowired private WaimaiDataRepository repo;
    @Autowired private WaimaiVariantProperties variant;
    @Autowired private RestTemplate restTemplate;

    public Map<String,Object> process(String txnCode, Map<String,String> p) {
        log.info("[{}] ComplexTxn start, txnCode={}, variant={}, request={}", TraceContext.getTraId(), txnCode, variant.getLabel(), p);
        Map<String,Object> data = new LinkedHashMap<>();
        data.put("txnCode", txnCode); data.put("greeting", variant.getGreeting());
        try {
            switch(txnCode) {
                case "PLACE_ORDER": data.putAll(placeOrder(p)); break;
                case "CONFIRM_ORDER": data.putAll(confirmOrder(p)); break;
                case "CANCEL_ORDER": data.putAll(cancelOrder(p)); break;
                case "QUERY_ORDER": data.putAll(queryOrder(p)); break;
                case "APPLY_REFUND": data.putAll(applyRefund(p)); break;
                case "SEARCH_MERCHANT": data.putAll(searchMerchant(p)); break;
                case "MERCHANT_DETAIL": data.putAll(merchantDetail(p)); break;
                case "ADD_CART": data.putAll(addCart(p)); break;
                case "QUERY_CART": data.putAll(queryCart(p)); break;
                case "SUBMIT_REVIEW": data.putAll(submitReview(p)); break;
                case "RIDER_LOCATION": data.putAll(riderLocation(p)); break;
                case "RECHARGE_WALLET": data.putAll(rechargeWallet(p)); break;
                case "WITHDRAW_WALLET": data.putAll(withdrawWallet(p)); break;
                case "QUERY_WALLET": data.putAll(queryWallet(p)); break;
                case "MERCHANT_SETTLE": data.putAll(merchantSettle(p)); break;
                default: data.put("result","UNKNOWN_COMPLEX_TXN");
            }
        } catch(Exception e) { log.error("[{}] ComplexTxn error: {}", TraceContext.getTraId(), e.getMessage(), e); data.put("error",e.getMessage()); }
        data.put("orderConfirmMsg", variant.getOrderConfirmMsg());
        log.info("[{}] ComplexTxn response, txnCode={}, body={}", TraceContext.getTraId(), txnCode, data);
        return data;
    }

    private String subCall(String path, Map<String,String> p) {
        int port = Integer.parseInt(System.getProperty("server.port","19091"));
        String url = "http://localhost:"+port+path;
        try {
            log.info("[{}] Sub-call request, path={}, body={}", TraceContext.getTraId(), path, p);
            @SuppressWarnings("unchecked") Map<String,Object> resp = restTemplate.postForObject(url, p, Map.class);
            log.info("[{}] Sub-call response, path={}, status={}, body={}",
                TraceContext.getTraId(),
                path,
                resp!=null?resp.get("status"):"null",
                resp);
            return resp!=null?String.valueOf(resp.get("data")):"null";
        } catch(Exception e) {
            log.warn("[{}] Sub-call failed, path={}, url={}, error={}", TraceContext.getTraId(), path, url, e.getMessage());
            return "sub_call_failed";
        }
    }

    private Map<String,Object> placeOrder(Map<String,String> p) {
        String oid="ORD_"+System.currentTimeMillis()%100000; repo.insertOrder(oid,p.getOrDefault("customerId","C001"),p.getOrDefault("merchantId","M001"),"CREATED");
        Map<String,Object> r=new LinkedHashMap<>(); r.put("orderId",oid); r.put("pricingResult",subCall("/waimai/internal/pricing",p));
        r.put("discountResult",subCall("/waimai/internal/discount",p)); r.put("riskResult",subCall("/waimai/internal/risk",p)); return r;
    }
    private Map<String,Object> confirmOrder(Map<String,String> p) {
        String oid=p.getOrDefault("orderId","ORD_00001"); repo.updateOrderStatus(oid,"CONFIRMED"); repo.decrementStock(p.getOrDefault("productId","P001"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("orderId",oid); r.put("status","CONFIRMED"); r.put("riskResult",subCall("/waimai/internal/risk",p)); return r;
    }
    private Map<String,Object> cancelOrder(Map<String,String> p) {
        String oid=p.getOrDefault("orderId","ORD_00001"); repo.updateOrderStatus(oid,"CANCELLED"); repo.incrementStock(p.getOrDefault("productId","P001"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("orderId",oid); r.put("status","CANCELLED"); r.put("refundStatus","PROCESSING"); return r;
    }
    private Map<String,Object> queryOrder(Map<String,String> p) {
        Map<String,Object> order=repo.queryOrder(p.getOrDefault("orderId","ORD_00001"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("order",order!=null?order:Collections.singletonMap("orderId","not_found"));
        r.put("deliveryEstimate",subCall("/waimai/internal/delivery-time",p)); return r;
    }
    private Map<String,Object> applyRefund(Map<String,String> p) {
        String rid="REF_"+System.currentTimeMillis()%100000; repo.insertRefund(rid,p.getOrDefault("orderId","ORD_00001"),"PENDING");
        Map<String,Object> r=new LinkedHashMap<>(); r.put("refundId",rid); r.put("riskResult",subCall("/waimai/internal/risk",p)); return r;
    }
    private Map<String,Object> searchMerchant(Map<String,String> p) {
        List<Map<String,Object>> ms=repo.searchMerchants(p.getOrDefault("keyword","快餐"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("merchants",ms); r.put("pricingHint",subCall("/waimai/internal/pricing",p)); return r;
    }
    private Map<String,Object> merchantDetail(Map<String,String> p) {
        Map<String,Object> m=repo.queryMerchant(p.getOrDefault("merchantId","M001"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("merchant",m!=null?m:Collections.singletonMap("name","not_found"));
        r.put("discountHint",subCall("/waimai/internal/discount",p)); return r;
    }
    private Map<String,Object> addCart(Map<String,String> p) {
        repo.addToCart(p.getOrDefault("customerId","C001"),p.getOrDefault("productId","P001"),p.getOrDefault("quantity","1"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("cartAdded","true"); r.put("pricingHint",subCall("/waimai/internal/pricing",p)); return r;
    }
    private Map<String,Object> queryCart(Map<String,String> p) {
        List<Map<String,Object>> cart=repo.queryCart(p.getOrDefault("customerId","C001"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("cartItems",cart); r.put("discountHint",subCall("/waimai/internal/discount",p)); return r;
    }
    private Map<String,Object> submitReview(Map<String,String> p) {
        String rid="REV_"+System.currentTimeMillis()%100000; repo.insertReview(rid,p.getOrDefault("orderId","ORD_00001"),p.getOrDefault("rating","5"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("reviewId",rid); r.put("riskResult",subCall("/waimai/internal/risk",p)); return r;
    }
    private Map<String,Object> riderLocation(Map<String,String> p) {
        Map<String,Object> loc=repo.queryRiderLocation(p.getOrDefault("riderId","R001"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("riderLocation",loc!=null?loc:Collections.singletonMap("lat","0"));
        r.put("deliveryEstimate",subCall("/waimai/internal/delivery-time",p)); return r;
    }
    private Map<String,Object> rechargeWallet(Map<String,String> p) {
        repo.updateWallet(p.getOrDefault("customerId","C001"),Double.parseDouble(p.getOrDefault("amount","100")));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("rechargeStatus","SUCCESS"); r.put("riskResult",subCall("/waimai/internal/risk",p)); return r;
    }
    private Map<String,Object> withdrawWallet(Map<String,String> p) {
        repo.updateWallet(p.getOrDefault("customerId","C001"),-Double.parseDouble(p.getOrDefault("amount","50")));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("withdrawStatus","SUCCESS"); r.put("riskResult",subCall("/waimai/internal/risk",p)); return r;
    }
    private Map<String,Object> queryWallet(Map<String,String> p) {
        Map<String,Object> wallet=repo.queryWallet(p.getOrDefault("customerId","C001"));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("wallet",wallet!=null?wallet:Collections.singletonMap("balance","0"));
        r.put("reconciliation",variant.isReconciliationExtra()?"EXTRA_CHECK":"STANDARD"); return r;
    }
    private Map<String,Object> merchantSettle(Map<String,String> p) {
        String sid="STL_"+System.currentTimeMillis()%100000; repo.insertSettlement(sid,p.getOrDefault("merchantId","M001"),Double.parseDouble(p.getOrDefault("amount","1000")));
        Map<String,Object> r=new LinkedHashMap<>(); r.put("settlementId",sid);
        r.put("reconciliation",variant.isReconciliationExtra()?"EXTRA_CHECK":"STANDARD"); return r;
    }
}
