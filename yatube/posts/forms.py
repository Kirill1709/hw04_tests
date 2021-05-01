from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group")
        help_texts = {
            "text": 'Введите Ваш комментарий',
            "group": 'Выберите группу',
        }
        error_messages = {
            'text': {
                'required': "Заполните комментарий",
            },
        }
