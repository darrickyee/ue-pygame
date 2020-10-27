def dispatch(name: str = None, data: str = None) -> None:
    """Dispatches an event to Unreal by calling the OnDispatch event dispatcher.

    Args:
        name (str, optional): String to be passed to the Name parameter.  Value will be coerced to FName.
        data (str, optional): String to be passed to the Data parameter (as an FString).
    """
    ...


def log(message: str = None) -> None:
    """Logs a message to the UE4 output console.

    Args:
        message (str, optional): The message to log.
    """
    ...
