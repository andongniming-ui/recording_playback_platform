package com.rental.base.controller;

import com.rental.common.dto.*;
import com.rental.common.util.TransactionLogUtil;
import com.rental.base.service.UserService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/user")
public class UserController {

    private final UserService userService;
    public UserController(UserService userService) { this.userService = userService; }

    @PostMapping("/register")
    public XmlResponse register(@RequestBody UserBody.RegisterReq body) {
        TransactionLogUtil.setRequestBody(body.toString());
        UserBody.UserRes res = userService.register(body);
        XmlResponse resp = new XmlResponse(
            new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "注册成功"), res);
        TransactionLogUtil.setResponseBody(toXmlString(resp));
        return resp;
    }

    @PostMapping("/login")
    public XmlResponse login(@RequestBody UserBody.LoginReq body) {
        UserBody.UserRes res = userService.login(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "1001", "用户名或密码错误"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "登录成功"), res);
    }

    @PostMapping("/query")
    public XmlResponse query(@RequestBody UserBody.QueryReq body) {
        UserBody.UserRes res = userService.query(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "1002", "用户不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "查询成功"), res);
    }

    @PostMapping("/update")
    public XmlResponse update(@RequestBody UserBody.UpdateReq body) {
        UserBody.UserRes res = userService.update(body);
        if (res == null) {
            return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "1002", "用户不存在"), null);
        }
        return new XmlResponse(new ResponseHeader(TransactionLogUtil.getSerialNo(), "0000", "更新成功"), res);
    }

    private String toXmlString(XmlResponse resp) {
        try {
            com.fasterxml.jackson.dataformat.xml.XmlMapper mapper = new com.fasterxml.jackson.dataformat.xml.XmlMapper();
            return mapper.writeValueAsString(resp);
        } catch (Exception e) { return resp.toString(); }
    }
}
