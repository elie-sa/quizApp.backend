from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
import pyotp

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)
    secret_key = models.CharField(max_length=32, blank=True, null=True)

    def generate_secret_key(self):
        self.secret_key = pyotp.random_base32()
        self.save()

    def __str__(self):
        return self.user.username

class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,  editable = False )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Team(models.Model):
    name = models.CharField(max_length=50)
    creation_date = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name="teams")

    def __str__(self):
        return self.name

class Major(models.Model):
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Course(models.Model):
    code = models.CharField(max_length=4)
    name = models.CharField(max_length=50)
    major = models.ForeignKey(Major, on_delete=models.CASCADE, related_name="courses")

    def __str__(self):
        return self.name

class Notebook(models.Model):
    title = models.CharField(max_length = 50)
    color = models.CharField(max_length=20)
    rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)], null = True, default=None)
    creation_date = models.DateTimeField(auto_now_add=True)
    user_creator = models.ForeignKey(User, null=True , on_delete=models.CASCADE, related_name="notebook")
    team_creator = models.ForeignKey(Team, null = True, on_delete=models.CASCADE, related_name="notebook")
    bookmark_users = models.ManyToManyField(User, related_name="bookmarked_notebooks")
    courses = models.ManyToManyField(Course, related_name="notebooks")
    public_access = models.BooleanField(default = False)

    def __str__(self):
        return self.title

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="ratings")
    individual_rating = models.PositiveIntegerField(validators=[MaxValueValidator(5)])

#Quiz Models
class FlashDeck(models.Model):
    title = models.CharField(max_length=20)
    creation_date = models.DateTimeField(auto_now_add=True)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="flashdecks")

    def __str__(self):
        return f"{self.title}: {self.id}"

class FlashCard(models.Model):
    title = models.CharField(max_length=20)
    question = models.CharField(max_length=400)
    answer = models.CharField(max_length=400, blank=False)
    difficulty = models.CharField(max_length=20)
    deck = models.ForeignKey(FlashDeck, on_delete=models.CASCADE, related_name="flashcards")

    def __str__(self):
        return f"{self.title}: {self.id}"

class Note(models.Model):
    title = models.CharField(max_length=50)
    file_link = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="notes")

    def __str__(self):
        return self.title

class Quiz(models.Model):
    title = models.CharField(max_length=20)
    creation_date = models.DateTimeField(auto_now_add=True)
    difficulty = models.CharField(max_length=20)
    questionTime = models.PositiveIntegerField()
    notebook = models.ForeignKey(Notebook, on_delete=models.CASCADE, related_name="quizzes")

    def __str__(self):
        return self.title

class BooleanQuestion(models.Model):
    question = models.CharField(max_length=20)
    answer = models.BooleanField(blank=False)
    points = models.FloatField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="boolean_questions")

class McqQuestion(models.Model):
    question = models.CharField(max_length=20)
    points = models.FloatField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="mcq_questions")

class McqAnswer(models.Model):
    answer = models.CharField(max_length=20)
    isCorrect = models.BooleanField(blank=False)
    mcq_question = models.ForeignKey(McqQuestion, related_name="possible_answers", on_delete=models.CASCADE)