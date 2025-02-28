from apps.curriculum.models import Courses, Rooms

class  DataSummary:
    def __init__(self, user):
        self.user = user
        self.program = user.program

    def get_total_courses(self):
        return Courses.objects.filter(program=self.program).count()
    
    def get_rooms_count(self):
        return Rooms.objects.count()
    
    def get_all_data_summary(self):
        return {
            'total_courses' : self.get_total_courses(),
            'rooms_count' : self.get_rooms_count(),
        }
    
