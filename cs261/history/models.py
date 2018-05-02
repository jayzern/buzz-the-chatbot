from django.db import models

class Query(models.Model):
    text = models.CharField(max_length=254)
    created_at = models.DateTimeField(auto_now_add=True)
    intent = models.CharField(max_length=255)
    entities = models.ManyToManyField('Entity')

    def __str__(self):
        return self.text

class Entity(models.Model):
    name = models.CharField(max_length=255)
    entity_type = models.CharField(max_length=255)

    def __str__(self):
        return self.entity_type + '/' + self.name
