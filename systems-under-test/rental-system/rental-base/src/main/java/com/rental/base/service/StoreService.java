package com.rental.base.service;

import com.rental.common.dto.StoreBody;
import com.rental.common.model.RentalStore;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.mapper.StoreMapper;
import com.rental.base.mapper.VehicleMapper;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
public class StoreService {
    private final StoreMapper storeMapper;
    private final VehicleMapper vehicleMapper;

    public StoreService(StoreMapper storeMapper, VehicleMapper vehicleMapper) {
        this.storeMapper = storeMapper;
        this.vehicleMapper = vehicleMapper;
    }

    public StoreBody.StoreRes add(StoreBody.AddReq req) {
        long start = System.currentTimeMillis();
        RentalStore s = new RentalStore();
        s.setStoreName(req.getStoreName());
        s.setAddress(req.getAddress());
        s.setPhone(req.getPhone());
        s.setBusinessHours(req.getBusinessHours());
        s.setStatus(1);
        storeMapper.insert(s);
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("INSERT rental_store name=" + req.getStoreName() + " elapsed=" + elapsed + "ms");
        return toStoreRes(s);
    }

    public StoreBody.StoreRes query(StoreBody.QueryReq req) {
        long start = System.currentTimeMillis();
        RentalStore s = storeMapper.findById(req.getStoreId());
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_store WHERE id=" + req.getStoreId() + " elapsed=" + elapsed + "ms");
        return s != null ? toStoreRes(s) : null;
    }

    public StoreBody.StoreListRes list(StoreBody.ListReq req) {
        long start = System.currentTimeMillis();
        List<RentalStore> stores;
        if (req.getStatus() != null) {
            stores = storeMapper.findByStatus(req.getStatus());
        } else {
            stores = storeMapper.findAll();
        }
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_store list elapsed=" + elapsed + "ms");

        StoreBody.StoreListRes res = new StoreBody.StoreListRes();
        List<StoreBody.StoreRes> storeResList = new ArrayList<>();
        for (RentalStore s : stores) {
            storeResList.add(toStoreRes(s));
        }
        res.setStores(storeResList);
        res.setTotal(storeResList.size());
        return res;
    }

    private StoreBody.StoreRes toStoreRes(RentalStore s) {
        StoreBody.StoreRes res = new StoreBody.StoreRes();
        res.setStoreId(s.getId());
        res.setStoreName(s.getStoreName());
        res.setAddress(s.getAddress());
        res.setPhone(s.getPhone());
        res.setBusinessHours(s.getBusinessHours());
        res.setStatus(s.getStatus());
        long t = System.currentTimeMillis();
        res.setVehicleCount(vehicleMapper.countByStoreId(s.getId()));
        TransactionLogUtil.addDbCall("SELECT COUNT rental_vehicle WHERE store_id=" + s.getId() + " elapsed=" + (System.currentTimeMillis() - t) + "ms");
        res.setCreateTime(com.rental.common.util.DateTimeUtil.format(s.getCreateTime()));
        return res;
    }
}
