package com.rental.base.config;

import com.rental.base.interceptor.TransactionLogInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.converter.xml.MappingJackson2XmlHttpMessageConverter;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.charset.StandardCharsets;
import java.util.Collections;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();
        MappingJackson2XmlHttpMessageConverter converter = new MappingJackson2XmlHttpMessageConverter();
        converter.setSupportedMediaTypes(Collections.singletonList(
            new org.springframework.http.MediaType("application", "xml", StandardCharsets.UTF_8)
        ));
        restTemplate.getMessageConverters().add(0, converter);
        return restTemplate;
    }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(new TransactionLogInterceptor(jdbcTemplate))
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/internal/**");
    }
}
