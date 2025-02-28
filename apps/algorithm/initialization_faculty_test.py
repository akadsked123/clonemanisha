def initialize(self):
        SPECIFIC_COURSE_MEETING_TIMES = {"C0012": "M0312", "C0110": "M0312"}
        SPECIFIC_COURSE_IDS = ["C0012", "C0110", "C0127", "C0146", "C0147", "C0138", "C0048", "C0049", "C0013", "C0028", "C0111", "C0127"]
        instructor_load = {}

        for class_group in self.get_classgroups():
            courses = class_group.get_scheduleCourses()
            for course in courses:
                if isinstance(course, Course):
                    newClass = Class(self._classNumb, class_group, course)
                    self._classNumb += 1
                    credit_hour = course.get_lecture_hours() + (course.get_laboratory_hours() * 3) - 0.75
                    available_meeting_times = self.get_available_meeting_times(credit_hour)

                    if course.get_instructors():
                        # Filter instructors based on their load
                        valid_instructors = [
                            instructor for instructor in course.get_instructors()
                            if instructor_load.get(instructor.get_id(), 0) + credit_hour <= 18
                        ]

                        if valid_instructors:
                            instructor = valid_instructors[rnd.randrange(len(valid_instructors))]
                            newClass.set_instructor(instructor)
                            # Update instructor's load
                            instructor_load[instructor.get_id()] = instructor_load.get(instructor.get_id(), 0) + credit_hour
                        else:
                            newClass.set_instructor(None)
                    else:
                        newClass.set_instructor(None)

                    if available_meeting_times:
                        newClass.set_meetingTime(available_meeting_times[rnd.randrange(len(available_meeting_times))])
                    else:
                        newClass.set_meetingTime(None)

                    if course.get_id() in SPECIFIC_COURSE_MEETING_TIMES:
                        specific_meeting_time_id = SPECIFIC_COURSE_MEETING_TIMES[course.get_id()]
                        specific_meeting_time = next((mt for mt in self._data['meeting_times'] if mt.get_id() == specific_meeting_time_id), None)
                        newClass.set_meetingTime(specific_meeting_time)

                    # Ensure no room is assigned to specific courses
                    if course.get_id() in SPECIFIC_COURSE_IDS:
                        newClass.set_room(None)
                    else:
                        if newClass.get_meetingTime() is not None:
                            rooms = self.get_rooms()
                            if course.get_laboratory_hours() > 0:
                                lab_rooms = [room for room in rooms if room.get_is_lab()]
                                if lab_rooms:
                                    newClass.set_room(lab_rooms[rnd.randrange(len(lab_rooms))])
                                else:
                                    newClass.set_room(None)
                            else:
                                lecture_rooms = [room for room in rooms if not room.get_is_lab()]
                                if lecture_rooms:
                                    newClass.set_room(lecture_rooms[rnd.randrange(len(lecture_rooms))])
                                else:
                                    newClass.set_room(None)
                        else:
                            newClass.set_room(None)

                    newClass.set_classGroup(class_group)
                    self._classes.append(newClass)

        return self