from django import forms

from .models import Problems, Test_logs


class ProblemForm(forms.ModelForm):

    class Meta:
        model = Problems
        fields = ('tag_UK', 'problem', 'answer',)


class Test_oneq_Form(forms.ModelForm):

    class Meta:
        model = Test_logs
        fields = ('problem_no', 'tag_UK', 'user', 'response', 'correct',)