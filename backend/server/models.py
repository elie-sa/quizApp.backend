from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,  editable = False )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Team(models.Model):
    name = models.CharField(max_length=30)
    members = models.ManyToManyField(User, related_name="teams")

class Major(models.Model):
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=20)

class Course(models.Model):
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=20)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="major")

class Notebook(models.Model):
    title = models.CharField(max_length = 30)
    color = models.CharField(max_length=20)
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    creation_date = models.DateTimeField(auto_now_add=True)
    user_creator = models.ForeignKey(User, null=True , on_delete=models.CASCADE, related_name="notebook")
    team_creator = models.ForeignKey(Team, null = True, on_delete=models.CASCADE, related_name="notebook")
    bookmark_users = models.ManyToManyField(User, related_name="bookmarked_notebooks")

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="ratings")
    individual_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])

#Quiz Models
class FlashDeck(models.Model):
    title = models.CharField(max_length=20)
    creation_date = models.DateTimeField(auto_now_add=True)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="flashdecks")

class FlashCard(models.Model):
    title = models.CharField(max_length=20)
    question = models.CharField(max_length=20)
    answer = models.CharField(max_length=20, blank=False)
    difficulty = models.CharField(max_length=20)
    deck = models.ForeignKey(FlashDeck, on_delete=models.CASCADE, related_name="flashcards")

class Note(models.Model):
    title = models.CharField(max_length=20)
    file_link = models.CharField(max_length=20)
    creation_date = models.DateTimeField(auto_now_add=True)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="notes")

class Quiz(models.Model):
    title = models.CharField(max_length=20)
    creation_date = models.DateTimeField(auto_now_add=True)
    difficulty = models.CharField(max_length=20)
    questionTime = models.PositiveIntegerField()
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="quizzes")

class BooleanQuestion(models.Model):
    question = models.CharField(max_length=20)
    answer = models.BooleanField(blank=False)
    points = models.FloatField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="boolean_questions")

class McqQuestion(models.Model):
    question = models.CharField(max_length=20)
    has_multiple_answers = models.BooleanField()
    points = models.FloatField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="mcq_questions")

class McqAnswer(models.Model):
    answer = models.CharField(max_length=20)
    isCorrect = models.BooleanField(blank=False)
    mcq_question = models.ForeignKey(McqQuestion, related_name="possible_answers", on_delete=models.CASCADE)