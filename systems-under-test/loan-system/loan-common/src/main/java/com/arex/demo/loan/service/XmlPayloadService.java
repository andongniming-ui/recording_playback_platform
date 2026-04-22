package com.arex.demo.loan.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.w3c.dom.*;

import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.transform.OutputKeys;
import javax.xml.transform.TransformerFactory;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import java.io.ByteArrayInputStream;
import java.io.StringWriter;
import java.util.*;

@Service
public class XmlPayloadService {

    private static final Logger log = LoggerFactory.getLogger(XmlPayloadService.class);

    public String extractTxnCode(String xml) {
        try {
            Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder()
                    .parse(new ByteArrayInputStream(xml.getBytes("UTF-8")));
            NodeList nl = doc.getElementsByTagName("txnCode");
            if (nl.getLength() > 0) return nl.item(0).getTextContent().trim();
        } catch (Exception e) {
            log.warn("[{}] extractTxnCode failed: {}", TraceContext.getTraId(), e.getMessage());
        }
        return "UNKNOWN";
    }

    public Map<String, String> extractParams(String xml) {
        Map<String, String> params = new LinkedHashMap<>();
        try {
            Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder()
                    .parse(new ByteArrayInputStream(xml.getBytes("UTF-8")));
            NodeList nl = doc.getElementsByTagName("body");
            if (nl.getLength() > 0) {
                NodeList children = nl.item(0).getChildNodes();
                for (int i = 0; i < children.getLength(); i++) {
                    Node n = children.item(i);
                    if (n.getNodeType() == Node.ELEMENT_NODE) {
                        params.put(n.getNodeName(), n.getTextContent().trim());
                    }
                }
            }
        } catch (Exception e) {
            log.warn("[{}] extractParams failed: {}", TraceContext.getTraId(), e.getMessage());
        }
        return params;
    }

    public String buildResponse(String txnCode, Map<String, Object> body) {
        try {
            Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
            Element root = doc.createElement("response");
            doc.appendChild(root);

            Element head = doc.createElement("head");
            ap(doc, head, "traId", TraceContext.getTraId());
            ap(doc, head, "requestTime", TraceContext.getRequestTime());
            ap(doc, head, "txnCode", txnCode);
            ap(doc, head, "status", "SUCCESS");
            ap(doc, head, "elapsed", String.valueOf(TraceContext.getElapsedMs()));
            root.appendChild(head);

            Element bodyEl = doc.createElement("body");
            if (body != null) {
                for (Map.Entry<String, Object> e : body.entrySet()) {
                    Object val = e.getValue();
                    if (val instanceof Map) {
                        Element sub = doc.createElement(e.getKey());
                        for (Map.Entry<?, ?> se : ((Map<?, ?>) val).entrySet()) {
                            ap(doc, sub, String.valueOf(se.getKey()), String.valueOf(se.getValue()));
                        }
                        bodyEl.appendChild(sub);
                    } else {
                        ap(doc, bodyEl, e.getKey(), String.valueOf(val));
                    }
                }
            }
            root.appendChild(bodyEl);

            TransformerFactory tf = TransformerFactory.newInstance();
            javax.xml.transform.Transformer t = tf.newTransformer();
            t.setOutputProperty(OutputKeys.INDENT, "yes");
            StringWriter sw = new StringWriter();
            t.transform(new DOMSource(doc), new StreamResult(sw));
            return sw.toString();
        } catch (Exception e) {
            log.error("[{}] buildResponse failed: {}", TraceContext.getTraId(), e.getMessage());
            return "<response><head><status>ERROR</status><message>" + e.getMessage() + "</message></head></response>";
        }
    }

    private void ap(Document doc, Element parent, String tag, String text) {
        Element el = doc.createElement(tag);
        el.setTextContent(text != null ? text : "");
        parent.appendChild(el);
    }
}
