package com.arex.demo.waimai;
import com.arex.demo.waimai.config.SharedWaimaiConfiguration;
import org.springframework.boot.SpringApplication; import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import; import org.springframework.web.client.RestTemplate; import org.springframework.context.annotation.Bean;
@SpringBootApplication @Import(SharedWaimaiConfiguration.class)
public class WaimaiCompareApplication {
    public static void main(String[] args) { SpringApplication.run(WaimaiCompareApplication.class, args); }
    @Bean public RestTemplate restTemplate() { return new RestTemplate(); }
}
