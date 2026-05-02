package com.arex.demo.dating.common.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import com.arex.demo.dating.common.model.DatingTransactionDefinition;
import com.arex.demo.dating.common.model.GatewayContext;
import com.arex.demo.dating.common.model.GatewayResult;

/**
 * 网关服务 - 负责交易码路由分发
 */
@Service
public class DatingGatewayService {

    private static final Logger log = LoggerFactory.getLogger(DatingGatewayService.class);

    private final DatingTransactionCatalog transactionCatalog;
    private final DatingTransactionService transactionService;
    private final XmlPayloadService xmlPayloadService;

    public DatingGatewayService(DatingTransactionCatalog transactionCatalog,
                                DatingTransactionService transactionService,
                                XmlPayloadService xmlPayloadService) {
        this.transactionCatalog = transactionCatalog;
        this.transactionService = transactionService;
        this.xmlPayloadService = xmlPayloadService;
    }

    /**
     * 处理 XML 网关请求
     */
    public String handle(GatewayContext context) {
        String traceId = context.getTraceId();
        String tranCode = context.getTranCode();

        // 查找交易码定义
        DatingTransactionDefinition definition = transactionCatalog.find(tranCode);
        if (definition == null) {
            log.warn("traceId={} Unknown transaction code: {}", traceId, tranCode);
            GatewayResult errorResult = new GatewayResult();
            errorResult.setStatus("FAIL");
            errorResult.setMessage("未知交易码: " + tranCode);
            return xmlPayloadService.buildResponseXml(context,
                new DatingTransactionDefinition(tranCode, "tran_code", "未知交易", "", ""), errorResult);
        }

        // 执行交易处理
        GatewayResult result = transactionService.process(definition, context);

        // 构建 XML 响应
        return xmlPayloadService.buildResponseXml(context, definition, result);
    }
}
