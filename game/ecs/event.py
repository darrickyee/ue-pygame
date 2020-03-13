

class Event(dict):

    def __init__(self, event_type: str, data=None, **kwargs):
        super().__init__(event_type=event_type, data=data, **kwargs)
        
