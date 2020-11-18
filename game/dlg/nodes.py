from typing import Any, List, Optional


class DlgNode:

    def __init__(self, condition: dict[str, Any] = None, on_enter: List[dict[str, Any]] = None) -> None:
        self.condition = condition  # pylint: disable=unsubscriptable-object
        self.on_enter = on_enter

    def __repr__(self):
        return f"{type(self).__name__}()"


class DlgText(DlgNode):

    def __init__(self, text: str = '', speaker: str = '', condition: dict[str, Any] = None):
        super().__init__(condition)
        self.text = text
        self.speaker = speaker

    def __repr__(self):
        return f"{type(self).__name__}(speaker='{self.speaker}', text='{self.text}')"


class DlgEnd(DlgNode):
    pass


class DlgBranch(DlgNode):
    pass


class DlgGroup(DlgNode):

    def __init__(self, condition: dict = None) -> None:
        super().__init__(condition=condition, on_enter=None)
