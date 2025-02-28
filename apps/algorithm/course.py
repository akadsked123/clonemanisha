class Course:
    def __init__(self, id, program,  course_code, course_description, lecture_hours, laboratory_hours, creditHour, instructors, year_level):
        self._id = id
        self._program = program
        self._course_code = course_code
        self._course_description = course_description
        self._lecture_hours = lecture_hours
        self._laboratory_hours = laboratory_hours
        self._creditHour = creditHour
        self._is_lab = laboratory_hours > 0
        self._year_level = year_level
        self._instructors = instructors
    
    def get_id(self): return self._id
    def get_course_code(self): return self._course_code
    def get_course_description(self): return self._course_description
    def get_lecture_hours(self): return self._lecture_hours
    def get_laboratory_hours(self): return self._laboratory_hours
    def get_creditHour(self): return self._creditHour
    def get_year_level(self): return self._year_level
    def get_instructors(self): return self._instructors
    def get_program(self): return self._program
    def __str__(self): return self._id
    def __repr__(self): return self._id
    def __eq__(self, o):
        returnFlag = False
        if isinstance(o, Course):
            if o.get_id() == self._id:
                returnFlag = True
        return returnFlag
        