package com.arex.demo.waimai.repository;
import com.arex.demo.waimai.service.TraceContext;
import org.slf4j.Logger; import org.slf4j.LoggerFactory; import org.springframework.beans.factory.annotation.Autowired; import org.springframework.jdbc.core.JdbcTemplate; import org.springframework.stereotype.Repository;
import java.util.*;
@Repository
public class WaimaiDataRepository {
    private static final Logger log = LoggerFactory.getLogger(WaimaiDataRepository.class);
    @Autowired private JdbcTemplate jdbc;

    public int insertOrder(String oid,String cid,String mid,String st) {
        int rows = jdbc.update("INSERT INTO orders(order_id,customer_id,merchant_id,status,created_at) VALUES(?,?,?,?,NOW())",oid,cid,mid,st);
        log.info("[{}] DB insertOrder, sql=INSERT INTO orders..., params={{orderId={}, customerId={}, merchantId={}, status={}}}, affectedRows={}", TraceContext.getTraId(), oid, cid, mid, st, rows);
        return rows;
    }
    public int updateOrderStatus(String oid,String st) {
        int rows = jdbc.update("UPDATE orders SET status=? WHERE order_id=?",st,oid);
        log.info("[{}] DB updateOrder, sql=UPDATE orders SET status=? WHERE order_id=?, params={{status={}, orderId={}}}, affectedRows={}", TraceContext.getTraId(), st, oid, rows);
        return rows;
    }
    public Map<String,Object> queryOrder(String oid) {
        List<Map<String,Object>> r=jdbc.queryForList("SELECT * FROM orders WHERE order_id=?",oid);
        Map<String,Object> result = r.isEmpty()?null:r.get(0);
        log.info("[{}] DB queryOrder, sql=SELECT * FROM orders WHERE order_id=?, params={{orderId={}}}, result={}", TraceContext.getTraId(), oid, result);
        return result;
    }
    public int decrementStock(String pid) {
        int rows = jdbc.update("UPDATE products SET stock=stock-1 WHERE product_id=?",pid);
        log.info("[{}] DB decStock, sql=UPDATE products SET stock=stock-1 WHERE product_id=?, params={{productId={}}}, affectedRows={}", TraceContext.getTraId(), pid, rows);
        return rows;
    }
    public int incrementStock(String pid) {
        int rows = jdbc.update("UPDATE products SET stock=stock+1 WHERE product_id=?",pid);
        log.info("[{}] DB incStock, sql=UPDATE products SET stock=stock+1 WHERE product_id=?, params={{productId={}}}, affectedRows={}", TraceContext.getTraId(), pid, rows);
        return rows;
    }
    public int insertRefund(String rid,String oid,String st) {
        int rows = jdbc.update("INSERT INTO refunds(refund_id,order_id,status,created_at) VALUES(?,?,?,NOW())",rid,oid,st);
        log.info("[{}] DB insertRefund, sql=INSERT INTO refunds..., params={{refundId={}, orderId={}, status={}}}, affectedRows={}", TraceContext.getTraId(), rid, oid, st, rows);
        return rows;
    }
    public List<Map<String,Object>> searchMerchants(String kw) {
        List<Map<String,Object>> result = jdbc.queryForList("SELECT * FROM merchants WHERE name LIKE ?","%"+kw+"%");
        log.info("[{}] DB searchMerchants, sql=SELECT * FROM merchants WHERE name LIKE ?, params={{keyword={}}}, resultSize={}, result={}", TraceContext.getTraId(), kw, result.size(), result);
        return result;
    }
    public Map<String,Object> queryMerchant(String mid) {
        List<Map<String,Object>> r=jdbc.queryForList("SELECT * FROM merchants WHERE merchant_id=?",mid);
        Map<String,Object> result = r.isEmpty()?null:r.get(0);
        log.info("[{}] DB queryMerchant, sql=SELECT * FROM merchants WHERE merchant_id=?, params={{merchantId={}}}, result={}", TraceContext.getTraId(), mid, result);
        return result;
    }
    public int addToCart(String cid,String pid,String qty) {
        int rows = jdbc.update("INSERT INTO cart(customer_id,product_id,quantity,added_at) VALUES(?,?,?,NOW())",cid,pid,Integer.parseInt(qty));
        log.info("[{}] DB addToCart, sql=INSERT INTO cart..., params={{customerId={}, productId={}, quantity={}}}, affectedRows={}", TraceContext.getTraId(), cid, pid, qty, rows);
        return rows;
    }
    public List<Map<String,Object>> queryCart(String cid) {
        List<Map<String,Object>> result = jdbc.queryForList("SELECT * FROM cart WHERE customer_id=?",cid);
        log.info("[{}] DB queryCart, sql=SELECT * FROM cart WHERE customer_id=?, params={{customerId={}}}, resultSize={}, result={}", TraceContext.getTraId(), cid, result.size(), result);
        return result;
    }
    public int insertReview(String rid,String oid,String rating) {
        int rows = jdbc.update("INSERT INTO reviews(review_id,order_id,rating,created_at) VALUES(?,?,?,NOW())",rid,oid,Integer.parseInt(rating));
        log.info("[{}] DB insertReview, sql=INSERT INTO reviews..., params={{reviewId={}, orderId={}, rating={}}}, affectedRows={}", TraceContext.getTraId(), rid, oid, rating, rows);
        return rows;
    }
    public Map<String,Object> queryRiderLocation(String rid) {
        List<Map<String,Object>> r=jdbc.queryForList("SELECT * FROM riders WHERE rider_id=?",rid);
        Map<String,Object> result = r.isEmpty()?null:r.get(0);
        log.info("[{}] DB queryRiderLoc, sql=SELECT * FROM riders WHERE rider_id=?, params={{riderId={}}}, result={}", TraceContext.getTraId(), rid, result);
        return result;
    }
    public int updateWallet(String cid,double amt) {
        int rows = jdbc.update("UPDATE wallets SET balance=balance+?,updated_at=NOW() WHERE customer_id=?",amt,cid);
        log.info("[{}] DB updateWallet, sql=UPDATE wallets SET balance=balance+?,updated_at=NOW() WHERE customer_id=?, params={{customerId={}, amount={}}}, affectedRows={}", TraceContext.getTraId(), cid, amt, rows);
        return rows;
    }
    public Map<String,Object> queryWallet(String cid) {
        List<Map<String,Object>> r=jdbc.queryForList("SELECT * FROM wallets WHERE customer_id=?",cid);
        Map<String,Object> result = r.isEmpty()?null:r.get(0);
        log.info("[{}] DB queryWallet, sql=SELECT * FROM wallets WHERE customer_id=?, params={{customerId={}}}, result={}", TraceContext.getTraId(), cid, result);
        return result;
    }
    public int insertSettlement(String sid,String mid,double amt) {
        int rows = jdbc.update("INSERT INTO settlements(settlement_id,merchant_id,amount,status,created_at) VALUES(?,?,?,\'COMPLETED\',NOW())",sid,mid,amt);
        log.info("[{}] DB insertSettle, sql=INSERT INTO settlements..., params={{settlementId={}, merchantId={}, amount={}}}, affectedRows={}", TraceContext.getTraId(), sid, mid, amt, rows);
        return rows;
    }
}
