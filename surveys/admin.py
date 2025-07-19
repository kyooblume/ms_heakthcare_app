from django.contrib import admin
from .models import Survey, Question, Choice, Answer

# Surveyモデルの管理画面設定
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1 # 新しい質問を1つ表示

class SurveyAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]

# Questionモデルの管理画面設定
class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2 # 新しい選択肢を2つ表示

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

# 各モデルを管理画面に登録
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(Choice)