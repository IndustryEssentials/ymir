from enum import IntEnum


class VizErrorCode(IntEnum):
    general_error = 140400
    branch_not_exists = 140401
    internal_error = 140500


class MonitorErrorCode(IntEnum):
    general_error = 150400
    duplicate_task_id = 150401
    percent_log_error = 150402
    internal_error = 150500
