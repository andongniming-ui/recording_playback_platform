"""Loan demo system plugin."""

from utils.system_plugin import SystemPlugin, register_plugin


_LOAN_REPOSITORY_SPECS: list[dict] = [
    {
        "full_class_name": "com.arex.demo.loan.repository.LoanDataRepository",
        "database": "mysql",
        "type": "MySQL",
        "methods": [
            {
                "method_name": "findCustomer",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerId"],
                "table": "customer",
                "operation": "SELECT customer",
                "status": "READ",
            },
            {
                "method_name": "findProduct",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["productId"],
                "table": "product_rule",
                "operation": "SELECT product_rule",
                "status": "READ",
            },
            {
                "method_name": "isOnBlacklist",
                "parameter_types": "java.lang.String",
                "key_formula": "#p0",
                "parameter_names": ["customerId"],
                "table": "blacklist",
                "operation": "SELECT blacklist",
                "status": "READ",
            },
        ],
    },
]


class LoanPlugin(SystemPlugin):
    @property
    def system_name(self) -> str:
        return "loan"

    def get_repository_specs(self) -> list[dict]:
        return _LOAN_REPOSITORY_SPECS


register_plugin(LoanPlugin())
