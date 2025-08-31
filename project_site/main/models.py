from django.db import models
from django.contrib.auth.models import User

class MessageBoard(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_boards')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class Message(models.Model):
    board = models.ForeignKey(MessageBoard, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['-created_at']
