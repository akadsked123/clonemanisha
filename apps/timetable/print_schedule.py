import datetime
import uuid
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Frame, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from django.contrib import messages
import os
from django.conf import settings
from apps.timetable.schedule_instructor import instructor_timetable
from apps.user.models import AdminLoadRelease, FacultyProfile, REPLoadRelease, User
from reportlab.lib.enums import TA_CENTER
from collections import defaultdict

LONG_BOND_PAPER = (612, 936)


DAY_MAPPING = {
    'Monday': 'M',
    'Tuesday': 'T',
    'Wednesday': 'W',
    'Thursday': 'Th',
    'Friday': 'F',
    'Saturday': 'S'
}

def generate_pdf(request, result_identification, selected_instructor_id):
    unique_id = uuid.uuid4()
    header_image = os.path.join(settings.STATIC_ROOT, 'images/print_schedule/header.jpg')
    footer_image = os.path.join(settings.STATIC_ROOT, 'images/print_schedule/footer.jpg')
    instructor_timetable_data = instructor_timetable(selected_instructor_id, result_identification) if selected_instructor_id else {'instructor_timetable': []}
    
    try:
        user = get_object_or_404(User, id=selected_instructor_id)
        faculty_profile = FacultyProfile.objects.filter(user=user).first()
        user_full_name = user.get_full_name().replace(" ", "").lower()
    except User.DoesNotExist:
        messages.error(request, "No User matches the given query.")
        return None
    
    # Create the output file
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().strftime('%B')
    base_dir = os.path.join(settings.MEDIA_ROOT, 'files', str(current_year), current_month)
    os.makedirs(base_dir, exist_ok=True)
    if user_full_name:
        output_file = os.path.join(base_dir, f'{user_full_name}-{unique_id}-schedule.pdf')
    else:
        output_file = os.path.join(base_dir, f'{unique_id}-schedule.pdf')
    full_name = f"{user.first_name} {user.middle_name or ''} {user.last_name}".strip()

    if faculty_profile:
        employment_status = dict(FacultyProfile._meta.get_field('employment_status').choices).get(faculty_profile.employment_status, 'None')
        undergraduate_degrees = ", ".join([degree.name for degree in faculty_profile.undergraduate_degrees.all()]) or "None"
        graduate_degrees = ", ".join([degree.name for degree in faculty_profile.graduate_degrees.all()]) or "None"
        program_code = faculty_profile.program.program_code if faculty_profile.program else "None"
    else:
        employment_status = "None"
        undergraduate_degrees = "None"
        graduate_degrees = "None"
        program_code = "None"

    # Collect core time data
    core_time = {}
    for entry in instructor_timetable_data['instructor_timetable']:
        for view in entry['timetable_view']:
            meeting_day = view['meeting_day']
            meeting_time = view['meeting_time']
            if meeting_day not in core_time:
                core_time[meeting_day] = set()
            core_time[meeting_day].add(meeting_time)
    
    core_time_text = ", ".join([f"{day} : {', '.join(times)}" for day, times in core_time.items()])

    cell_style = ParagraphStyle(name='CellStyle', fontName='Helvetica', fontSize=10, wordWrap='CJK')
    
    # Set Data
    texts = [
        "Educational Preparation:",
        f"\tUndergraduate: <b>{undergraduate_degrees}</b>",
        f"\tGraduate: <b>{graduate_degrees}</b>",
        "Team Teach:",
        f"\tHighest Educational Attainment: <b></b>",
        f"Core Time: <b>{core_time_text}</b>",
        "Student Consultation:",
    ]

    data3 = [
        [Paragraph(f'Faculty: <b>{full_name.upper()}</b>', cell_style), Paragraph(f'Employment Status: <b>{employment_status}</b>', cell_style), Paragraph(f'Designation: <b>{faculty_profile.designation if faculty_profile else "None"}</b>', cell_style)],
        [Paragraph(f'Academic Rank: <b>{faculty_profile.academic_rank if faculty_profile else "None"}</b>', cell_style), Paragraph(f'Institute: <b>Computing</b>', cell_style), Paragraph(f'Program: <b>{program_code}</b>', cell_style)]
    ]

    progchair = User.objects.filter(
        user_type=4,
        program=user.program if user.program else None,
        institute=user.institute if user.institute else None
    ).first()
    if progchair:
        progchair_name = progchair.get_full_name().upper()
        program_code = progchair.program.program_code if progchair.program else (user.program.program_code if user.program else "")
    else:
        progchair_name = ""
        program_code = ""

    cell_style_table6 = ParagraphStyle(name='CellStyleTable6', fontName='Helvetica', fontSize=10, wordWrap='CJK')
    data6 = [
        [Paragraph(f'Prepared By:<br/><br/><b>{progchair_name}</b><br/>Program Chairperson, {program_code}', cell_style_table6), 
         Paragraph('Recommending Approval:<br/><br/><b>MARK VAN M. BULADACO</b><br/>Institute Dean', cell_style_table6)],
        ['', ''],
        [Paragraph('Approved:<br/><br/><b>GIRLEY S. GUMANAO</b><br/>VP for Academic Affairs', cell_style_table6), '']
    ]

    # Fetch AdminLoadRelease and REPLoadRelease data
    admin_load_releases = AdminLoadRelease.objects.filter(user=user)
    rep_load_releases = REPLoadRelease.objects.filter(user=user)

    data2style = ParagraphStyle(name='Centered', alignment=1, fontName='Helvetica', fontSize=8)

    data2 = [[Paragraph('<b>ADMIN LOAD RELEASE</b>', data2style), Paragraph('<b>Hour</b>', data2style), Paragraph('<b>Unit</b>', data2style)]]
    total_admin_units = 0
    if admin_load_releases.exists():
      for release in admin_load_releases:
          total_admin_units += release.unit
          data2.append([
              Paragraph(release.description, ParagraphStyle(name='CellStyle', fontName='Helvetica', fontSize=8, wordWrap='CJK')),
              Paragraph(str(release.hour), ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER)),
              Paragraph(str(release.unit), ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER))
          ])
    else:
        data2.append([
            Paragraph("None", ParagraphStyle(name='CellStyle', fontName='Helvetica', fontSize=8, wordWrap='CJK')),
            Paragraph("", ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER)),
            Paragraph("", ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER))
        ])
    data2.append([Paragraph('<b>REP LOAD RELEASE</b>', data2style), '', ''])
    total_rep_units = 0
    if rep_load_releases.exists():
      for release in rep_load_releases:
          total_rep_units += release.unit
          data2.append([
              Paragraph(release.description, ParagraphStyle(name='CellStyle', fontName='Helvetica', fontSize=8, wordWrap='CJK')),
              Paragraph(str(release.hour), ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER)),
              Paragraph(str(release.unit), ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER))
          ])
    else:
        data2.append([
            Paragraph("None", ParagraphStyle(name='CellStyle', fontName='Helvetica', fontSize=8, wordWrap='CJK')),
            Paragraph("", ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER)),
            Paragraph("", ParagraphStyle(name='Centered', fontName='Helvetica', fontSize=8, wordWrap='CJK', alignment=TA_CENTER))
        ])
    cell_style_table_1 = ParagraphStyle(name='CellStyle', fontName='Helvetica', fontSize=8, wordWrap='CJK')
    centered_style_table_1 = ParagraphStyle(name='Centered', alignment=1, fontName='Helvetica-Bold', fontSize=8, spaceAfter=0)
    centered_style_table_2 = ParagraphStyle(name='Centered', alignment=1, fontName='Helvetica', fontSize=8, spaceAfter=0)
    cell_style_table4 = ParagraphStyle(name='CellStyleTable4', fontName='Helvetica', fontSize=10, wordWrap='CJK')
    data1 = [[Paragraph('Course No.', centered_style_table_1), Paragraph('Course Title', centered_style_table_1), Paragraph('Unit', centered_style_table_1), Paragraph('Time', centered_style_table_1), Paragraph('Day', centered_style_table_1), Paragraph('Room', centered_style_table_1), Paragraph('Program /Section', centered_style_table_1), Paragraph('Hrs. Lec (a)', centered_style_table_1), Paragraph('Hrs. Lab', centered_style_table_1), Paragraph('Actual Contract Teaching Hrs/Wk', centered_style_table_1), Paragraph('.75 Eqv. (b)', centered_style_table_1), Paragraph('Total Load Eqv', centered_style_table_1)]]

    # Group entries by course_id and meeting_time
    grouped_entries = defaultdict(lambda: defaultdict(list))
    
    for entry in instructor_timetable_data['instructor_timetable']:
        for view in entry['timetable_view']:
            course_id = entry['course_id']
            meeting_time = view['meeting_time']
            grouped_entries[course_id][meeting_time].append(view)
    
    processed_course_ids = set()
    total_teaching_hours = 0
    total_load_eqv_sum = 0
    unique_course_ids = set()
    
    for course_id, times in grouped_entries.items():
        combined_views = defaultdict(list)
        for meeting_time, views in times.items():
            for view in views:
                combined_views[(course_id, view['class_group_id'])].append(view)
    
        for (course_id, class_group_id), views in combined_views.items():
            days = ''.join(DAY_MAPPING.get(view['meeting_day'], view['meeting_day']) for view in views)
            lec_units = views[0]['lec_units']
            lab_units = views[0]['lab_units'] * 3
            actual_contract_hrs = lec_units + lab_units
            eqv_b = lab_units * 0.75
            total_load_eqv = lec_units + eqv_b
    
            # Combine room and meeting times, ensuring room label is not repeated for the same room on different days
            room_days = defaultdict(lambda: {'days': set(), 'times': set()})
            for view in views:
                room_days[view['room_name']]['days'].add(DAY_MAPPING.get(view['meeting_day'], view['meeting_day']))
                room_days[view['room_name']]['times'].add(view['meeting_time'])
    
            if len(room_days) == 1:
                room_display = ', '.join(room for room in room_days.keys())
            else:
                room_display = ', '.join(f"{room} ({''.join(sorted(details['days']))})" for room, details in room_days.items())
    
            # Filter out duplicate meeting times
            unique_meeting_times = set()
            filtered_meeting_times = []
            for details in room_days.values():
                for time in sorted(details['times']):
                    if time not in unique_meeting_times:
                        unique_meeting_times.add(time)
                        filtered_meeting_times.append(time)
            meeting_times = ', '.join(filtered_meeting_times)
    
            data1.append([
                Paragraph(views[0]['course_code'], centered_style_table_2),
                Paragraph(views[0]['course_description'], cell_style_table_1),
                Paragraph(str(views[0]['credit_units']), centered_style_table_2),
                Paragraph(meeting_times, centered_style_table_2),
                Paragraph(days, centered_style_table_2),
                Paragraph(room_display, cell_style_table_1),
                Paragraph(views[0]['class_group_name'], centered_style_table_2),
                Paragraph(str(lec_units), centered_style_table_2),
                Paragraph(str(lab_units), centered_style_table_2),
                Paragraph(str(actual_contract_hrs), centered_style_table_2),
                Paragraph(str(eqv_b), centered_style_table_2),
                Paragraph(str(total_load_eqv), centered_style_table_2)
            ])
    
            unique_key = (course_id, class_group_id)
            if unique_key not in processed_course_ids:
                if views[0]['instructor_id'] == selected_instructor_id and class_group_id:
                    total_teaching_hours += actual_contract_hrs
                    total_load_eqv_sum += total_load_eqv
                    processed_course_ids.add(unique_key)
                    unique_course_ids.add(course_id)
    
    total_no_of_preparation = len(unique_course_ids)

    def format_number(number):
        return f'{number:g}' if number % 1 != 0 else f'{int(number)}'

    total_irepa_units = total_load_eqv_sum + total_admin_units + total_rep_units
    total_irepa_hours = total_teaching_hours + sum(release.hour for release in admin_load_releases) + sum(release.hour for release in rep_load_releases)

    data4 = [
        [Paragraph('Total Teaching Hours/Wk:', cell_style_table4), Paragraph(f'<b>{format_number(total_teaching_hours)}</b>', cell_style_table4), Paragraph('Total No. of Preparation:', cell_style_table4), Paragraph(f'<b>{total_no_of_preparation}</b>', cell_style_table4)],
        [Paragraph('Total MS Load Equivalent:', cell_style_table4), Paragraph(f'<b>{format_number(total_load_eqv_sum)}</b>', cell_style_table4), Paragraph('Total No. of MS Students:', cell_style_table4), Paragraph('<b>0</b>', cell_style_table4)]
    ]

    # Define a paragraph style for the table cells of Table 5
    cell_style_table5 = ParagraphStyle(name='CellStyleTable5', fontName='Helvetica', fontSize=10, wordWrap='CJK')

    # Define the fifth table data with Paragraph objects
    data5 = [
        [Paragraph('TOTAL IREPA (Instruction, Research, Extension, Production and Administrative) LOAD UNITS/WK:', cell_style_table5), Paragraph(f'<b>{format_number(total_irepa_units)}</b>', cell_style_table5)],
        [Paragraph('TOTAL IREPA (Instruction, Research, Extension, Production and Administrative) LOAD HOURS/WK:', cell_style_table5), Paragraph(f'<b>{format_number(total_irepa_hours)}</b>', cell_style_table5)]
    ]

    create_pdf_with_header_footer(output_file, header_image, footer_image, data3, texts, data6, data1, data2, full_name, data4, data5)

    return FileResponse(open(output_file, 'rb'), as_attachment=True, content_type='application/pdf')

