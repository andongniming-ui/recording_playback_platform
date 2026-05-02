package com.rental.base.mapper;

import com.rental.common.model.RentalStore;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.Date;
import java.util.List;

@Repository
public class StoreMapper {
    private final JdbcTemplate jdbc;
    public StoreMapper(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    private final RowMapper<RentalStore> rowMapper = (rs, rn) -> {
        RentalStore s = new RentalStore();
        s.setId(rs.getLong("id"));
        s.setStoreName(rs.getString("store_name"));
        s.setAddress(rs.getString("address"));
        s.setPhone(rs.getString("phone"));
        s.setBusinessHours(rs.getString("business_hours"));
        s.setStatus(rs.getInt("status"));
        s.setCreateTime(rs.getTimestamp("create_time"));
        s.setUpdateTime(rs.getTimestamp("update_time"));
        return s;
    };

    public int insert(RentalStore s) {
        return jdbc.update(
            "INSERT INTO rental_store (store_name,address,phone,business_hours,status,create_time,update_time) VALUES (?,?,?,?,?,?,?)",
            s.getStoreName(), s.getAddress(), s.getPhone(), s.getBusinessHours(),
            s.getStatus() != null ? s.getStatus() : 1, new Date(), new Date()
        );
    }

    public RentalStore findById(Long id) {
        List<RentalStore> list = jdbc.query("SELECT * FROM rental_store WHERE id=?", rowMapper, id);
        return list.isEmpty() ? null : list.get(0);
    }

    public List<RentalStore> findAll() {
        return jdbc.query("SELECT * FROM rental_store ORDER BY id", rowMapper);
    }

    public List<RentalStore> findByStatus(Integer status) {
        return jdbc.query("SELECT * FROM rental_store WHERE status=? ORDER BY id", rowMapper, status);
    }
}
