package com.rental.compare.mapper;

import com.rental.common.model.RentalUser;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.Date;
import java.util.List;

@Repository
public class UserMapper {
    private final JdbcTemplate jdbc;

    public UserMapper(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    private final RowMapper<RentalUser> rowMapper = (rs, rn) -> {
        RentalUser u = new RentalUser();
        u.setId(rs.getLong("id"));
        u.setUsername(rs.getString("username"));
        u.setPassword(rs.getString("password"));
        u.setRealName(rs.getString("real_name"));
        u.setPhone(rs.getString("phone"));
        u.setEmail(rs.getString("email"));
        u.setIdCard(rs.getString("id_card"));
        u.setDriverLicense(rs.getString("driver_license"));
        u.setMembershipLevel(rs.getString("membership_level"));
        u.setBalance(rs.getBigDecimal("balance"));
        u.setStatus(rs.getInt("status"));
        u.setCreateTime(rs.getTimestamp("create_time"));
        u.setUpdateTime(rs.getTimestamp("update_time"));
        return u;
    };

    public int insert(RentalUser u) {
        return jdbc.update(
            "INSERT INTO rental_user (username,password,real_name,phone,email,id_card,driver_license,membership_level,balance,status,create_time,update_time) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            u.getUsername(), u.getPassword(), u.getRealName(), u.getPhone(), u.getEmail(),
            u.getIdCard(), u.getDriverLicense(), u.getMembershipLevel() != null ? u.getMembershipLevel() : "SILVER",
            u.getBalance() != null ? u.getBalance() : new java.math.BigDecimal("0.00"),
            u.getStatus() != null ? u.getStatus() : 1,
            new Date(), new Date()
        );
    }

    public RentalUser findById(Long id) {
        List<RentalUser> list = jdbc.query("SELECT * FROM rental_user WHERE id=?", rowMapper, id);
        return list.isEmpty() ? null : list.get(0);
    }

    public RentalUser findByUsername(String username) {
        List<RentalUser> list = jdbc.query("SELECT * FROM rental_user WHERE username=?", rowMapper, username);
        return list.isEmpty() ? null : list.get(0);
    }

    public int update(RentalUser u) {
        return jdbc.update(
            "UPDATE rental_user SET real_name=?,phone=?,email=?,update_time=? WHERE id=?",
            u.getRealName(), u.getPhone(), u.getEmail(), new Date(), u.getId()
        );
    }

    public List<RentalUser> findAll() {
        return jdbc.query("SELECT * FROM rental_user ORDER BY id", rowMapper);
    }
}
