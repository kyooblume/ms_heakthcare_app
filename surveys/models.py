# surveys/models.py

from django.db import models
from django.conf import settings

class Survey(models.Model):
    """アンケート全体（例：「アプリ満足度調査」）"""
    title = models.CharField(max_length=200, verbose_name='アンケートのタイトル')
    description = models.TextField(blank=True, verbose_name='説明文')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    """アンケートに含まれる個々の質問"""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='questions')
    text = models.CharField(max_length=500, verbose_name='質問文')
    QUESTION_TYPE_CHOICES = [
        ('text', '自由記述'),
        ('choice', '単一選択'),
    ]
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='text')

    def __str__(self):
        return self.text

class Choice(models.Model):
    """選択式の質問の「選択肢」"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200, verbose_name='選択肢のテキスト')

    def __str__(self):
        return self.text

class Answer(models.Model):
    """ユーザーからの回答"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text_answer = models.TextField(blank=True, null=True)
    choice_answer = models.ForeignKey(Choice, on_delete=models.CASCADE, blank=True, null=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s answer to '{self.question.text}'"
