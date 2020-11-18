from .types import State, FsmInput, FsmTransitionMap


def from_input(_: State, fsm_input: FsmInput = None) -> State:
    """Sets the next state to the input value (ignores the current state).
    """
    return fsm_input


def from_map(transition_map: FsmTransitionMap):
    """Returns a transition function that implements the transitions specified
    by `transition_map`.  The current state is returned if the `(state, fsm_input)`
    is not found in the mapping's keys.

    Args:
        transition_map (FsmTransitionMap): A Mapping where each key is a `(state, fsm_input)`
        tuple and its value is the corresponding next state.
    """

    def transition(state: State, fsm_input: FsmInput):
        return transition_map.get((state, fsm_input), state)

    return transition
