def get_template_by_user_type(user, page):
    # Template for users
    templates = {
        'dashboard': {
            1: './pages/registrar/dashboard.html',
            2: './pages/vpaa/dashboard.html',
            3: './pages/dean/dashboard.html',
            4: './pages/progchair/dashboard.html',
        },
        'curriculum': {
            1: './pages/registrar/curriculum.html',
            4: './pages/progchair/curriculum.html',
        },
        'scheduler':{
            4: './pages/progchair/scheduler.html',
        },
        'faculty-workload':{
            4: './pages/progchair/faculty-workload.html',
            2: './pages/vpaa/faculty-workload.html',
            3: './pages/dean/faculty-workload.html',
        },
        'timetables':{
            4: './pages/progchair/timetables.html',
        },
        'courses':{
            2: './pages/vpaa/courses.html',
            4: './pages/progchair/courses.html',
            3: './pages/dean/courses.html',
        },
        'institutes':{
            1: './pages/registrar/institutes.html',
            2: './pages/vpaa/institutes.html',
        },
       
        'programs':{
            # list of institutes and program (registrar)
            1: './pages/registrar/curriculum-maintenance-and-management.html',
            2: './pages/vpaa/programs.html',
            3: './pages/dean/programs.html',
        },
        'view-program-detail':{
            # list of programs
            1: './pages/registrar/view-program-detail.html',
        },
        'update-program-detail':{
            # list of programs
            1: './pages/registrar/update-program-detail.html',
        },
        'edit-institute':{
            # list of institutes
            1: './pages/registrar/update-institute.html',
        },
        'add-program-detail':{
            # list of programs
            1: './pages/registrar/add-program-detail.html',
        },
        'faculty':{
            2: './pages/vpaa/faculty.html',
            3: './pages/dean/faculty.html',  
        },
        'my-schedule':{
            5: './pages/faculty/my-schedule.html', 
        },
        'curriculum-version':{
          1: './pages/registrar/curriculum-version.html',
          2: './pages/dean/curriculum-version.html', 
          4: './pages/progchair/curriculum-version.html', 
        },
        'assign-faculty':{
            2: './pages/vpaa/assign-faculty.html', 
            3: './pages/dean/assign-faculty.html', 
        },
        'classrooms':{
            4: './pages/progchair/classrooms.html',
        },
        'instructors':{
            4: './pages/progchair/instructors.html',
        },
        'schedule-classrooms':{
            4: './pages/progchair/customizing_schedules/schedule-classrooms.html',
        },
        'schedule-instructors':{
            4: './pages/progchair/customizing_schedules/schedule-instructors.html',
        },
        'schedule-class-groups':{
            4: './pages/progchair/customizing_schedules/schedule-class-groups.html',
        },
        'list-of-conflicts':{
            4: './pages/progchair/customizing_schedules/list-of-conflicts.html'
        },
    }
    user_type = user.user_type
    return templates.get(page, {}).get(user_type)