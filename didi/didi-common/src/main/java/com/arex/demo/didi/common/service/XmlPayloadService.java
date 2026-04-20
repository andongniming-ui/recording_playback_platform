package com.arex.demo.didi.common.service;

import java.io.StringReader;
import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.springframework.stereotype.Service;
import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import com.arex.demo.didi.common.config.DidiVariantProperties;
import com.arex.demo.didi.common.model.CarTransactionDefinition;
import com.arex.demo.didi.common.model.GatewayContext;
import com.arex.demo.didi.common.model.GatewayResult;

@Service
public class XmlPayloadService {

    private static final List<String> TX_FIELDS = Arrays.asList("code", "trs_code", "service_code", "biz_code", "trans_code");

    public GatewayContext parse(String xml) {
        try {
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            factory.setNamespaceAware(false);
            factory.setExpandEntityReferences(false);
            DocumentBuilder builder = factory.newDocumentBuilder();
            Document document = builder.parse(new InputSource(new StringReader(xml)));

            GatewayContext context = new GatewayContext();
            context.setRawXml(xml);
            for (String field : TX_FIELDS) {
                String value = textOf(document, field);
                if (hasText(value)) {
                    context.setTransactionCode(value.trim());
                    context.setRequestField(field);
                    break;
                }
            }
            context.setRequestNo(firstNonBlank(textOf(document, "request_no"), textOf(document, "req_no"), textOf(document, "order_no")));
            context.setCustomerNo(firstNonBlank(textOf(document, "customer_no"), textOf(document, "cust_no")));
            context.setPlateNo(firstNonBlank(textOf(document, "plate_no"), textOf(document, "car_no")));
            context.setVin(textOf(document, "vin"));
            context.setPolicyNo(textOf(document, "policy_no"));
            context.setClaimNo(textOf(document, "claim_no"));
            context.setGarageCode(textOf(document, "garage_code"));
            context.setCity(textOf(document, "city"));
            return context;
        } catch (Exception ex) {
            throw new IllegalArgumentException("invalid xml payload: " + ex.getMessage(), ex);
        }
    }

    public String buildResponseXml(GatewayContext context,
                                   CarTransactionDefinition definition,
                                   GatewayResult result,
                                   DidiVariantProperties variantProperties) {
        StringBuilder builder = new StringBuilder();
        builder.append("<response>");
        append(builder, "system", variantProperties.getSystemName());
        append(builder, "variant_id", variantProperties.getVariantId());
        append(builder, "compare_hint", variantProperties.getCompareHint());
        append(builder, "txn_code", definition.getCode());
        append(builder, "txn_name", definition.getDisplayName());
        append(builder, "request_field", context.getRequestField());
        append(builder, "request_no", context.getRequestNo());
        append(builder, "status", result.getStatus());
        append(builder, "message", result.getMessage());
        append(builder, "customer_tier", result.getCustomerTier());
        append(builder, "vehicle_model", result.getVehicleModel());
        append(builder, "risk_level", result.getRiskLevel());
        append(builder, "decision", result.getDecision());
        append(builder, "dispatch_city", result.getDispatchCity());
        append(builder, "policy_status", result.getPolicyStatus());
        append(builder, "database_flag", result.getDbFlag());
        append(builder, "sub_call_flag", result.getSubCallFlag());
        append(builder, "base_amount", formatAmount(result.getBaseAmount()));
        append(builder, "final_amount", formatAmount(result.getFinalAmount()));
        builder.append("</response>");
        return builder.toString();
    }

    private void append(StringBuilder builder, String tagName, String value) {
        builder.append("<").append(tagName).append(">");
        builder.append(escapeXml(value));
        builder.append("</").append(tagName).append(">");
    }

    private String formatAmount(BigDecimal amount) {
        return amount == null ? "" : amount.setScale(2, BigDecimal.ROUND_HALF_UP).toPlainString();
    }

    private String escapeXml(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&apos;");
    }

    private String textOf(Document document, String tagName) {
        NodeList list = document.getElementsByTagName(tagName);
        if (list == null || list.getLength() == 0 || list.item(0) == null || list.item(0).getTextContent() == null) {
            return null;
        }
        return list.item(0).getTextContent();
    }

    private boolean hasText(String value) {
        return value != null && value.trim().length() > 0;
    }

    private String firstNonBlank(String first, String second) {
        return hasText(first) ? first : second;
    }

    private String firstNonBlank(String first, String second, String third) {
        if (hasText(first)) {
            return first;
        }
        if (hasText(second)) {
            return second;
        }
        return third;
    }
}
