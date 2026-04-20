package com.arex.demo.didi.systema;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.arex.demo.didi")
public class DidiSystemAApplication {

    public static void main(String[] args) {
        SpringApplication.run(DidiSystemAApplication.class, args);
    }
}
