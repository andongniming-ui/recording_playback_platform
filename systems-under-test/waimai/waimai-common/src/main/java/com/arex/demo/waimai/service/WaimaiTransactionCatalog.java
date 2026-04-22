package com.arex.demo.waimai.service;
import com.arex.demo.waimai.model.TxnDefinition;
import org.springframework.stereotype.Component;
import java.util.*;

@Component
public class WaimaiTransactionCatalog {
    private final Map<String,TxnDefinition> catalog = new LinkedHashMap<>();
    public WaimaiTransactionCatalog() {
        add("PLACE_ORDER","下单","COMPLEX","创建订单+子调用定价/优惠/风控");
        add("CONFIRM_ORDER","确认订单","COMPLEX","确认支付+扣库存+记账");
        add("CANCEL_ORDER","取消订单","COMPLEX","取消+退款+库存回滚");
        add("QUERY_ORDER","查询订单","COMPLEX","DB查询+调配送预估");
        add("APPLY_REFUND","申请退款","COMPLEX","退款审核+风控校验");
        add("SEARCH_MERCHANT","搜索商户","COMPLEX","DB搜索+调定价接口");
        add("MERCHANT_DETAIL","商户详情","COMPLEX","DB查询+调优惠接口");
        add("ADD_CART","加入购物车","COMPLEX","DB写入+调定价接口");
        add("QUERY_CART","查询购物车","COMPLEX","DB查询+调优惠接口");
        add("SUBMIT_REVIEW","提交评价","COMPLEX","DB写入+风控校验");
        add("RIDER_LOCATION","骑手位置","COMPLEX","DB查询+配送预估");
        add("RECHARGE_WALLET","钱包充值","COMPLEX","DB写入+风控+记账");
        add("WITHDRAW_WALLET","钱包提现","COMPLEX","DB写入+风控+记账");
        add("QUERY_WALLET","查询钱包","COMPLEX","DB查询+对账校验");
        add("MERCHANT_SETTLE","商户结算","COMPLEX","DB写入+对账+记账");
        add("LIST_CATEGORIES","分类列表","SIMPLE","直接返回分类");
        add("LIST_PRODUCTS","商品列表","SIMPLE","直接返回商品");
        add("PRODUCT_DETAIL","商品详情","SIMPLE","直接返回详情");
        add("LIST_ADDRESS","地址列表","SIMPLE","直接返回地址");
        add("SAVE_ADDRESS","保存地址","SIMPLE","直接保存");
        add("LIST_COUPONS","优惠券列表","SIMPLE","直接返回优惠券");
        add("CLAIM_COUPON","领取优惠券","SIMPLE","直接领取");
        add("RIDER_LIST","骑手列表","SIMPLE","直接返回骑手");
        add("QUERY_DELIVERY","查询配送","SIMPLE","直接返回配送");
        add("COMPLAINT_SUBMIT","提交投诉","SIMPLE","直接提交");
        add("COMPLAINT_DETAIL","投诉详情","SIMPLE","直接返回详情");
        add("NOTIFICATION_LIST","通知列表","SIMPLE","直接返回通知");
        add("SYSTEM_CONFIG","系统配置","SIMPLE","直接返回配置");
        add("VERSION_CHECK","版本检查","SIMPLE","直接返回版本");
        add("FEEDBACK_SUBMIT","提交反馈","SIMPLE","直接提交");
    }
    private void add(String c,String n,String t,String d) { catalog.put(c, new TxnDefinition(c,n,t,d)); }
    public TxnDefinition get(String txnCode) { return catalog.get(txnCode); }
    public boolean isComplex(String txnCode) { TxnDefinition d=catalog.get(txnCode); return d!=null&&"COMPLEX".equals(d.getType()); }
    public Collection<TxnDefinition> all() { return catalog.values(); }
}
