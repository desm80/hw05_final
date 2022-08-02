from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
        blank=True,
        null=False,

    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='posts',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    def save(self, *args, **kwargs):
        if not self.text:
            self.text = None
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(unique=True, verbose_name='Идентификатор группы')
    description = models.TextField(blank=True, null=True,
                                   verbose_name='Описание группы')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Комментарий',
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='comments',
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария',
        blank=False,
        null=False,
    )
    created = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ('created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    IS_CLEAR = False

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Фоловер',
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Лидер мнений',
        related_name='following',
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписку'
        verbose_name_plural = 'Подписки'

    def save(self, *args, **kwargs):
        if not self.IS_CLEAR:
            self.full_clean()
        return super().save(*args, **kwargs)

    def clean(self):
        self.IS_CLEAR = True
        if (
                self.author
                and self.author.get_username() == self.user.get_username()
        ):
            raise ValidationError(
                'Пользователь не может быть подписан на себя!'
            )
        return super().clean()
