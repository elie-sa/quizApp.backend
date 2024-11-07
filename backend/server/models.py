from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User

class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,  editable = False )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Group(models.Model):
    name = models.CharField(max_length=30)
    members = models.ManyToManyRel(User)

class Notebook(models.Model):
    title = models.CharField(max_length = 30)
    color = models.CharField()
    
    creationDate = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True , on_delete=models.CASCADE)
    group = models.ForeignKey(Group, null = True, on_delete=models.CASCADE)
