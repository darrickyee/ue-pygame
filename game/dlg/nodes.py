from typing import Any, Optional


class DlgNode:

    def __init__(self, condition: dict = None) -> None:
        self.condition: Optional[dict] = condition  # pylint: disable=unsubscriptable-object

    def __repr__(self):
        return f"{type(self).__name__}()"


class DlgText(DlgNode):

    def __init__(self, text: str = '', speaker: Any = None, condition: dict = None):
        super().__init__(condition)
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
