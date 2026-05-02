package io.arex.inst.database.jdbc;

import io.arex.inst.extension.TypeInstrumentation;
import net.bytebuddy.asm.Advice;
import net.bytebuddy.description.method.MethodDescription;
import net.bytebuddy.description.type.TypeDescription;
import net.bytebuddy.matcher.ElementMatcher;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static net.bytebuddy.matcher.ElementMatchers.*;

/**
 * 拦截 JdbcTemplate 核心方法：
 *   - update(String sql, Object... args)
 *   - queryForMap(String sql, Object... args)
 *   - queryForList(String sql, Object... args)
 *   - queryForObject(String sql, Class<T> requiredType, Object... args)
 *
 * 对标：MybatisExecutorInstrumentation（同包下）
 */
public class JdbcTemplateInstrumentation extends TypeInstrumentation {

    @Override
    public ElementMatcher<TypeDescription> typeMatcher() {
        // 精确匹配 JdbcTemplate 类，不拦截子类（避免 NamedParameterJdbcTemplate 双重拦截）
        return named("org.springframework.jdbc.core.JdbcTemplate");
    }

    @Override
    public List<MethodDescription> methodMatchers() {
        return Arrays.asList(
                // update(String sql, Object... args)
                named("update")
                        .and(takesArgument(0, String.class))
                        .and(isPublic()),

                // queryForMap(String sql, Object... args)
                named("queryForMap")
                        .and(takesArgument(0, String.class))
                        .and(isPublic()),

                // queryForList(String sql, Object... args)
                named("queryForList")
                        .and(takesArgument(0, String.class))
                        .and(isPublic()),

                // queryForObject(String sql, Class requiredType, Object... args)
                named("queryForObject")
                        .and(takesArgument(0, String.class))
                        .and(isPublic())
        );
    }

    @Override
    public String adviceClassName() {
        return JdbcTemplateAdvice.class.getName();
    }

    // -------------------------------------------------------------------------
    // Advice（内部静态类，会被 ByteBuddy 内联到目标字节码中）
    // -------------------------------------------------------------------------
    @SuppressWarnings("unused")
    public static class JdbcTemplateAdvice {

        /**
         * 方法进入：
         *   - 如果处于 replay 模式，拦截调用并返回 mock 结果（skipOn 生效，跳过原方法）
         *   - 如果处于 record 模式，放行原方法，记录参数供 exit 使用
         *   - 其他情况直接放行
         *
         * @return MockResult（replay 时）或 null（record/passthrough 时）
         */
        @Advice.OnMethodEnter(skipOn = Advice.OnNonDefaultValue.class, suppress = Throwable.class)
        public static Object onEnter(
                @Advice.Origin("#m") String methodName,
                @Advice.Argument(0) String sql,
                @Advice.AllArguments Object[] allArgs) {

            return InternalJdbcExecutor.onEnter(methodName, sql, allArgs);
        }

        /**
         * 方法退出：
         *   - 如果 enter 返回了 mock（replay），用 mock 结果替换返回值
         *   - 如果是 record 模式，将实际返回值录入 AREX
         */
        @Advice.OnMethodExit(onThrowable = Throwable.class, suppress = Throwable.class)
        public static void onExit(
                @Advice.Origin("#m") String methodName,
                @Advice.Argument(0) String sql,
                @Advice.AllArguments Object[] allArgs,
                @Advice.Enter Object mockResult,
                @Advice.Return(readOnly = false) Object returnValue,
                @Advice.Thrown Throwable throwable) {

            returnValue = InternalJdbcExecutor.onExit(
                    methodName, sql, allArgs, mockResult, returnValue, throwable);
        }
    }
}
