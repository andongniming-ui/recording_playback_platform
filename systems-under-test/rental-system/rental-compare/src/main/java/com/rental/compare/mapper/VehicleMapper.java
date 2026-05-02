package com.rental.compare.mapper;

import com.rental.common.model.RentalVehicle;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.stereotype.Repository;
import java.util.Date;
import java.util.List;

@Repository
public class VehicleMapper {
    private final JdbcTemplate jdbc;
    public VehicleMapper(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    private final RowMapper<RentalVehicle> rowMapper = (rs, rn) -> {
        RentalVehicle v = new RentalVehicle();
        v.setId(rs.getLong("id"));
        v.setPlateNumber(rs.getString("plate_number"));
        v.setBrand(rs.getString("brand"));
        v.setModel(rs.getString("model"));
        v.setColor(rs.getString("color"));
        v.setYear(rs.getInt("year"));
        v.setSeats(rs.getInt("seats"));
        v.setDisplacement(rs.getString("displacement"));
        v.setPricePerDay(rs.getBigDecimal("price_per_day"));
        v.setStoreId(rs.getLong("store_id"));
        v.setStatus(rs.getInt("status"));
        v.setMileage(rs.getInt("mileage"));
        v.setInsuranceExpire(rs.getTimestamp("insurance_expire"));
        v.setMaintenanceStatus(rs.getString("maintenance_status"));
        v.setCreateTime(rs.getTimestamp("create_time"));
        v.setUpdateTime(rs.getTimestamp("update_time"));
        return v;
    };

    public int insert(RentalVehicle v) {
        return jdbc.update(
            "INSERT INTO rental_vehicle (plate_number,brand,model,color,year,seats,displacement,price_per_day,store_id,status,mileage,insurance_expire,maintenance_status,create_time,update_time) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            v.getPlateNumber(), v.getBrand(), v.getModel(), v.getColor(), v.getYear(),
            v.getSeats(), v.getDisplacement(), v.getPricePerDay(), v.getStoreId(),
            v.getStatus() != null ? v.getStatus() : 1, v.getMileage() != null ? v.getMileage() : 0,
            v.getInsuranceExpire(), v.getMaintenanceStatus() != null ? v.getMaintenanceStatus() : "NORMAL",
            new Date(), new Date()
        );
    }

    public RentalVehicle findById(Long id) {
        List<RentalVehicle> list = jdbc.query("SELECT * FROM rental_vehicle WHERE id=?", rowMapper, id);
        return list.isEmpty() ? null : list.get(0);
    }

    public List<RentalVehicle> findByPlateNumber(String plateNumber) {
        return jdbc.query("SELECT * FROM rental_vehicle WHERE plate_number=?", rowMapper, plateNumber);
    }

    public List<RentalVehicle> findByStoreId(Long storeId, Integer status) {
        if (status != null) {
            return jdbc.query("SELECT * FROM rental_vehicle WHERE store_id=? AND status=? ORDER BY id", rowMapper, storeId, status);
        }
        return jdbc.query("SELECT * FROM rental_vehicle WHERE store_id=? ORDER BY id", rowMapper, storeId);
    }

    public List<RentalVehicle> findByStatus(Integer status) {
        return jdbc.query("SELECT * FROM rental_vehicle WHERE status=? ORDER BY id", rowMapper, status);
    }

    public int update(RentalVehicle v) {
        return jdbc.update(
            "UPDATE rental_vehicle SET price_per_day=?,status=?,mileage=?,store_id=?,maintenance_status=?,update_time=? WHERE id=?",
            v.getPricePerDay(), v.getStatus(), v.getMileage(), v.getStoreId(),
            v.getMaintenanceStatus(), new Date(), v.getId()
        );
    }

    public int delete(Long id) {
        return jdbc.update("DELETE FROM rental_vehicle WHERE id=?", id);
    }

    public int countByStoreId(Long storeId) {
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM rental_vehicle WHERE store_id=?", Integer.class, storeId);
        return count != null ? count : 0;
    }

    public int countByStatus(Integer status) {
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM rental_vehicle WHERE status=?", Integer.class, status);
        return count != null ? count : 0;
    }

    public int totalCount() {
        Integer count = jdbc.queryForObject("SELECT COUNT(*) FROM rental_vehicle", Integer.class);
        return count != null ? count : 0;
    }
}
