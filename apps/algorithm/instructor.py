class Instructor:
    def __init__(self, id, name, courses, availability):
        self._id = id
        self._name = name
        self._courses = courses
        self._availability = availability
    def get_id(self): return self._id
    def get_name(self): return self._name
    def get_courses(self): return self._courses
    def get_availability(self): return self._availability
    def get_creditHourAvailability(self, creditHour):
        returnAvailability = []
        for i in range(0, len(self._availability)):
            if self._availability[i].get_creditHour() == creditHour:
                returnAvailability.append(self._availability[i])
        return returnAvailability
    def __eq__(self, o: object):
        returnFlag = False
        if isinstance(o, Instructor):
            if o.get_id() == self._id:
                returnFlag = True
        return returnFlag
    def __hash__(self): return hash(self._id)
    def __repr__(self): return self._id
    def __str__(self): return self._id