"""Central string constants for job / result status values.

Using plain class attributes (not enum.Enum) keeps SQLAlchemy column
comparisons and JSON dict values working without .value unwrapping.
"""


class JobStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ResultStatus:
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"


class ScheduleRunStatus:
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
