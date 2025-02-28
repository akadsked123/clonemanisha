class Classroom:
    def __init__(self, id, roomName, is_lab):
        self._id = id
        self._roomName = roomName
        self._is_lab = is_lab
    def get_id(self): return self._id
    def get_roomName(self): return self._roomName
    def get_is_lab(self): return self._is_lab
    def __str__(self): return self._id
    def __repr__(self): return self._id
    def __hash__(self): return hash(self._id)
    def __eq__(self, o):
        returnFlag = False
        if isinstance(o, Classroom):
            if o.get_id() == self._id:
                returnFlag = True
        return returnFlag