from django.db import models

class Email(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.EmailField()
    receiver = models.EmailField()
    subject = models.TextField(max_length=998)
    body = models.TextField()
    failed = models.BooleanField(blank=True, null=True)
    
    def to_string(self):
        as_string = f"""SUBJECT: 
{self.subject}
BODY:
{self.body}"""
        return as_string
    
    def __str__(self):
        return f"Email from {self.sender} to {self.receiver}"