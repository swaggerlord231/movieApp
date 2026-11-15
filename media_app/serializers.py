# media_app/serializers.py
from rest_framework import serializers
from .models import Series, Season, Episode

class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ['episode_number', 'title', 'slug', 'video_file', 'description', 'poster', 'trailer', 'duration', 'is_published']

class SeasonSerializer(serializers.ModelSerializer):
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta:
        model = Season
        fields = ['number', 'description', 'episodes']

class SeriesSerializer(serializers.ModelSerializer):
    seasons = SeasonSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = ['title', 'slug', 'description', 'poster', 'trailer', 'release_date', 'genres', 'country', 'is_published', 'seasons']
