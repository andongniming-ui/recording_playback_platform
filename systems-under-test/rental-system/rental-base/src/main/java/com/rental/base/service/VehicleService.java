package com.rental.base.service;

import com.rental.common.dto.VehicleBody;
import com.rental.common.model.RentalVehicle;
import com.rental.common.util.DateTimeUtil;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.mapper.VehicleMapper;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Service
public class VehicleService {
    private final VehicleMapper vehicleMapper;
    private final SubCallService subCallService;

    public VehicleService(VehicleMapper vehicleMapper, SubCallService subCallService) {
        this.vehicleMapper = vehicleMapper;
        this.subCallService = subCallService;
    }

    public VehicleBody.VehicleRes add(VehicleBody.AddReq req) {
        long start = System.currentTimeMillis();
        RentalVehicle v = new RentalVehicle();
        v.setPlateNumber(req.getPlateNumber());
        v.setBrand(req.getBrand());
        v.setModel(req.getModel());
        v.setColor(req.getColor());
        v.setYear(req.getYear());
        v.setSeats(req.getSeats());
        v.setDisplacement(req.getDisplacement());
        v.setPricePerDay(new BigDecimal(req.getPricePerDay()));
        v.setStoreId(req.getStoreId());
        v.setMileage(req.getMileage() != null ? req.getMileage() : 0);
        v.setInsuranceExpire(DateTimeUtil.parse(req.getInsuranceExpire()));
        v.setStatus(1);
        v.setMaintenanceStatus("NORMAL");
        vehicleMapper.insert(v);
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("INSERT rental_vehicle plate=" + req.getPlateNumber() + " elapsed=" + elapsed + "ms");

        long t2 = System.currentTimeMillis();
        List<RentalVehicle> saved = vehicleMapper.findByPlateNumber(req.getPlateNumber());
        TransactionLogUtil.addDbCall("SELECT rental_vehicle WHERE plate_number=" + req.getPlateNumber() + " elapsed=" + (System.currentTimeMillis() - t2) + "ms");
        return saved.isEmpty() ? null : toVehicleRes(saved.get(0), null);
    }

    public VehicleBody.VehicleRes query(VehicleBody.QueryReq req) {
        long start = System.currentTimeMillis();
        RentalVehicle v = null;
        if (req.getVehicleId() != null) {
            v = vehicleMapper.findById(req.getVehicleId());
        } else if (req.getPlateNumber() != null) {
            List<RentalVehicle> list = vehicleMapper.findByPlateNumber(req.getPlateNumber());
            v = list.isEmpty() ? null : list.get(0);
        }
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_vehicle elapsed=" + elapsed + "ms");

        if (v == null) return null;

        // Sub-call: query insurance info
        String serialNo = TransactionLogUtil.getSerialNo();
        Map<String, Object> subResult = subCallService.queryInsurance(v.getId(), v.getPlateNumber(), serialNo);
        TransactionLogUtil.addSubCall(subResult.toString());

        return toVehicleRes(v, null);
    }

