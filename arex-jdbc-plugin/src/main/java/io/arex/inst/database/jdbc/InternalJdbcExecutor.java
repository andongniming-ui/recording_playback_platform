package io.arex.inst.database.jdbc;

import io.arex.agent.bootstrap.model.MockResult;
import io.arex.inst.database.common.DatabaseExtractor;
import io.arex.inst.runtime.context.ContextManager;

import java.util.Arrays;

/**
 * JdbcTemplate 录制/回放核心逻辑。
 *
 * 职责：
 *   onEnter() — replay 模式时返回 MockResult（触发 ByteBuddy skipOn，跳过原方法）
 *   onExit()  — record 模式时把实际返回值写入 AREX；replay 时把 mock 解包为真正返回值
 *
 * 对标：MybatisExecutorWrapper（io.arex.inst.database.mybatis3）
 *
 * NOTE: 此类方法均为静态，因为 ByteBuddy @Advice 要求 helper 以静态方式调用。
 */
public final class InternalJdbcExecutor {

    private InternalJdbcExecutor() {}

    // -------------------------------------------------------------------------
    // onEnter：在原方法执行前调用
    // -------------------------------------------------------------------------

    /**
     * @return MockResult（非 null）时 ByteBuddy 会跳过原方法；
     *         null 时正常执行原方法。
     */
    public static Object onEnter(String methodName, String sql, Object[] allArgs) {
        if (ContextManager.needReplay()) {
            // replay 模式：用录制参数构造 extractor，查询 mock 数据
            DatabaseExtractor extractor = buildExtractor(sql, allArgs, methodName);
            MockResult mockResult = extractor.replay();
            // MockResult 非 null 则返回，触发 skipOn；若 mock 找不到也返回 null 放行原方法
            return mockResult;
        }
        // record 模式 / passthrough：放行原方法
        return null;
    }

    // -------------------------------------------------------------------------
    // onExit：在原方法执行后（或被跳过后）调用
    // -------------------------------------------------------------------------

    /**
     * @param mockResult  onEnter 的返回值（replay 时为 MockResult，其他情况为 null）
     * @param returnValue 原方法实际返回值（replay 被跳过时为默认值 null/0）
     * @param throwable   原方法抛出的异常（未抛出时为 null）
     * @return 最终要返回给调用方的值
     */
    public static Object onExit(
            String methodName,
            String sql,
            Object[] allArgs,
            Object mockResult,
            Object returnValue,
            Throwable throwable) {

        if (mockResult instanceof MockResult) {
            // replay 模式：解包 mock 数据作为最终返回值
            MockResult result = (MockResult) mockResult;
            if (result.notIgnoreMockResult()) {
                return result.getResult();
            }
            return returnValue;
        }

        if (ContextManager.needRecord()) {
            // record 模式：将真实返回值（或异常）录入 AREX
            DatabaseExtractor extractor = buildExtractor(sql, allArgs, methodName);
            if (throwable != null) {
                extractor.recordDb(throwable);
            } else {
                extractor.recordDb(returnValue);
            }
        }

        return returnValue;
    }

    // -------------------------------------------------------------------------
    // 内部工具
    // -------------------------------------------------------------------------

    /**
     * 构造 DatabaseExtractor。
     *
     * DatabaseExtractor(String sql, String parameters, String methodName)
     *   - sql:        原始 SQL 字符串
     *   - parameters: 参数列表序列化为字符串（AREX 用于 mock 匹配）
     *   - methodName: 方法名（update / queryForMap / queryForList / queryForObject）
     *
     * 参数序列化：取 allArgs[1..] 去掉第一个 sql 参数；
     * 如果最后一个参数是 Object[]（可变参），展开后再序列化。
     */
    private static DatabaseExtractor buildExtractor(String sql, Object[] allArgs, String methodName) {
        String parameters = serializeParameters(allArgs);
        return new DatabaseExtractor(sql, parameters, methodName);
    }

    /**
     * 将方法参数序列化为字符串供 AREX 匹配使用。
     * allArgs[0] 是 sql，从 allArgs[1] 开始才是真正的绑定参数。
     */
    private static String serializeParameters(Object[] allArgs) {
        if (allArgs == null || allArgs.length <= 1) {
            return "";
        }
        // allArgs[1] 可能是 Object[]（JdbcTemplate 可变参展开后），也可能是单个值
        if (allArgs.length == 2 && allArgs[1] instanceof Object[]) {
            return Arrays.toString((Object[]) allArgs[1]);
        }
        // 截取从 index 1 开始的部分
        Object[] params = Arrays.copyOfRange(allArgs, 1, allArgs.length);
        return Arrays.toString(params);
    }
}
