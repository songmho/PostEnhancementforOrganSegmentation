# Django Multiupload Required: pip install django-multiupload
from django import forms

from multiupload.fields import MultiFileField


class UploadForm(forms.Form):
    attachments = MultiFileField(min_num=1)
    # attachments = MultiFileField(min_num=1, max_num=3, max_file_size=1024*1024*5)


class TestForm(forms.Form):
    txt_name = forms.CharField()
    txt_pwd = forms.CharField()
    txt_addr = forms.CharField()


class Login(forms.Form):
    first_name = forms.CharField(label='first_name')
    last_name = forms.CharField(label='last_name')
    email = forms.CharField(label='email')
    cur_role = forms.CharField(label='cur_role')
    identification_number = forms.IntegerField(label='identification_number')

    def get_info(self):
        return {"first_name":self.data['first_name'], 'last_name':self.data['last_name'], "email":self.data['email'],
                "cur_role": self.data['cur_role'], 'identification_number':self.data['identification_number']}


class CurrentTestSession(forms.Form):
    program = forms.CharField(label='program')
    offering = forms.CharField(label='offering')
    evaluator = forms.CharField(label='evaluator')
    evaluator_id = forms.IntegerField(label="evaluator_id")
    test_session_id = forms.IntegerField(label="test_session_id")


class CurrentProblem(forms.Form):
    problem_id = forms.IntegerField(label='problem_id')
    problem_name = forms.CharField(label='problem_name')
    course = forms.CharField(label='course')
    problem_type = forms.CharField(label='problem_type')
    difficulty_level = forms.IntegerField(label='difficulty_level')
    question_description = forms.CharField(label='question_description')
    solution_description = forms.CharField(label='solution_description')
    solution_interpretation = forms.CharField(label='solution_interpretation')

    def get_p_id(self):
        return {'problem_id': self.data['problem_id']}


class CurrentProgram(forms.Form):
    program_id = forms.IntegerField(label='program_id')
    program_name = forms.CharField(label='program_name')
    program_start_date = forms.DateField(label='program_start_date')
    program_level = forms.IntegerField(label='program_level')
    training_duration = forms.IntegerField(label='training_duration')
    courses = forms.CharField(label='courses')
    offering_conditions = forms.CharField(label='offering_conditions')


class CurrentCourse(forms.Form):
    course_id = forms.IntegerField(label='course_id')
    course_title = forms.CharField(label='course_title')
    course_level = forms.IntegerField(label='course_level')
    teaching_methods = forms.CharField(label='teaching_methods')
    passing_conditions = forms.CharField(label='passing_conditions')


class CurrentOffering(forms.Form):
    offering_id = forms.IntegerField(label='offering_id')
    program_offering_name = forms.CharField(label='program_offering_name')
    training_program_id = forms.IntegerField(label='training_program_id')
    offering_start_date = forms.DateField(label='offering_start_date')
    max_trainees = forms.IntegerField(label='max_trainees')
    min_trainees = forms.IntegerField(label='min_trainees')
    program_status = forms.CharField(label='program_status')
    part_trainee_list = forms.CharField(label='part_trainee_list')


# References
# https://github.com/Chive/django-multiupload
# https://www.chicagodjango.com/blog/multiple-file-uploads-django/