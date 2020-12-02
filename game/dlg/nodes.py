from typing import Any, List


class DlgNode:

    def __init__(self, condition: dict[str, Any] = None, on_enter: List[dict[str, Any]] = None) -> None:
        self.condition: dict[str, Any] = condition or {}
        self.on_enter: List[dict[str, Any]] = on_enter or []

    def __repr__(self):
        return f"{type(self).__name__}()"


class DlgText(DlgNode):

    def __init__(self, condition: dict[str, Any] = None,
                 on_enter: List[dict[str, Any]] = None,
                 text: str = '',
                 speaker: str = '', ):
        super().__init__(condition, on_enter)
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
