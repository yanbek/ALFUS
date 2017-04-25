from django.contrib import admin

from .models import Choice, Question, Subject, Chapter, Urls


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    
class UrlsInLine(admin.TabularInline):
    model = Urls
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
      (None, {'fields': ['question_text', 'question_image', 'difficulty', 'chapter']}),
      ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
      ('topic_text', {'fields': ['topic_text'], 'classes': ['collapse']})
    ]
    inlines = [ChoiceInline, UrlsInLine]
    list_display = ('question_text', 'topic')
    list_filter = ['topic_text']
    search_fields = ['question_text','topic_text']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Subject)
admin.site.register(Chapter)

# admin.site.site_header = "Polls Administration"
