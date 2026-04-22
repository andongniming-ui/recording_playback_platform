package com.arex.demo.waimai.service;
import com.arex.demo.waimai.config.WaimaiVariantProperties;
import com.arex.demo.waimai.model.GatewayResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import java.util.*;

@Service
public class WaimaiGatewayService {
    private static final Logger log = LoggerFactory.getLogger(WaimaiGatewayService.class);
    @Autowired private XmlPayloadService xmlPayloadService;
    @Autowired private WaimaiTransactionCatalog catalog;
    @Autowired private ComplexTransactionService complexTxnService;
    @Autowired private WaimaiVariantProperties variant;

    public String handleXmlRequest(String xmlBody) {
        String txnCode = xmlPayloadService.extractTxnCode(xmlBody);
        Map<String,String> params = xmlPayloadService.extractParams(xmlBody);
        log.info("[{}] Parsed XML txnCode={}, paramCount={}", TraceContext.getTraId(), txnCode, params.size());
        Map<String,Object> data = process(txnCode, params);
        return xmlPayloadService.buildResponse(txnCode, data);
    }
    public GatewayResult handleJsonRequest(String txnCode, Map<String,String> params) {
        log.info("[{}] JSON txnCode={}", TraceContext.getTraId(), txnCode);
        Map<String,Object> data = process(txnCode, params);
        return GatewayResult.ok(txnCode, data);
    }
    private Map<String,Object> process(String txnCode, Map<String,String> params) {
        log.info("[{}] Processing txnCode={}, variant={}", TraceContext.getTraId(), txnCode, variant.getLabel());
        if(!catalog.isComplex(txnCode)) return processSimple(txnCode, params);
        return complexTxnService.process(txnCode, params);
    }
    private Map<String,Object> processSimple(String txnCode, Map<String,String> params) {
        Map<String,Object> data = new LinkedHashMap<>();
        data.put("txnCode", txnCode); data.put("greeting", variant.getGreeting());
        switch(txnCode) {
            case "LIST_CATEGORIES": data.put("categories",Arrays.asList("快餐","火锅","奶茶","烧烤")); break;
            case "LIST_PRODUCTS": data.put("products",Arrays.asList("宫保鸡丁","水煮鱼","麻婆豆腐")); break;
            case "PRODUCT_DETAIL": data.put("productName",params.getOrDefault("productName","宫保鸡丁")); data.put("price","32.00"); break;
            case "LIST_ADDRESS": data.put("addresses",Arrays.asList("北京市朝阳区xx路","北京市海淀区yy路")); break;
            case "SAVE_ADDRESS": data.put("saved","true"); data.put("addressId","ADDR_"+System.currentTimeMillis()%10000); break;
            case "LIST_COUPONS": data.put("coupons",Arrays.asList("满30减5","新用户立减10")); break;
            case "CLAIM_COUPON": data.put("claimed","true"); data.put("couponId","CPN_"+System.currentTimeMillis()%10000); break;
            case "RIDER_LIST": data.put("riders",Arrays.asList("骑手张三","骑手李四")); break;
            case "QUERY_DELIVERY": data.put("status","配送中"); data.put("eta","15分钟"); break;
            case "COMPLAINT_SUBMIT": data.put("complaintId","CPT_"+System.currentTimeMillis()%10000); data.put("status","已提交"); break;
            case "COMPLAINT_DETAIL": data.put("complaintId",params.getOrDefault("complaintId","CPT_0001")); data.put("result","处理中"); break;
            case "NOTIFICATION_LIST": data.put("notifications",Arrays.asList("您的订单已接单","骑手已取餐")); break;
            case "SYSTEM_CONFIG": data.put("config",Collections.singletonMap("minOrderAmount","20")); break;
            case "VERSION_CHECK": data.put("latestVersion","3.2.1"); data.put("needUpdate","false"); break;
            case "FEEDBACK_SUBMIT": data.put("feedbackId","FB_"+System.currentTimeMillis()%10000); data.put("status","已提交"); break;
            default: data.put("result","UNKNOWN_TXN");
        }
        data.put("orderConfirmMsg", variant.getOrderConfirmMsg());
        return data;
    }
}
