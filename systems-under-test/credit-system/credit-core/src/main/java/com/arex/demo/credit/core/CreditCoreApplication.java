package com.arex.demo.credit.core;

import com.arex.demo.credit.config.SharedCreditConfiguration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;

@SpringBootApplication(scanBasePackages = "com.arex.demo.credit")
@Import(SharedCreditConfiguration.class)
public class CreditCoreApplication {
    public static void main(String[] args) {
        SpringApplication.run(CreditCoreApplication.class, args);
    }
}