def draw_multiline_text(c, texts, x, y, max_width, tab_width=10, footer_height=0, margin_top_bottom=0, add_new_page=None):
    styles = getSampleStyleSheet()
    style = styles['Normal']
    style.fontName = 'Helvetica'
    style.fontSize = 10
    style.leading = 13

    for text in texts:
        text = text.replace('\t', '&nbsp;' * (tab_width))
        paragraph = Paragraph(text, style)
        paragraph_height = paragraph.wrap(max_width, max_width)[1]
        if y - paragraph_height < footer_height + margin_top_bottom:
            if add_new_page:
                y = add_new_page()
        frame = Frame(x, y - max_width, max_width, max_width, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0, showBoundary=0)
        frame.addFromList([paragraph], c)
        y -= paragraph_height
    return y

def create_pdf_with_header_footer(output_file, header_image, footer_image, data3, texts, data6, data1, data2, full_name, data4, data5):
    c = canvas.Canvas(output_file, pagesize=LONG_BOND_PAPER)
    
    # Get page dimensions
    page_width, page_height = LONG_BOND_PAPER
    
    # Use ImageReader for header and footer images
    header_reader = ImageReader(header_image)
    footer_reader = ImageReader(footer_image)
    
    # Get actual dimensions of the images
    header_width, header_height = header_reader.getSize()
    footer_width, footer_height = footer_reader.getSize()
    
    # Scale images to fit the width of the page while maintaining aspect ratio
    header_scale = page_width / header_width
    footer_scale = page_width / footer_width
    
    # Calculate new dimensions for header and footer
    header_new_width = page_width
    header_new_height = header_height * header_scale
    footer_new_width = page_width
    footer_new_height = footer_height * footer_scale
    
    def draw_header_footer():
        # Draw header image at the top
        c.drawImage(header_reader, 0, page_height - header_new_height, 
                    width=header_new_width, height=header_new_height)
        
        # Draw footer image at the bottom
        c.drawImage(footer_reader, 0, 0, 
                    width=footer_new_width, height=footer_new_height)
    
    def add_new_page():
        c.showPage()
        draw_header_footer()
        return page_height - header_new_height - margin_top_bottom
    
    # Draw header and footer on the first page
    draw_header_footer()
    
    # Define margins
    margin = 36
    
    # Add content between header and footer with margins
    margin_top_bottom = 14.4  # 0.2 inches in points
    content_top = page_height - header_new_height - margin_top_bottom
    content_left = margin
    content_width = page_width - 2 * margin
 
    # Define the third table data with 3 columns (no header)
    # Define the third table data with Paragraph objects and bold formatting
    
    # Define column widths to fit the page width
    col_widths = [200, 200, 170]
    
    # Create the third table
    table3 = Table(data3, colWidths=col_widths)
    table3.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    # Draw the third table and handle page breaks
    table3.wrapOn(c, content_width, content_top)
    table3.drawOn(c, content_left, content_top - table3._height)
    content_top -= table3._height

    # Define the texts with specific words in bold
    
    # Draw multiline texts and get the updated y position
    content_top = draw_multiline_text(c, texts, content_left, content_top, content_width, footer_height=footer_new_height, margin_top_bottom=margin_top_bottom, add_new_page=add_new_page)
        
    # Add spacing between the paragraph and the table
    line_spacing = 5  # Adjust this value as needed
    content_top -= line_spacing
    
    # Define the first table data
    # Define a paragraph style for the table cells
   
    
    # Define column widths based on the expected content length
    col_widths = [38, 95, 27, 85, 36, 60, 47, 29, 30, 40, 27, 27]
    
    # Create the first table
    table1 = Table(data1, colWidths=col_widths)
    table1.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP') ,
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    # Draw the first table and handle page breaks
    table1.wrapOn(c, content_width, content_top)
    table1.drawOn(c, content_left, content_top - table1._height)
    content_top -= table1._height
    
    # Add spacing between the first and second table
    table_spacing = 10  # Adjust this value as needed
    content_top -= table_spacing


    
    # Define column widths to fit the page width
    col_widths4 = [content_width / 4] * 4
    
    # Create the fourth table
    table4 = Table(data4, colWidths=col_widths4)
    table4.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12), 
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    # Draw the fourth table and handle page breaks
    table4.wrapOn(c, content_width, content_top)
    table4.drawOn(c, content_left, content_top - table4._height)
    content_top -= table4._height

    table_spacing = 10  # Adjust this value as needed
    content_top -= table_spacing

    # Define column widths to utilize the whole width of the paper
    col_widths = [441, 50, 50]
    
    # Create the second table
    table2 = Table(data2, colWidths=col_widths)
    
    # Define the table style
    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ])
    
    # Apply the table style
    table2.setStyle(table_style)
    
    # Draw the second table and handle page breaks
    table2.wrapOn(c, content_width, content_top)
    table2.drawOn(c, content_left, content_top - table2._height)
    content_top -= table2._height

    # Add spacing between the fourth and fifth table
    table_spacing = 10  # Adjust this value as needed
    content_top -= table_spacing
    
    # Define column widths to fit the page width
    col_widths5 = [490, 50]
    
    # Create the fifth table
    table5 = Table(data5, colWidths=col_widths5)
    table5.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12), 
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    # Draw the fifth table and handle page breaks
    table5.wrapOn(c, content_width, content_top)
    table5.drawOn(c, content_left, content_top - table5._height)
    content_top -= table5._height
    
    # Add spacing between the fifth and sixth table
    table_spacing = 10  # Adjust this value as needed
    content_top -= table_spacing
    
    col_widths6 = [content_width / 2] * 2
    
    # Create the sixth table
    table6 = Table(data6, colWidths=col_widths6)
    table6.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10), 
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    
    # Draw the sixth table and handle page breaks
    table6.wrapOn(c, content_width, content_top)
    table6.drawOn(c, content_left, content_top - table6._height)
    content_top -= table6._height
    
    # Save the PDF
    c.setTitle(full_name.upper())
    c.showPage()
    c.save()