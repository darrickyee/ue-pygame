from typing import Any, Callable, Mapping, Tuple

State = Any
FsmInput = Any
FsmTransition = Callable[[State, FsmInput], State]
FsmTransitionMap = Mapping[Tuple[State, FsmInput], State]
