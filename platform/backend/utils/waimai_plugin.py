"""Waimai demo system plugin."""

from utils.system_plugin import SystemPlugin, register_plugin


_WAIMAI_REPOSITORY_SPECS: list[dict] = [
    {
        "full_class_name": "com.arex.demo.waimai.repository.WaimaiDataRepository",
        "database": "mysql",
        "type": "MySQL",
        "methods": [
            {
                "method_name": "insertOrder",
                "parameter_types": "java.lang.String@java.lang.String@java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["orderId", "customerId", "merchantId", "status"],
                "table": "orders",
                "operation": "INSERT orders",
                "status": "WRITE",
            },
            {
                "method_name": "updateOrderStatus",
                "parameter_types": "java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["orderId", "status"],
                "table": "orders",
                "operation": "UPDATE orders",
                "status": "WRITE",
            },
            {
                "method_name": "queryOrder",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["orderId"],
                "table": "orders",
                "operation": "SELECT orders",
                "status": "READ",
            },
            {
                "method_name": "decrementStock",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["productId"],
                "table": "products",
                "operation": "UPDATE products",
                "status": "WRITE",
            },
            {
                "method_name": "incrementStock",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["productId"],
                "table": "products",
                "operation": "UPDATE products",
                "status": "WRITE",
            },
            {
                "method_name": "insertRefund",
                "parameter_types": "java.lang.String@java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["refundId", "orderId", "status"],
                "table": "refunds",
                "operation": "INSERT refunds",
                "status": "WRITE",
            },
            {
                "method_name": "searchMerchants",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["keyword"],
                "table": "merchants",
                "operation": "SELECT merchants",
                "status": "READ",
            },
            {
                "method_name": "queryMerchant",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["merchantId"],
                "table": "merchants",
                "operation": "SELECT merchants",
                "status": "READ",
            },
            {
                "method_name": "addToCart",
                "parameter_types": "java.lang.String@java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerId", "productId", "quantity"],
                "table": "cart",
                "operation": "INSERT cart",
                "status": "WRITE",
            },
            {
                "method_name": "queryCart",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerId"],
                "table": "cart",
                "operation": "SELECT cart",
                "status": "READ",
            },
            {
                "method_name": "insertReview",
                "parameter_types": "java.lang.String@java.lang.String@java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["reviewId", "orderId", "rating"],
                "table": "reviews",
                "operation": "INSERT reviews",
                "status": "WRITE",
            },
            {
                "method_name": "queryRiderLocation",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["riderId"],
                "table": "riders",
                "operation": "SELECT riders",
                "status": "READ",
            },
            {
                "method_name": "updateWallet",
                "parameter_types": "java.lang.String@double",
                "key_formula": "#p0",
                "parameter_names": ["customerId", "amount"],
                "table": "wallets",
                "operation": "UPDATE wallets",
                "status": "WRITE",
            },
            {
                "method_name": "queryWallet",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerId"],
                "table": "wallets",
                "operation": "SELECT wallets",
                "status": "READ",
            },
            {
                "method_name": "insertSettlement",
                "parameter_types": "java.lang.String@java.lang.String@double",
                "key_formula": "#p0",
                "parameter_names": ["settlementId", "merchantId", "amount"],
                "table": "settlements",
                "operation": "INSERT settlements",
                "status": "WRITE",
            },
        ],
    },
]


class WaimaiPlugin(SystemPlugin):
    @property
    def system_name(self) -> str:
        return "waimai"

    def get_repository_specs(self) -> list[dict]:
        return _WAIMAI_REPOSITORY_SPECS


register_plugin(WaimaiPlugin())
