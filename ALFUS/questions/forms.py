from django import forms
from .models import Question, Answer

class AnswerForm(forms.Form):
    def __init__(self, question, answer):
        ##        self.generated_ids = ''
        #self.user = user
        #self.data = data
        #self.num_of_questions = num_of_questions
        self.question = question
        self.answer = answer

        #def check_answer(self):


