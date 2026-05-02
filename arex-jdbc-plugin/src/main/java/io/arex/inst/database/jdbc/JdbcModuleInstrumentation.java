package io.arex.inst.database.jdbc;

import com.google.auto.service.AutoService;
import io.arex.inst.extension.ModuleDescription;
import io.arex.inst.extension.ModuleInstrumentation;
import io.arex.inst.extension.TypeInstrumentation;
import io.arex.agent.bootstrap.model.ComparableVersion;

import java.util.Arrays;
import java.util.List;

/**
 * AREX JDBC Plugin 入口
 *
 * 对标：MyBatisModuleInstrumentation
 *
 * 注册步骤：
 *   1. @AutoService 会自动在 META-INF/services/ 生成 SPI 注册文件
 *   2. 在 arex-agent-java 的 arex-instrumentation/database/ 下新建本模块
 *   3. 在上层 database/pom.xml 的 <modules> 中加入 arex-database-jdbc
 */
@AutoService(ModuleInstrumentation.class)
public class JdbcModuleInstrumentation extends ModuleInstrumentation {

    public JdbcModuleInstrumentation() {
        super("spring-jdbc", ModuleDescription.builder()
                // spring-jdbc 从 3.0 开始，目标：3.x / 4.x / 5.x / 6.x 全覆盖
                .name("spring-jdbc")
                .supportFrom(ComparableVersion.of("3.0"))
                .build());
    }

    @Override
    public List<TypeInstrumentation> instrumentationTypes() {
        return Arrays.asList(
                new JdbcTemplateInstrumentation()   // 拦截 JdbcTemplate 核心方法
                // 后续可扩展：new NamedParameterJdbcTemplateInstrumentation()
        );
    }
}
