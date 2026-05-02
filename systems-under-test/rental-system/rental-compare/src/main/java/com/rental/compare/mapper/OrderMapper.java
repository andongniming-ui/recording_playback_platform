package com.rental.compare.mapper;

import com.rental.common.model.RentalOrder;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.Date;
import java.util.List;

@Repository
public class OrderMapper {
    private final JdbcTemplate jdbc;
    public OrderMapper(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    private final RowMapper<RentalOrder> rowMapper = (rs, rn) -> {
        RentalOrder o = new RentalOrder();
        o.setId(rs.getLong("id"));
        o.setOrderNo(rs.getString("order_no"));
        o.setUserId(rs.getLong("user_id"));
        o.setVehicleId(rs.getLong("vehicle_id"));
        o.setStoreId(rs.getLong("store_id"));
        o.setStartTime(rs.getTimestamp("start_time"));
        o.setEndTime(rs.getTimestamp("end_time"));
        o.setEstimatedFee(rs.getBigDecimal("estimated_fee"));
        o.setDeposit(rs.getBigDecimal("deposit"));
        o.setActualFee(rs.getBigDecimal("actual_fee"));
        o.setStatus(rs.getInt("status"));
        o.setCreateTime(rs.getTimestamp("create_time"));
        o.setUpdateTime(rs.getTimestamp("update_time"));
        return o;
    };

    public int insert(RentalOrder o) {
        return jdbc.update(
            "INSERT INTO rental_order (order_no,user_id,vehicle_id,store_id,start_time,end_time,estimated_fee,deposit,actual_fee,status,create_time,update_time) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            o.getOrderNo(), o.getUserId(), o.getVehicleId(), o.getStoreId(),
            o.getStartTime(), o.getEndTime(), o.getEstimatedFee(), o.getDeposit(), o.getActualFee(),
            o.getStatus() != null ? o.getStatus() : 1, new Date(), new Date()
        );
    }

    public RentalOrder findByOrderNo(String orderNo) {
        List<RentalOrder> list = jdbc.query("SELECT * FROM rental_order WHERE order_no=?", rowMapper, orderNo);
        return list.isEmpty() ? null : list.get(0);
    }

    public List<RentalOrder> findByUserId(Long userId, Integer status) {
        if (status != null) {
            return jdbc.query("SELECT * FROM rental_order WHERE user_id=? AND status=? ORDER BY create_time DESC", rowMapper, userId, status);
        }
        return jdbc.query("SELECT * FROM rental_order WHERE user_id=? ORDER BY create_time DESC", rowMapper, userId);
    }

    public List<RentalOrder> findByStatus(Integer status) {
        return jdbc.query("SELECT * FROM rental_order WHERE status=? ORDER BY create_time", rowMapper, status);
    }

    public int updateStatus(String orderNo, Integer status) {
        return jdbc.update("UPDATE rental_order SET status=?,update_time=? WHERE order_no=?",
            status, new Date(), orderNo);
    }

    public int update(RentalOrder o) {
        return jdbc.update(
            "UPDATE rental_order SET end_time=?,estimated_fee=?,deposit=?,actual_fee=?,status=?,update_time=? WHERE order_no=?",
            o.getEndTime(), o.getEstimatedFee(), o.getDeposit(), o.getActualFee(),
            o.getStatus(), new Date(), o.getOrderNo()
        );
    }

    public List<RentalOrder> findByDateRange(Date start, Date end) {
        return jdbc.query("SELECT * FROM rental_order WHERE create_time BETWEEN ? AND ? ORDER BY create_time",
            rowMapper, start, end);
    }

    public List<RentalOrder> findByStoreAndDateRange(Long storeId, Date start, Date end) {
        return jdbc.query("SELECT * FROM rental_order WHERE store_id=? AND create_time BETWEEN ? AND ? ORDER BY create_time",
            rowMapper, storeId, start, end);
    }

    public int countByDate(Date date) {
        java.util.Calendar cal = java.util.Calendar.getInstance();
        cal.setTime(date);
        cal.set(java.util.Calendar.HOUR_OF_DAY, 0);
        cal.set(java.util.Calendar.MINUTE, 0);
        cal.set(java.util.Calendar.SECOND, 0);
        Date start = cal.getTime();
        cal.add(java.util.Calendar.DAY_OF_MONTH, 1);
        Date end = cal.getTime();
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM rental_order WHERE create_time>=? AND create_time<?",
            Integer.class, start, end);
        return count != null ? count : 0;
    }
}
