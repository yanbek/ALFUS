from django import forms


class AnswerForm(forms.Form):
    def __init__(self, question, answer):
        ##        self.generated_ids = ''
        # self.user = user
        # self.data = data
        # self.num_of_questions = num_of_questions
        self.question = question
        self.answer = answer
        
class ChangeEmailForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = User
        fields = {
            'email',
            'password'
        }
        widgets = {
            'email': TextInput(attrs={'class': 'form-control'}),
        }

