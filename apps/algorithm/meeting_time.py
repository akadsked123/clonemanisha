class MeetingTime:
    def __init__(self, id, time, creditHour, conflictingTimes, roomConflictingTimes):
        self._id = id
        self._time = time
        self._creditHour = creditHour
        self._conflictingTimes = conflictingTimes
        self._roomConflictingTimes = roomConflictingTimes
    def get_id(self): return self._id
    def get_time(self): return self._time
    def get_creditHour(self): return self._creditHour
    def get_conflictingTimes(self): return self._conflictingTimes
    def get_roomConflictingTimes(self): return self._roomConflictingTimes
    def __str__(self): return self._id
    def __repr__(self): return self._id
    def __eq__(self, o) :
        returnFlag = False
        if isinstance(o, MeetingTime):
            if o.get_id() == self._id:
                returnFlag = True
        return returnFlag
    def __hash__(self): return hash(self._id)


class RoomMeetingTime:
    def __init__(self, id, time, creditHour, conflictingTimes):
        self._id = id
        self._time = time
        self._creditHour = creditHour
        self._conflictingTimes = conflictingTimes
    def get_id(self): return self._id
    def get_time(self): return self._time
    def get_creditHour(self): return self._creditHour
    def get_conflictingTimes(self): return self._conflictingTimes
    def __str__(self): return self._id
    def __repr__(self): return self._id
    def __eq__(self, o) :
        returnFlag = False
        if isinstance(o, MeetingTime):
            if o.get_id() == self._id:
                returnFlag = True
        return returnFlag
    def __hash__(self): return hash(self._id)




# class MeetingTime:
#     def __init__(self, time, creditHour):
#         self._time = time
#         self._creditHour = creditHour
#     def get_time(self): return self._time
#     def get_creditHour(self): return self._creditHour
#     def __str__(self): return self._time
#     def __repr__(self): return self._time
#     def __eq__(self, o):
#         return isinstance(o, MeetingTime) and o.get_time() == self._time
#     def __hash__(self): return hash(self._time)

# class MeetingDay:
#     def __init__(self, day, creditHour):
#         self._day = day
#         self._creditHour = creditHour
#     def get_day(self): return self._day
#     def get_creditHour(self): return self._creditHour
#     def __str__(self): return self._day
#     def __repr__(self): return self._day
#     def __eq__(self, o):
#         return isinstance(o, MeetingDay) and o.get_day() == self._day
#     def __hash__(self): return hash(self._day)
