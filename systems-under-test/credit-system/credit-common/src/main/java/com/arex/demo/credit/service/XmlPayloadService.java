package com.arex.demo.credit.service;

import com.arex.demo.credit.model.GatewayResult;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.w3c.dom.Document;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.Transformer;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.ByteArrayInputStream;
import java.io.StringWriter;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class XmlPayloadService {

    private static final Logger log = LoggerFactory.getLogger(XmlPayloadService.class);

    public Map<String, String> extractParams(String xmlBody) {
        Map<String, String> params = new LinkedHashMap<String, String>();
        try {
            Document doc = DocumentBuilderFactory.newInstance()
                    .newDocumentBuilder()
                    .parse(new ByteArrayInputStream(xmlBody.getBytes("UTF-8")));
            Node root = doc.getDocumentElement();
            NodeList children = root.getChildNodes();
            for (int i = 0; i < children.getLength(); i++) {
                Node child = children.item(i);
                if (child.getNodeType() == Node.ELEMENT_NODE) {
                    params.put(child.getNodeName(), child.getTextContent().trim());
                }
            }
        } catch (Exception e) {
            log.warn("extractParams failed: {}", e.getMessage());
        }
        return params;
    }

    public String buildResponse(GatewayResult result) {
        try {
            Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
            Node root = doc.createElement("response");
            doc.appendChild(root);

            append(doc, root, "txn_code", result.getTxnCode());
            append(doc, root, "tra_id", result.getTraId());
            append(doc, root, "request_time", result.getRequestTime());
            append(doc, root, "response_time", result.getResponseTime());
            append(doc, root, "status", result.getStatus());

            if (result.getBody() != null) {
                for (Map.Entry<String, Object> entry : result.getBody().entrySet()) {
                    append(doc, root, entry.getKey(), entry.getValue() == null ? "" : String.valueOf(entry.getValue()));
                }
            }

            Transformer transformer = TransformerFactory.newInstance().newTransformer();
            transformer.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "yes");
            transformer.setOutputProperty(OutputKeys.INDENT, "no");
            StringWriter writer = new StringWriter();
            transformer.transform(new DOMSource(doc), new StreamResult(writer));
            return writer.toString();
        } catch (Exception e) {
            log.error("buildResponse failed: {}", e.getMessage(), e);
            return "<response><status>ERROR</status><error_message>" + e.getMessage() + "</error_message></response>";
        }
    }

    private void append(Document doc, Node parent, String tag, String value) {
        Node element = doc.createElement(tag);
        element.setTextContent(value == null ? "" : value);
        parent.appendChild(element);
    }
}
