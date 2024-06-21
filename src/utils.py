class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_session_state():
    return SessionState(mode=None)
