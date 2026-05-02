package com.rental.compare.mapper;

import com.rental.common.model.RentalPayment;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.Date;
import java.util.List;

@Repository
public class PaymentMapper {
    private final JdbcTemplate jdbc;
    public PaymentMapper(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    private final RowMapper<RentalPayment> rowMapper = (rs, rn) -> {
        RentalPayment p = new RentalPayment();
        p.setId(rs.getLong("id"));
        p.setPaymentNo(rs.getString("payment_no"));
        p.setOrderNo(rs.getString("order_no"));
        p.setAmount(rs.getBigDecimal("amount"));
        p.setChannel(rs.getString("channel"));
        p.setPaymentMethod(rs.getString("payment_method"));
        p.setStatus(rs.getInt("status"));
        p.setPayTime(rs.getTimestamp("pay_time"));
        p.setCreateTime(rs.getTimestamp("create_time"));
        p.setUpdateTime(rs.getTimestamp("update_time"));
        return p;
    };

    public int insert(RentalPayment p) {
        return jdbc.update(
            "INSERT INTO rental_payment (payment_no,order_no,amount,channel,payment_method,status,pay_time,create_time,update_time) VALUES (?,?,?,?,?,?,?,?,?)",
            p.getPaymentNo(), p.getOrderNo(), p.getAmount(), p.getChannel(),
            p.getPaymentMethod(), p.getStatus() != null ? p.getStatus() : 1,
            p.getPayTime(), new Date(), new Date()
        );
    }

    public RentalPayment findByPaymentNo(String paymentNo) {
        List<RentalPayment> list = jdbc.query("SELECT * FROM rental_payment WHERE payment_no=?", rowMapper, paymentNo);
        return list.isEmpty() ? null : list.get(0);
    }

    public RentalPayment findByOrderNo(String orderNo) {
        List<RentalPayment> list = jdbc.query("SELECT * FROM rental_payment WHERE order_no=? ORDER BY create_time DESC", rowMapper, orderNo);
        return list.isEmpty() ? null : list.get(0);
    }

    public int updateStatus(String paymentNo, Integer status) {
        return jdbc.update("UPDATE rental_payment SET status=?,pay_time=?,update_time=? WHERE payment_no=?",
            status, status == 2 ? new Date() : null, new Date(), paymentNo);
    }

    public List<RentalPayment> findByDateRange(Date start, Date end) {
        return jdbc.query("SELECT * FROM rental_payment WHERE create_time BETWEEN ? AND ? ORDER BY create_time",
            rowMapper, start, end);
    }
}
