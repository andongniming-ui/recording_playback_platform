package com.rental.base.controller;

import com.rental.common.dto.*;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.service.VehicleService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/vehicle")
public class VehicleController {

    private final VehicleService vehicleService;
    public VehicleController(VehicleService vehicleService) { this.vehicleService = vehicleService; }

    @PostMapping("/add")
    public XmlResponse add(@RequestBody VehicleBody.AddReq body) {
        VehicleBody.VehicleRes res = vehicleService.add(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "车辆添加成功"), res);
    }

    @PostMapping("/query")
    public XmlResponse query(@RequestBody VehicleBody.QueryReq body) {
        VehicleBody.VehicleRes res = vehicleService.query(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "2001", "车辆不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }

    @PostMapping("/update")
    public XmlResponse update(@RequestBody VehicleBody.UpdateReq body) {
        VehicleBody.VehicleRes res = vehicleService.update(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "2001", "车辆不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "更新成功"), res);
    }

    @PostMapping("/delete")
    public XmlResponse delete(@RequestBody VehicleBody.DeleteReq body) {
        boolean ok = vehicleService.delete(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(),
            ok ? "0000" : "2001", ok ? "删除成功" : "车辆不存在"), null);
    }

    @PostMapping("/list")
    public XmlResponse list(@RequestBody VehicleBody.ListReq body) {
        VehicleBody.VehicleListRes res = vehicleService.list(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }

    @PostMapping("/insurance")
    public XmlResponse insurance(@RequestBody VehicleBody.InsuranceReq body) {
        VehicleBody.InsuranceRes res = vehicleService.insurance(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "2001", "车辆不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "保险查询成功"), res);
    }
}
