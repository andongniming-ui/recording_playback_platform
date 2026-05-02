package com.rental.compare.service;

import com.rental.common.dto.UserBody;
import com.rental.common.model.RentalUser;
import com.rental.common.util.TransactionLogUtil;
import com.rental.compare.mapper.UserMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;

@Service
public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserService.class);
    private final UserMapper userMapper;

    public UserService(UserMapper userMapper) { this.userMapper = userMapper; }

    public UserBody.UserRes register(UserBody.RegisterReq req) {
        long start = System.currentTimeMillis();
        RentalUser u = new RentalUser();
        u.setUsername(req.getUsername());
        u.setPassword(req.getPassword());
        u.setRealName(req.getRealName());
        u.setPhone(req.getPhone());
        u.setEmail(req.getEmail());
        u.setIdCard(req.getIdCard());
        u.setDriverLicense(req.getDriverLicense());
        u.setMembershipLevel("SILVER");
        u.setBalance(new BigDecimal("0.00"));
        u.setStatus(1);

        userMapper.insert(u);
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("INSERT rental_user username=" + req.getUsername() + " elapsed=" + elapsed + "ms");

        long t2 = System.currentTimeMillis();
        RentalUser saved = userMapper.findByUsername(req.getUsername());
        TransactionLogUtil.addDbCall("SELECT rental_user WHERE username=" + req.getUsername() + " elapsed=" + (System.currentTimeMillis() - t2) + "ms");
        return toUserRes(saved);
    }

    public UserBody.UserRes login(UserBody.LoginReq req) {
        long start = System.currentTimeMillis();
        RentalUser u = userMapper.findByUsername(req.getUsername());
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_user WHERE username=" + req.getUsername() + " elapsed=" + elapsed + "ms");

        if (u == null || !u.getPassword().equals(req.getPassword())) {
            return null;
        }
        return toUserRes(u);
    }

    public UserBody.UserRes query(UserBody.QueryReq req) {
        long start = System.currentTimeMillis();
        RentalUser u = null;
        if (req.getUserId() != null) {
            u = userMapper.findById(req.getUserId());
        } else if (req.getUsername() != null) {
            u = userMapper.findByUsername(req.getUsername());
        }
        long elapsed = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_user elapsed=" + elapsed + "ms");

        return u != null ? toUserRes(u) : null;
    }

    public UserBody.UserRes update(UserBody.UpdateReq req) {
        long start = System.currentTimeMillis();
        RentalUser u = userMapper.findById(req.getUserId());
        long t1 = System.currentTimeMillis() - start;
        TransactionLogUtil.addDbCall("SELECT rental_user WHERE id=" + req.getUserId() + " elapsed=" + t1 + "ms");
        if (u == null) return null;

        if (req.getRealName() != null) u.setRealName(req.getRealName());
        if (req.getPhone() != null) u.setPhone(req.getPhone());
        if (req.getEmail() != null) u.setEmail(req.getEmail());
        long t2 = System.currentTimeMillis();
        userMapper.update(u);
        TransactionLogUtil.addDbCall("UPDATE rental_user WHERE id=" + req.getUserId() + " elapsed=" + (System.currentTimeMillis() - t2) + "ms");

        long t3 = System.currentTimeMillis();
        RentalUser updated = userMapper.findById(req.getUserId());
        TransactionLogUtil.addDbCall("SELECT rental_user WHERE id=" + req.getUserId() + " elapsed=" + (System.currentTimeMillis() - t3) + "ms");
        return toUserRes(updated);
    }

    private UserBody.UserRes toUserRes(RentalUser u) {
        UserBody.UserRes res = new UserBody.UserRes();
        res.setUserId(u.getId());
        res.setUsername(u.getUsername());
        res.setRealName(u.getRealName());
        res.setPhone(u.getPhone());
        res.setEmail(u.getEmail());
        res.setIdCard(u.getIdCard());
        res.setDriverLicense(u.getDriverLicense());
        res.setMembershipLevel(u.getMembershipLevel());
        res.setBalance(u.getBalance() != null ? u.getBalance().toString() : "0.00");
        res.setStatus(u.getStatus());
        res.setCreateTime(com.rental.common.util.DateTimeUtil.format(u.getCreateTime()));
        return res;
    }
}
