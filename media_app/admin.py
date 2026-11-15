from django.contrib import admin
from .models import Movie, Series, Season, Episode, Genre,Ad,Music,Album,Track

import nested_admin

from django.contrib import admin
from .models import Series, Season, Episode

# --------------------- Episode Admin ---------------------
from django.contrib import admin
from .models import Episode
from .forms import EpisodeForm
import requests
from django.core.files.base import ContentFile
import os
from datetime import timedelta

from django.contrib import admin
from .models import Episode
from .forms import EpisodeForm

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    form = EpisodeForm

    fields = ['season', 'episode_number', 'video_file']  # only show these
    list_display = ('title', 'season', 'episode_number', 'is_published', 'upload_date')
    readonly_fields = ('upload_date', 'download_count')
    ordering = ('season', 'episode_number')



# --------------------- Season Admin ---------------------

from django.contrib import admin
from .models import Season
from .forms import SeasonForm

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    form = SeasonForm
    list_display = ('series', 'number', 'title')
    list_filter = ('series',)
    search_fields = ('series__title',)
    ordering = ('series', 'number')

    def save_model(self, request, obj, form, change):
        if not change:       # Only on new season creation
            obj.fetch_from_api()
        super().save_model(request, obj, form, change)


import nested_admin


from django import forms
import nested_admin
from django.contrib import admin
from .models import Series, Season

# Inline for seasons
class SeasonInline(nested_admin.NestedStackedInline):
    model = Season
    extra = 0
    fields = ('number', 'description')

# Admin form: only input title
class SeriesAdminForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['title']  # only title is input

@admin.register(Series)
class SeriesAdmin(nested_admin.NestedModelAdmin):
    form = SeriesAdminForm  # only the admin form with title
    list_display = ('title', 'release_date', 'is_published')
    search_fields = ('title',)
    inlines = [SeasonInline]

    def save_model(self, request, obj, form, change):
        # Fetch API details automatically for new objects
        if not change:
            obj.fetch_series_details()
        super().save_model(request, obj, form, change)


from django.contrib import admin
from .models import Movie, Genre

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'upload_date', 'uploaded_by', 'is_published', 'download_count')
    search_fields = ('title',)
    list_filter = ('is_published', 'release_date')
    readonly_fields = ('tmdb_id', 'poster', 'trailer_key', 'poster_url', 'backdrop_url', 'description', 'rating', 'duration', 'genres')
    fields = ('title', 'video_file', 'uploaded_by', 'upload_date', 'is_published')  # Only editable fields

    def save_model(self, request, obj, form, change):
        # Set uploaded_by automatically
        if not obj.uploaded_by:
            obj.uploaded_by = request.user

        # Call original save
        obj.save()

        # Fetch TMDb data after object exists
        if not obj.tmdb_id and obj.title:
            from django.conf import settings
            import requests
            from django.core.files.base import ContentFile
            from django.utils.text import slugify

            try:
                # 1️⃣ Search TMDb
                url = f"https://api.themoviedb.org/3/search/movie?api_key={settings.TMDB_API_KEY}&query={obj.title}"
                res = requests.get(url)
                data = res.json().get("results")
                if data:
                    movie_data = data[0]
                    obj.tmdb_id = movie_data.get("id")
                    obj.description = movie_data.get("overview", "")
                    obj.release_date = movie_data.get("release_date")
                    obj.rating = movie_data.get("vote_average")
                    obj.duration = movie_data.get("runtime")
                    poster_path = movie_data.get("poster_path")
                    backdrop_path = movie_data.get("backdrop_path")
                    obj.poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                    obj.backdrop_url = f"https://image.tmdb.org/t/p/original{backdrop_path}" if backdrop_path else None

                    # Download poster
                    if obj.poster_url:
                        img = requests.get(obj.poster_url, stream=True)
                        if img.status_code == 200:
                            obj.poster.save(
                                f"{slugify(obj.title)}.jpg",
                                ContentFile(img.content),
                                save=False
                            )

                    # Fetch trailer
                    video_url = f"https://api.themoviedb.org/3/movie/{obj.tmdb_id}/videos?api_key={settings.TMDB_API_KEY}"
                    videos = requests.get(video_url).json().get("results", [])
                    for vid in videos:
                        if vid["site"] == "YouTube" and vid["type"] == "Trailer":
                            obj.trailer_key = vid["key"]
                            break

                    # Fetch genres
                    genre_ids = movie_data.get("genre_ids", [])
                    genre_api = f"https://api.themoviedb.org/3/genre/movie/list?api_key={settings.TMDB_API_KEY}"
                    all_genres = requests.get(genre_api).json().get("genres", [])
                    for g_id in genre_ids:
                        for g in all_genres:
                            if g["id"] == g_id:
                                genre_obj, _ = Genre.objects.get_or_create(name=g["name"])
                                obj.genres.add(genre_obj)

                    # Save after updating
                    obj.save()

            except Exception as e:
                print("TMDb fetch failed:", e)

        super().save_model(request, obj, form, change)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Ad)
class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner_name', 'owner_email', 'posted_by_admin', 'created_at')
    search_fields = ('title', 'owner_name', 'owner_email', 'description')
    list_filter = ('posted_by_admin', 'created_at')
    
from django.contrib import admin
from .models import Music, Album, Track

# Inline for tracks under an album
class TrackInline(admin.TabularInline):
    model = Track
    extra = 1
    fields = ('title', 'file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'music_type', 'uploaded_by', 'created_at')
    list_filter = ('music_type', 'created_at')
    search_fields = ('title', 'artist')
    inlines = [TrackInline]
    fieldsets = (
        ('Album Details', {
            'fields': ('title', 'artist', 'music_type', 'poster')
        }),
        ('Uploader Info', {
            'fields': ('uploaded_by',),
        }),
    )


@admin.register(Music)
class MusicAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'music_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('music_type', 'uploaded_at', 'genre')
    search_fields = ('title', 'artist', 'genre')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('uploaded_at',)
    fieldsets = (
        ('Music Details', {
            'fields': ('title', 'artist', 'genre', 'music_type', 'file', 'poster')
        }),
        ('Uploader Info', {
            'fields': ('uploaded_by',),
        }),
        ('Metadata', {
            'fields': ('slug', 'uploaded_at'),
        }),
    )





from django.contrib import admin
from .models import Video

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'upload_date', 'is_published')
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_published', 'upload_date')
    search_fields = ('title', 'description')
