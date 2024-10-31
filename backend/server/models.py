from django.db import models
import uuid
from django.db import models
from django.contrib.auth.models import User

class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,  editable = False )
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)