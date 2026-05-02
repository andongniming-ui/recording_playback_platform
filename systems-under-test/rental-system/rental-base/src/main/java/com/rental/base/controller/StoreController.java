package com.rental.base.controller;

import com.rental.common.dto.*;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.service.StoreService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/store")
public class StoreController {

    private final StoreService storeService;
    public StoreController(StoreService storeService) { this.storeService = storeService; }

    @PostMapping("/add")
    public XmlResponse add(@RequestBody StoreBody.AddReq body) {
        StoreBody.StoreRes res = storeService.add(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "门店添加成功"), res);
    }

    @PostMapping("/query")
    public XmlResponse query(@RequestBody StoreBody.QueryReq body) {
        StoreBody.StoreRes res = storeService.query(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "3001", "门店不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }

    @PostMapping("/list")
    public XmlResponse list(@RequestBody StoreBody.ListReq body) {
        StoreBody.StoreListRes res = storeService.list(body);
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }
}
