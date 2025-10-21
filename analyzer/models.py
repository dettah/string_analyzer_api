from django.db import models

class StringAnalysis(models.Model):
    # id field
    id = models.CharField(max_length=64, primary_key=True)
    
    # Input text value
    value = models.TextField(unique=True)
    
    # properties of the value entered
    properties = models.JSONField()
    
    # Time stamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return self.value
    
    