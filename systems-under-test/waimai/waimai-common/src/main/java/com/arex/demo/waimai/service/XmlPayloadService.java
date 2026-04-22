package com.arex.demo.waimai.service;
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
        try { Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new ByteArrayInputStream(xml.getBytes("UTF-8")));
            NodeList nl = doc.getElementsByTagName("txnCode"); if(nl.getLength()>0) return nl.item(0).getTextContent().trim();
        } catch(Exception e) { log.warn("[{}] extractTxnCode failed: {}", TraceContext.getTraId(), e.getMessage()); } return "UNKNOWN";
    }
    public Map<String,String> extractParams(String xml) {
        Map<String,String> params = new LinkedHashMap<>();
        try { Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().parse(new ByteArrayInputStream(xml.getBytes("UTF-8")));
            NodeList nl = doc.getElementsByTagName("params"); if(nl.getLength()>0) { NodeList ch = nl.item(0).getChildNodes();
                for(int i=0;i<ch.getLength();i++) { Node n=ch.item(i); if(n.getNodeType()==Node.ELEMENT_NODE) params.put(n.getNodeName(),n.getTextContent().trim()); }
            }
        } catch(Exception e) { log.warn("[{}] extractParams failed: {}", TraceContext.getTraId(), e.getMessage()); } return params;
    }
    public String buildResponse(String txnCode, Map<String,Object> data) {
        try { Document doc = DocumentBuilderFactory.newInstance().newDocumentBuilder().newDocument();
            Element root = doc.createElement("response"); doc.appendChild(root);
            ap(doc,root,"traId",TraceContext.getTraId()); ap(doc,root,"requestTime",TraceContext.getRequestTime());
            ap(doc,root,"txnCode",txnCode); ap(doc,root,"status","SUCCESS");
            Element d = doc.createElement("data"); for(Map.Entry<String,Object> e: data.entrySet()) ap(doc,d,e.getKey(),String.valueOf(e.getValue()));
            root.appendChild(d);
            javax.xml.transform.Transformer t = TransformerFactory.newInstance().newTransformer(); t.setOutputProperty(OutputKeys.INDENT,"yes");
            StringWriter sw = new StringWriter(); t.transform(new DOMSource(doc), new StreamResult(sw)); return sw.toString();
        } catch(Exception e) { return "<response><status>ERROR</status><message>"+e.getMessage()+"</message></response>"; }
    }
    private void ap(Document doc, Element p, String tag, String text) { Element el = doc.createElement(tag); el.setTextContent(text!=null?text:""); p.appendChild(el); }
}
