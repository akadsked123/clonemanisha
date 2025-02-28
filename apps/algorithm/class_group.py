class ClassGroup:
    def __init__(self, id, name, year_level):
        self._id = id
        self._name = name
        self._year_level = year_level
        self._scheduleCourses = []

    def get_id(self): return self._id
    def get_name(self): return self._name
    def get_year_level(self): return self._year_level
    def get_scheduleCourses(self): return self._scheduleCourses

    def __hash__(self): return hash(self._id)
    def __str__(self): return self._id
    def __eq__(self, o):
        returnFlag = False
        if isinstance(o, ClassGroup):
            if o.get_id() == self._id:
                returnFlag = True
        return returnFlag
    def __repr__(self): return self._id