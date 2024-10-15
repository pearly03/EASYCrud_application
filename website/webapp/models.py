from django.db import models


class UserData(models.Model):
    id = models.AutoField(primary_key=True)  # Optional: Django automatically adds a primary key
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
# Creating MModel For Document Upload

class Document(models.Model):
    file = models.FileField(upload_to='documents/')  # Files will be saved to media/documents/
    uploaded_at = models.DateTimeField(auto_now_add=True)



