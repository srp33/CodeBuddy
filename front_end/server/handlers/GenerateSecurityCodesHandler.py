# <copyright_statement>
#   CodeBuddy: A programming assignment management system for short-form exercises
#   Copyright (C) 2024 Stephen Piccolo
#   This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details. You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.
# </copyright_statement>

from BaseUserHandler import *
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, PageBreak, Paragraph, SimpleDocTemplate, Spacer

# The get() method displays assignments and options.
# The post() method will generate the PDF.
class GenerateSecurityCodesHandler(BaseUserHandler):
    async def get(self, course_id):
        try:
            if self.is_administrator or await self.is_instructor_for_course(course_id) or await self.is_assistant_for_course(course_id):
                course_basics = await self.get_course_basics(course_id)
                secure_assignments = self.content.get_secure_assignments(course_basics["id"])

                self.render("generate_security_codes.html", courses=self.courses, course_basics=course_basics, secure_assignments=secure_assignments, user_info=self.user_info, is_administrator=self.is_administrator, is_instructor=await self.is_instructor_for_course(course_id), is_assistant=await self.is_assistant_for_course(course_id))
            else:
                self.render("permissions.html")
        except:
            render_error(self, traceback.format_exc())

    async def post(self, course_id):
        self.set_header('Content-type', "application/pdf")
        tmp_pdf_file_path = f"/tmp/{generate_unique_id(16, 1)}.pdf"

        try:
            info_dict = ujson.loads(self.request.body)
            student_count = len(self.content.get_registered_students(course_id))

            assignment_security_code_dict = self.content.save_security_codes(course_id, info_dict["selected_assignments_ids"], info_dict["overwrite_existing"], student_count, info_dict["make_distinct"])

            secure_assignments = self.content.get_secure_assignments(course_id, info_dict["selected_assignments_ids"])

            assignment_security_codes = []

            if info_dict["make_distinct"] is True:
                if student_count == 0:
                    create_error_pdf("No students have registered for the course.", tmp_pdf_file_path)
                else:
                    for i in range(student_count):
                        for assignment_title in secure_assignments:
                            assignment_id = secure_assignments[assignment_title]["id"]
                            require_confirmation_code = secure_assignments[assignment_title]["require_security_codes"] == 2
                            codes = assignment_security_code_dict[assignment_id].pop()

                            security_code = codes[0]
                            confirmation_code = codes[1] if require_confirmation_code else None

                            assignment_security_codes.append([assignment_id, assignment_title, security_code, confirmation_code])
                    create_pdf(assignment_security_codes, tmp_pdf_file_path, info_dict["large_header"], info_dict["small_header"], info_dict["top_message"], info_dict["bottom_message"])
            else:
                for assignment_title in secure_assignments:
                    assignment_id = secure_assignments[assignment_title]["id"]
                    require_confirmation_code = secure_assignments[assignment_title]["require_security_codes"] == 2
                    codes = assignment_security_code_dict[assignment_id].pop()

                    security_code = codes[0]
                    confirmation_code = codes[1] if require_confirmation_code else None

                    assignment_security_codes.append([assignment_id, assignment_title, security_code, confirmation_code])

                create_pdf(assignment_security_codes, tmp_pdf_file_path, info_dict["large_header"], info_dict["small_header"], info_dict["top_message"], info_dict["bottom_message"])
        except:
            create_error_pdf(traceback.format_exc(), tmp_pdf_file_path)

        self.write(read_file(tmp_pdf_file_path, mode="rb"))
        os.unlink(tmp_pdf_file_path)

def create_pdf(assignment_security_codes, out_file_path, large_header_text, small_header_text, top_message_text, bottom_message_text):
    # This class enables us to create the blank boxes.
    class RectanglesFlowable(Flowable):
        def __init__(self, width, height, spacing, count):
            Flowable.__init__(self)
            self.width = width
            self.height = height
            self.spacing = spacing
            self.count = count

        def draw(self):
            # This function creates the rectangles.
            x = 0
            for i in range(self.count):
                self.canv.rect(x, 0, self.width, self.height)
                x += self.width + self.spacing

    rectangles = RectanglesFlowable(0.7 * inch, 0.9 * inch, 0.15 * inch, 4)

    # Add items for which text has been provided.
    doc = get_doc_template(out_file_path)
    elements = []

    for assignment_security_code in assignment_security_codes:
        if len(large_header_text) > 0:
            # Add the large header
            elements.append(Paragraph(large_header_text, get_large_header_style()))

        # Add the small header
        elements.append(Paragraph(assignment_security_code[1] + " " + small_header_text, get_small_header_style()))

        elements.append(Spacer(1, 0.2 * inch))
        elements.append(Paragraph("Your name: _____________________________________________________", get_paragraph_style()))
        elements.append(Paragraph("Your login ID: ____________________", get_paragraph_style()))

        elements.append(Spacer(1, 0.08 * inch))

        if len(top_message_text) > 0:
            # Add the first paragraph
            elements.append(Paragraph(top_message_text, get_paragraph_style()))

        # Add the security code
        elements.append(Paragraph(assignment_security_code[2], get_exam_code_style()))

        # Add the second paragraph
        if len(bottom_message_text) > 0 and assignment_security_code[3]:
            elements.append(Paragraph(bottom_message_text, get_small_header_style()))
            elements.append(Spacer(1, 0.1 * inch))
        
            # Add the empty rectangles
            elements.append(rectangles)

        # Add a page break after each sublist
        elements.append(PageBreak())

    # Remove the last PageBreak to avoid an extra blank page at the end
    if elements and isinstance(elements[-1], PageBreak):
        elements.pop()

    # Build the PDF
    doc.build(elements)

def create_error_pdf(message, out_file_path):
    get_doc_template(out_file_path).build([Paragraph("An error occurred when attempting to generate the PDF file.", get_small_header_style()), Paragraph(message, get_paragraph_style())])

# Define the general page structure
def get_doc_template(out_file_path):
    return SimpleDocTemplate(out_file_path, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)

def get_large_header_style():
    return ParagraphStyle(
        'LargeHeaderStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontName='Times-Bold',
        fontSize=30,
        leading=32,
        alignment=TA_LEFT,
        spaceAfter=20,
    )

def get_small_header_style():
    return ParagraphStyle(
        'SmallHeaderStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontName='Times-Bold',
        fontSize=12,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=14,
    )

def get_paragraph_style():
    return ParagraphStyle(
        'ParagraphStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontName='Times-Roman',
        fontSize=12,
        leading=14,
        spaceAfter=14,
    )

def get_exam_code_style():
    return ParagraphStyle(
        'ExamCodeStyle',
        parent=getSampleStyleSheet()['Normal'],
        fontName='Courier',
        fontSize=24,
        leading=0,
        spaceAfter=48,
    )