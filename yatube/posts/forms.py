from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True
        self.fields['text'].label = 'Текст поста'
        self.fields['group'].label = 'Группа'
        self.fields['group'].help_text = (
            "Группа, к которой будет относиться пост")

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].required = True

    class Meta:
        model = Comment
        fields = ('text',)
