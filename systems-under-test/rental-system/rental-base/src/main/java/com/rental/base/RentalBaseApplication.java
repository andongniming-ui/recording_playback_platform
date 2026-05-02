package com.rental.base;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication(scanBasePackages = "com.rental.base")
public class RentalBaseApplication {
    public static void main(String[] args) {
        SpringApplication.run(RentalBaseApplication.class, args);
    }
}
