from typing import Any, Optional


class DlgNode:

    def __init__(self, conditions: list[dict] = None) -> None:
        self.conditions: Optional[list[dict]] = conditions

    def __repr__(self):
        return f"{type(self).__name__}()"


class DlgText(DlgNode):

    def __init__(self, text: str = '', speaker: Any = None, conditions: list[dict] = None):
        super().__init__(conditions)
        self.text: str = text
        self.speaker: Any = speaker

    def __repr__(self):
        return f"{type(self).__name__}(speaker='{self.speaker}', text='{self.text}')"


class DlgEnd(DlgNode):
    pass


class DlgBranch(DlgNode):
    pass


class DlgGroup(DlgNode):
    pass
