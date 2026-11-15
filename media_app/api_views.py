# media_app/api_views.py
from rest_framework import generics
from .models import Series
from .serializers import SeriesSerializer

# List all series
class SeriesListAPIView(generics.ListAPIView):
    queryset = Series.objects.filter(is_published=True)
    serializer_class = SeriesSerializer

# Retrieve one series with all seasons & episodes
class SeriesDetailAPIView(generics.RetrieveAPIView):
    queryset = Series.objects.filter(is_published=True)
    serializer_class = SeriesSerializer
    lookup_field = 'slug'
