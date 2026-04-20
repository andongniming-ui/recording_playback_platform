package com.arex.demo.didi.common.service;

import java.math.BigDecimal;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.Map;

import org.springframework.stereotype.Component;

import com.arex.demo.didi.common.model.CarTransactionDefinition;

@Component
public class CarTransactionCatalog {

    private final Map<String, CarTransactionDefinition> definitions = new LinkedHashMap<String, CarTransactionDefinition>();

    public CarTransactionCatalog() {
        register("car000001", "code", "车险试算", true, "320.00");
        register("car000002", "code", "车险出单", true, "560.00");
        register("car000003", "code", "车险续保", true, "610.00");
        register("car000004", "code", "理赔报案", true, "420.00");
        register("car000005", "code", "理赔定损", true, "880.00");
        register("car000006", "trs_code", "道路救援派单", true, "260.00");
        register("car000007", "trs_code", "维修估价", true, "740.00");
        register("car000008", "trs_code", "维修确认", true, "910.00");
        register("car000009", "trs_code", "二手车估值", true, "510.00");
        register("car000010", "trs_code", "车贷预审", true, "430.00");
        register("car000011", "service_code", "车贷放款确认", true, "1200.00");
        register("car000012", "service_code", "延保查询", true, "390.00");
        register("car000013", "service_code", "违章代办", true, "180.00");
        register("car000014", "biz_code", "电池健康检测", true, "350.00");
        register("car000015", "biz_code", "充电订单创建", true, "150.00");

        register("car000016", "code", "车辆画像查询", false, "120.00");
        register("car000017", "code", "配件库存查询", false, "90.00");
        register("car000018", "code", "保养套餐查询", false, "110.00");
        register("car000019", "code", "门店营业时间查询", false, "80.00");
        register("car000020", "code", "试驾预约提交", false, "140.00");
        register("car000021", "trs_code", "新能源补贴测算", false, "210.00");
        register("car000022", "trs_code", "停车费试算", false, "75.00");
        register("car000023", "trs_code", "车机版本查询", false, "55.00");
        register("car000024", "trs_code", "会员权益校验", false, "130.00");
        register("car000025", "trs_code", "预约洗车", false, "95.00");
        register("car000026", "service_code", "牌照归属地查询", false, "60.00");
        register("car000027", "service_code", "充电站列表查询", false, "68.00");
        register("car000028", "service_code", "积分兑换测算", false, "77.00");
        register("car000029", "biz_code", "优惠券核销校验", false, "88.00");
        register("car000030", "biz_code", "售后评价提交", false, "66.00");
    }

    public CarTransactionDefinition find(String code) {
        return definitions.get(code);
    }

    public Collection<CarTransactionDefinition> all() {
        return definitions.values();
    }

    private void register(String code, String requestField, String displayName, boolean complex, String baseAmount) {
        definitions.put(code, new CarTransactionDefinition(code, requestField, displayName, complex, new BigDecimal(baseAmount)));
    }
}
