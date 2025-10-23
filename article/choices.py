from django.db import models


class IdeaStatus(models.TextChoices):
    CREATED = "created", "Created"
    ACCEPTED = "accepted", "Accepted"
    PROCESSED = "processed", "Processed"
    ERROR = "error", "Error"
    REJECTED = "rejected", "Rejected"
