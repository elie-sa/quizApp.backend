from django.contrib import admin
from .models import Major, Course, Profile, Notebook, Team, FlashDeck, FlashCard, Quiz, McqAnswer, McqQuestion, BooleanQuestion, Note

admin.site.register(Major)
admin.site.register(Course)
admin.site.register(Profile)
admin.site.register(Notebook)
admin.site.register(Team)
admin.site.register(FlashDeck)
admin.site.register(FlashCard)
admin.site.register(Quiz)
admin.site.register(McqAnswer)
admin.site.register(McqQuestion)
admin.site.register(BooleanQuestion)
admin.site.register(Note)