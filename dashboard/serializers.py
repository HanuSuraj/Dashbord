from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField()  # Display the author's username

    class Meta:
        model = Article
        fields = ["title", "author", "publishedAt", "type"]
