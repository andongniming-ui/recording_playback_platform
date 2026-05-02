package com.arex.demo.dating.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@ComponentScan(basePackages = "com.arex.demo.dating")
public class DatingAppApplication {

    public static void main(String[] args) {
        SpringApplication.run(DatingAppApplication.class, args);
    }
}
