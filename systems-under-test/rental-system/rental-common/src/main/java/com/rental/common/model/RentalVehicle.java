package com.rental.common.model;

import com.fasterxml.jackson.dataformat.xml.annotation.JacksonXmlRootElement;

@JacksonXmlRootElement(localName = "vehicle")
public class RentalVehicle {
    private Long id;
    private String plateNumber;
    private String brand;
    private String model;
    private String color;
    private Integer year;
    private Integer seats;
    private String displacement;
    private java.math.BigDecimal pricePerDay;
    private Long storeId;
    private Integer status;
    private Integer mileage;
    private java.util.Date insuranceExpire;
    private String maintenanceStatus;
    private java.util.Date createTime;
    private java.util.Date updateTime;

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public String getPlateNumber() { return plateNumber; }
    public void setPlateNumber(String plateNumber) { this.plateNumber = plateNumber; }
    public String getBrand() { return brand; }
    public void setBrand(String brand) { this.brand = brand; }
    public String getModel() { return model; }
    public void setModel(String model) { this.model = model; }
    public String getColor() { return color; }
    public void setColor(String color) { this.color = color; }
    public Integer getYear() { return year; }
    public void setYear(Integer year) { this.year = year; }
    public Integer getSeats() { return seats; }
    public void setSeats(Integer seats) { this.seats = seats; }
    public String getDisplacement() { return displacement; }
    public void setDisplacement(String displacement) { this.displacement = displacement; }
    public java.math.BigDecimal getPricePerDay() { return pricePerDay; }
    public void setPricePerDay(java.math.BigDecimal pricePerDay) { this.pricePerDay = pricePerDay; }
    public Long getStoreId() { return storeId; }
    public void setStoreId(Long storeId) { this.storeId = storeId; }
    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }
    public Integer getMileage() { return mileage; }
    public void setMileage(Integer mileage) { this.mileage = mileage; }
    public java.util.Date getInsuranceExpire() { return insuranceExpire; }
    public void setInsuranceExpire(java.util.Date insuranceExpire) { this.insuranceExpire = insuranceExpire; }
    public String getMaintenanceStatus() { return maintenanceStatus; }
    public void setMaintenanceStatus(String maintenanceStatus) { this.maintenanceStatus = maintenanceStatus; }
    public java.util.Date getCreateTime() { return createTime; }
    public void setCreateTime(java.util.Date createTime) { this.createTime = createTime; }
    public java.util.Date getUpdateTime() { return updateTime; }
    public void setUpdateTime(java.util.Date updateTime) { this.updateTime = updateTime; }
}
