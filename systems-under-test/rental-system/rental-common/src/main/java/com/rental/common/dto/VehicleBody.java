package com.rental.common.dto;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlProperty;
import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

public class VehicleBody {

    @JacksonXmlRootElement(localName = "body")
    public static class AddReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "plate_number") private String plateNumber;
        @JacksonXmlProperty(localName = "brand") private String brand;
        @JacksonXmlProperty(localName = "model") private String model;
        @JacksonXmlProperty(localName = "color") private String color;
        @JacksonXmlProperty(localName = "year") private Integer year;
        @JacksonXmlProperty(localName = "seats") private Integer seats;
        @JacksonXmlProperty(localName = "displacement") private String displacement;
        @JacksonXmlProperty(localName = "price_per_day") private String pricePerDay;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "mileage") private Integer mileage;
        @JacksonXmlProperty(localName = "insurance_expire") private String insuranceExpire;
        public String getPlateNumber() { return plateNumber; } public void setPlateNumber(String v) { this.plateNumber = v; }
        public String getBrand() { return brand; } public void setBrand(String v) { this.brand = v; }
        public String getModel() { return model; } public void setModel(String v) { this.model = v; }
        public String getColor() { return color; } public void setColor(String v) { this.color = v; }
        public Integer getYear() { return year; } public void setYear(Integer v) { this.year = v; }
        public Integer getSeats() { return seats; } public void setSeats(Integer v) { this.seats = v; }
        public String getDisplacement() { return displacement; } public void setDisplacement(String v) { this.displacement = v; }
        public String getPricePerDay() { return pricePerDay; } public void setPricePerDay(String v) { this.pricePerDay = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public Integer getMileage() { return mileage; } public void setMileage(Integer v) { this.mileage = v; }
        public String getInsuranceExpire() { return insuranceExpire; } public void setInsuranceExpire(String v) { this.insuranceExpire = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class QueryReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "plate_number") private String plateNumber;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public String getPlateNumber() { return plateNumber; } public void setPlateNumber(String v) { this.plateNumber = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class UpdateReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "price_per_day") private String pricePerDay;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "mileage") private Integer mileage;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public String getPricePerDay() { return pricePerDay; } public void setPricePerDay(String v) { this.pricePerDay = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public Integer getMileage() { return mileage; } public void setMileage(Integer v) { this.mileage = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class DeleteReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class ListReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "brand") private String brand;
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public String getBrand() { return brand; } public void setBrand(String v) { this.brand = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class InsuranceReq {
        @JacksonXmlProperty(localName = "trans_code") private String transCode;
        public String getTransCode() { return transCode; } public void setTransCode(String v) { this.transCode = v; }
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "plate_number") private String plateNumber;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public String getPlateNumber() { return plateNumber; } public void setPlateNumber(String v) { this.plateNumber = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class VehicleRes {
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "plate_number") private String plateNumber;
        @JacksonXmlProperty(localName = "brand") private String brand;
        @JacksonXmlProperty(localName = "model") private String model;
        @JacksonXmlProperty(localName = "color") private String color;
        @JacksonXmlProperty(localName = "year") private Integer year;
        @JacksonXmlProperty(localName = "seats") private Integer seats;
        @JacksonXmlProperty(localName = "displacement") private String displacement;
        @JacksonXmlProperty(localName = "price_per_day") private String pricePerDay;
        @JacksonXmlProperty(localName = "store_id") private Long storeId;
        @JacksonXmlProperty(localName = "status") private Integer status;
        @JacksonXmlProperty(localName = "mileage") private Integer mileage;
        @JacksonXmlProperty(localName = "insurance_expire") private String insuranceExpire;
        @JacksonXmlProperty(localName = "maintenance_status") private String maintenanceStatus;
        @JacksonXmlProperty(localName = "create_time") private String createTime;
        @JacksonXmlProperty(localName = "insurance_info") private String insuranceInfo;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public String getPlateNumber() { return plateNumber; } public void setPlateNumber(String v) { this.plateNumber = v; }
        public String getBrand() { return brand; } public void setBrand(String v) { this.brand = v; }
        public String getModel() { return model; } public void setModel(String v) { this.model = v; }
        public String getColor() { return color; } public void setColor(String v) { this.color = v; }
        public Integer getYear() { return year; } public void setYear(Integer v) { this.year = v; }
        public Integer getSeats() { return seats; } public void setSeats(Integer v) { this.seats = v; }
        public String getDisplacement() { return displacement; } public void setDisplacement(String v) { this.displacement = v; }
        public String getPricePerDay() { return pricePerDay; } public void setPricePerDay(String v) { this.pricePerDay = v; }
        public Long getStoreId() { return storeId; } public void setStoreId(Long v) { this.storeId = v; }
        public Integer getStatus() { return status; } public void setStatus(Integer v) { this.status = v; }
        public Integer getMileage() { return mileage; } public void setMileage(Integer v) { this.mileage = v; }
        public String getInsuranceExpire() { return insuranceExpire; } public void setInsuranceExpire(String v) { this.insuranceExpire = v; }
        public String getMaintenanceStatus() { return maintenanceStatus; } public void setMaintenanceStatus(String v) { this.maintenanceStatus = v; }
        public String getCreateTime() { return createTime; } public void setCreateTime(String v) { this.createTime = v; }
        public String getInsuranceInfo() { return insuranceInfo; } public void setInsuranceInfo(String v) { this.insuranceInfo = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class VehicleListRes {
        @JacksonXmlProperty(localName = "vehicles") private java.util.List<VehicleRes> vehicles;
        @JacksonXmlProperty(localName = "total") private Integer total;
        public java.util.List<VehicleRes> getVehicles() { return vehicles; } public void setVehicles(java.util.List<VehicleRes> v) { this.vehicles = v; }
        public Integer getTotal() { return total; } public void setTotal(Integer v) { this.total = v; }
    }

    @JacksonXmlRootElement(localName = "body")
    public static class InsuranceRes {
        @JacksonXmlProperty(localName = "vehicle_id") private Long vehicleId;
        @JacksonXmlProperty(localName = "plate_number") private String plateNumber;
        @JacksonXmlProperty(localName = "insurance_company") private String insuranceCompany;
        @JacksonXmlProperty(localName = "insurance_type") private String insuranceType;
        @JacksonXmlProperty(localName = "insurance_expire") private String insuranceExpire;
        @JacksonXmlProperty(localName = "coverage_amount") private String coverageAmount;
        @JacksonXmlProperty(localName = "is_valid") private Boolean isValid;
        public Long getVehicleId() { return vehicleId; } public void setVehicleId(Long v) { this.vehicleId = v; }
        public String getPlateNumber() { return plateNumber; } public void setPlateNumber(String v) { this.plateNumber = v; }
        public String getInsuranceCompany() { return insuranceCompany; } public void setInsuranceCompany(String v) { this.insuranceCompany = v; }
        public String getInsuranceType() { return insuranceType; } public void setInsuranceType(String v) { this.insuranceType = v; }
        public String getInsuranceExpire() { return insuranceExpire; } public void setInsuranceExpire(String v) { this.insuranceExpire = v; }
        public String getCoverageAmount() { return coverageAmount; } public void setCoverageAmount(String v) { this.coverageAmount = v; }
        public Boolean getIsValid() { return isValid; } public void setIsValid(Boolean v) { this.isValid = v; }
    }
}
