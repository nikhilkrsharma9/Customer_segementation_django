from django.db import models

class ChatMessage(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    session_key = models.CharField(max_length=100)

    def __str__(self):
        return f"Message {self.id}"