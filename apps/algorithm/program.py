class Program:
    def __init__(self, id, name, courses, program_code):
        self._id = id
        self._name = name
        self._courses = courses
        self._program_code = program_code
    def get_id(self): return self._id
    def get_name(self): return self._name
    def get_program_code(self): return self._program_code
    def get_courses(self): return self._courses