    public VehicleBody.VehicleRes update(VehicleBody.UpdateReq req) {
        long start = System.currentTimeMillis();
        RentalVehicle v = vehicleMapper.findById(req.getVehicleId());
        long t1 = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_vehicle WHERE id=" + req.getVehicleId() + " elapsed=" + t1 + "ms");
        if (v == null) return null;

        if (req.getPricePerDay() != null) v.setPricePerDay(new BigDecimal(req.getPricePerDay()));
        if (req.getStatus() != null) v.setStatus(req.getStatus());
        if (req.getMileage() != null) v.setMileage(req.getMileage());
        if (req.getStoreId() != null) v.setStoreId(req.getStoreId());
        long t2 = System.currentTimeMillis();
        vehicleMapper.update(v);
        TransactionLogUtil.addDbCall("UPDATE rental_vehicle WHERE id=" + req.getVehicleId() + " elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        long t3 = System.currentTimeMillis();
        RentalVehicle updated = vehicleMapper.findById(req.getVehicleId());
        TransactionLogUtil.addDbCall("SELECT rental_vehicle WHERE id=" + req.getVehicleId() + " elapsed=" + (System.currentTimeMillis() - t3) + "ms");
        return toVehicleRes(updated, null);
    }

    public boolean delete(VehicleBody.DeleteReq req) {
        long start = System.currentTimeMillis();
        int rows = vehicleMapper.delete(req.getVehicleId());
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("DELETE rental_vehicle WHERE id=" + req.getVehicleId() + " elapsed=" + elapsed + "ms");
        return rows > 0;
    }

    public VehicleBody.VehicleListRes list(VehicleBody.ListReq req) {
        long start = System.currentTimeMillis();
        List<RentalVehicle> vehicles;
        if (req.getStoreId() != null) {
            vehicles = vehicleMapper.findByStoreId(req.getStoreId(), req.getStatus());
        } else if (req.getStatus() != null) {
            vehicles = vehicleMapper.findByStatus(req.getStatus());
        } else {
            vehicles = vehicleMapper.findByStatus(1); // default available
        }
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_vehicle list elapsed=" + elapsed + "ms");

        // Sub-call: query store info for each unique store
        String serialNo = TransactionLogUtil.getSerialNo();
        if (req.getStoreId() != null) {
            Map<String, Object> subResult = subCallService.queryStoreInfo(req.getStoreId(), serialNo);
            TransactionLogUtil.addSubCall(subResult.toString());
        }

        VehicleBody.VehicleListRes res = new VehicleBody.VehicleListRes();
        List<VehicleBody.VehicleRes> resList = new ArrayList<>();
        for (RentalVehicle v : vehicles) {
            resList.add(toVehicleRes(v, null));
        }
        res.setVehicles(resList);
        res.setTotal(resList.size());
        return res;
    }

    public VehicleBody.InsuranceRes insurance(VehicleBody.InsuranceReq req) {
        long start = System.currentTimeMillis();
        RentalVehicle v = null;
        if (req.getVehicleId() != null) {
            v = vehicleMapper.findById(req.getVehicleId());
        } else if (req.getPlateNumber() != null) {
            List<RentalVehicle> list = vehicleMapper.findByPlateNumber(req.getPlateNumber());
            v = list.isEmpty() ? null : list.get(0);
        }
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_vehicle elapsed=" + elapsed + "ms");

        if (v == null) return null;

        // Sub-call: query insurance service
        String serialNo = TransactionLogUtil.getSerialNo();
        Map<String, Object> subResult = subCallService.queryInsurance(v.getId(), v.getPlateNumber(), serialNo);
        TransactionLogUtil.addSubCall(subResult.toString());

        VehicleBody.InsuranceRes res = new VehicleBody.InsuranceRes();
        res.setVehicleId(v.getId());
        res.setPlateNumber(v.getPlateNumber());
        if (subResult.containsKey("insurance_company")) {
            res.setInsuranceCompany((String) subResult.get("insurance_company"));
            res.setInsuranceType((String) subResult.get("insurance_type"));
            res.setInsuranceExpire(DateTimeUtil.format(v.getInsuranceExpire()));
            res.setCoverageAmount((String) subResult.get("coverage_amount"));
            res.setIsValid((Boolean) subResult.get("is_valid"));
        }
        return res;
    }

    public VehicleBody.VehicleRes toVehicleRes(RentalVehicle v, String insuranceInfo) {
        VehicleBody.VehicleRes res = new VehicleBody.VehicleRes();
        res.setVehicleId(v.getId());
        res.setPlateNumber(v.getPlateNumber());
        res.setBrand(v.getBrand());
        res.setModel(v.getModel());
        res.setColor(v.getColor());
        res.setYear(v.getYear());
        res.setSeats(v.getSeats());
        res.setDisplacement(v.getDisplacement());
        res.setPricePerDay(v.getPricePerDay() != null ? v.getPricePerDay().toString() : "0.00");
        res.setStoreId(v.getStoreId());
        res.setStatus(v.getStatus());
        res.setMileage(v.getMileage());
        res.setInsuranceExpire(DateTimeUtil.format(v.getInsuranceExpire()));
        res.setMaintenanceStatus(v.getMaintenanceStatus());
        res.setCreateTime(DateTimeUtil.format(v.getCreateTime()));
        res.setInsuranceInfo(insuranceInfo);
        return res;
    }
}
