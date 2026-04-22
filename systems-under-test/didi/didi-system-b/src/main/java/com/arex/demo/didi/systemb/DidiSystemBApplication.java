package com.arex.demo.didi.systemb;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.arex.demo.didi")
public class DidiSystemBApplication {

    public static void main(String[] args) {
        SpringApplication.run(DidiSystemBApplication.class, args);
    }
}
