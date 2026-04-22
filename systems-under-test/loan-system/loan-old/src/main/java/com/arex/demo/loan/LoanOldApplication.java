package com.arex.demo.loan;
import com.arex.demo.loan.config.SharedLoanConfiguration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;
import org.springframework.web.client.RestTemplate;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
@Import(SharedLoanConfiguration.class)
public class LoanOldApplication {
    public static void main(String[] args) { SpringApplication.run(LoanOldApplication.class, args); }
    @Bean
    public RestTemplate restTemplate() { return new RestTemplate(); }
}
