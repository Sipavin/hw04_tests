from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {'text': forms.Textarea(attrs={'cols': 40, 'rows': 10})}
        help_texts = {
            'text': 'Введите текст',
            'group': 'Выберите группу',
            'image': 'Выберите картинку'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Напиши комментарий',
        }
