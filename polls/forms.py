from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['question', 'created_date', 'author', 'text']

    def __init__(self, *args, question_pk=None, username=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['text'].widget.attrs['autofocus'] = ''

        if question_pk:
            self.fields['question'].initial = question_pk
            self.fields['question'].disabled = True
        if username:
            self.fields['author'].initial = username
        self.fields['created_date'].disabled = True
