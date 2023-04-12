from app.constants.state import FinalStates
from app.schemas.task import TaskResultUpdateMessage


def message_filter(message: TaskResultUpdateMessage) -> bool:
    """
    check if message meet the following criteria:
    - Task state in FinalStates (done, error or terminated)
    """
    return message.state in FinalStates
