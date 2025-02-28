class Class:
    def __init__(self, id, program, course):
        self._id = '%0*d' % (4, id)
        self._program = program
        self._course = course
        self._instructor = None
        self._meetingTime = None
        self._meetingDay = None
        self._room = None
        self._classGroup = None

    def get_classGroupIds(self):
        classGroupIds = []
        for i in self._classGroup:
            classGroupIds.append(i.get_id())
        return classGroupIds
    
    def get_id(self): return self._id
    def get_program(self): return self._program
    def get_course(self): return self._course
    def get_instructor(self): return self._instructor
    def get_meetingTime(self): return self._meetingTime
    def get_meetingDay(self): return self._meetingDay
    def get_room(self): return self._room
    def get_classGroup(self): return self._classGroup
    def set_classGroup(self, classGroup): self._classGroup = classGroup
    def set_instructor(self, instructor): self._instructor = instructor
    def set_meetingTime(self, meetingTime): self._meetingTime = meetingTime
    def set_meetingDay(self, meetingDay): self._meetingDay = meetingDay
    def set_room(self, room): self._room = room
    def __repr__(self): return self.__str__()
    def __str__(self):
        return "["+ str(self.get_id()) + "," + str(self._program.get_name()) + ", " + str(self._course.get_id()) + "," + \
                str(self._room) + "," + (str(self._instructor.get_id()) if self._instructor else "None") + "," + \
                str(self._meetingTime) + "," + str(self._meetingDay) + "," + str(self._course.get_creditHour()) + "]"