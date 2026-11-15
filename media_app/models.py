from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
import requests
from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_mb = 200  # example
    if file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"File too large. Max {max_mb} MB.")


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

import requests
from django.core.files.base import ContentFile
import requests
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.core.files.base import ContentFile
from django.conf import settings

class Movie(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    # TMDb fields
    tmdb_id = models.IntegerField(blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True)
    backdrop_url = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)  # runtime in minutes
    rating = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    genres = models.ManyToManyField('Genre', blank=True)
    trailer_key = models.CharField(max_length=50, blank=True, null=True)  # YouTube trailer ID
    trailer = models.FileField(upload_to='trailers/movies/', blank=True, null=True)
    poster = models.ImageField(upload_to='posters/movies/', blank=True, null=True)
    video_file = models.FileField(upload_to='videos/movies/', blank=True, null=True)

    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    upload_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    download_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-upload_date']

    def save(self, *args, **kwargs):
        # Generate slug if empty
        if not self.slug:
            base_slug = slugify(self.title)[:200]
            slug = base_slug
            i = 1
            while Movie.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("media_app:movie_detail", args=[self.slug])

    def __str__(self):
        return self.title


import requests
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings
import requests
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.db import models
from django.conf import settings


class Series(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    poster = models.ImageField(upload_to='posters/series/', blank=True, null=True)
    trailer = models.FileField(upload_to='trailers/series/', blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    uploaded_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.FloatField(blank=True, null=True)
    genres = models.ManyToManyField('Genre', blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    download_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-release_date']

    def save(self, *args, **kwargs):
        # ------------------------
        # 1️⃣ Auto-generate slug
        # ------------------------
        if not self.slug and self.title:
            base_slug = slugify(self.title)[:200]
            slug = base_slug
            i = 1
            while Series.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug

        # ------------------------
        # 2️⃣ Fetch TMDB details if needed
        # ------------------------
        fetched_genres = None
        if not self.description or not self.poster:
            series_data, fetched_genres = self.fetch_series_details()

            if series_data:
                self.description = series_data.get("overview") or self.description
                self.release_date = series_data.get("first_air_date") or self.release_date
                self.rating = series_data.get("vote_average", 0)
                origin_country = series_data.get("origin_country")
                if origin_country:
                    self.country = origin_country[0]

        # ------------------------
        # 3️⃣ Save instance first
        # ------------------------
        super().save(*args, **kwargs)

        # ------------------------
        # 4️⃣ Save genres
        # ------------------------
        if fetched_genres:
            self.save_genres(fetched_genres)

    def fetch_series_details(self):
        """Fetch series info + genres from TMDB API."""
        api_key = settings.TMDB_API_KEY
        from urllib.parse import quote

        title_encoded = quote(self.title)
        search_url = f"https://api.themoviedb.org/3/search/tv?api_key={api_key}&query={title_encoded}"

        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return None, None

        data = response.json()
        results = data.get("results", [])
        if not results:
            return None, None

        # pick exact match or first
        series_data = next(
            (r for r in results if r.get("name", "").lower() == self.title.lower()),
            results[0]
        )

        # ------------------------
        # Genres
        # ------------------------
        genre_ids = series_data.get("genre_ids", [])
        genre_names = []
        genre_list_url = f"https://api.themoviedb.org/3/genre/tv/list?api_key={api_key}&language=en-US"
        try:
            genre_res = requests.get(genre_list_url, timeout=10)
            genre_res.raise_for_status()
            all_genres = genre_res.json().get("genres", [])
            genre_names = [g["name"] for g in all_genres if g["id"] in genre_ids]
        except requests.RequestException:
            pass

        # ------------------------
        # Poster
        # ------------------------
        poster_path = series_data.get("poster_path")
        if poster_path and not self.poster:
            poster_url = f"https://image.tmdb.org/t/p/original{poster_path}"
            try:
                img_res = requests.get(poster_url, timeout=10)
                if img_res.status_code == 200:
                    self.poster.save(
                        f"{slugify(self.title)}.jpg",
                        ContentFile(img_res.content),
                        save=False
                    )
            except requests.RequestException:
                pass

        return series_data, genre_names

    def save_genres(self, genre_names):
        """Update ManyToMany Genre field."""
        from .models import Genre
        self.genres.clear()
        for name in genre_names:
            genre, created = Genre.objects.get_or_create(name=name)
            self.genres.add(genre)

    def __str__(self):
        return self.title

from django.db import models
from django.utils.text import slugify

from django.core.files.base import ContentFile

class Season(models.Model):
    series = models.ForeignKey('Series', related_name='seasons', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()

    # Auto-fetched fields
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    poster = models.ImageField(upload_to='posters/series/', blank=True, null=True)
    trailer = models.URLField(blank=True, null=True)
    release_date = models.DateField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    genres = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('series', 'number')
        ordering = ['number']

    def __str__(self):
        return f"{self.series.title} — Season {self.number}"

    # ---------------------------------------------------------
    # ⭐ WORKING FULL TMDB FETCH FOR SEASON DETAILS
    # ---------------------------------------------------------
    def fetch_from_api(self):
        TMDB_API_KEY = "f6e981a8634f8555e14762aebe24ea43"
        base = "https://api.themoviedb.org/3"

        # STEP 1 — Search TV By Title
        search_url = f"{base}/search/tv?api_key={TMDB_API_KEY}&query={self.series.title}"
        search_res = requests.get(search_url).json()

        if not search_res.get("results"):
            print("❌ No series found")
            return

        series_id = search_res["results"][0]["id"]

        # STEP 2 — Fetch The Season
        season_url = (
            f"{base}/tv/{series_id}/season/{self.number}"
            f"?api_key={TMDB_API_KEY}&append_to_response=videos"
        )

        season_data = requests.get(season_url).json()

        # TITLE
        raw_title = season_data.get("name")
        self.title = raw_title or f"{self.series.title} — Season {self.number}"

        # DESCRIPTION
        self.description = season_data.get("overview") or "No description available."

        # BASIC FIELDS
        self.release_date = season_data.get("air_date")
        self.rating = season_data.get("vote_average")

        # GENRES
        self.genres = ", ".join([g["name"] for g in season_data.get("genres", [])])

        # COUNTRIES
        self.country = ", ".join([c["name"] for c in season_data.get("production_countries", [])])

        # POSTER
        poster_path = season_data.get("poster_path")
        if poster_path:
            image_url = f"https://image.tmdb.org/t/p/original{poster_path}"
            img_content = requests.get(image_url).content
            self.poster.save(
                f"{self.series.slug}_season_{self.number}.jpg",
                ContentFile(img_content),
                save=False
            )

        # TRAILER
        videos = season_data.get("videos", {}).get("results", [])
        trailer = next(
            (v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"),
            None
        )
        if trailer:
            self.trailer = f"https://www.youtube.com/watch?v={trailer['key']}"

class Episode(TimestampedModel):
    season = models.ForeignKey(Season, related_name='episodes', on_delete=models.CASCADE)
    episode_number = models.PositiveIntegerField()
    video_file = models.FileField(upload_to='videos/episodes/', blank=True, null=True)
    # Auto-fetched fields from api
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    poster = models.ImageField(upload_to='posters/episodes/', blank=True, null=True)
    trailer = models.FileField(upload_to='trailers/episodes/', blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    genres = models.ManyToManyField(Genre, blank=True)  # If fetched from API
    duration = models.DurationField(blank=True, null=True)
    upload_date = models.DateTimeField(default=timezone.now)
    download_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        unique_together = ('season', 'episode_number')
        ordering = ['episode_number']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.season.series.title}-s{self.season.number}-e{self.episode_number}-{self.title}")[:250]
            slug = base
            i = 1
            while Episode.objects.filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('media_app:episode_detail', args=[self.season.series.slug, self.season.number, self.slug])

    def __str__(self):
        return f"{self.season.series.title} S{self.season.number}E{self.episode_number}: {self.title}"


from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=100, blank=True)  # for guests
    email = models.EmailField(blank=True)  # for guests
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic relation to Movie, Series, or Episode
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        display_name = self.user.username if self.user else self.name
        return f"Review by {display_name or 'Anonymous'} on {self.content_object}"


class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    media_file = models.FileField(upload_to='ads/', blank=True, null=True)  # video or image
    owner_name = models.CharField(max_length=100)
    owner_email = models.EmailField()
    owner_phone = models.CharField(max_length=20, blank=True, null=True)
    posted_by_admin = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_video(self):
        if self.media_file:
            return self.media_file.url.lower().endswith(('.mp4', '.webm', '.ogg'))
        return False

    def is_image(self):
        if self.media_file:
            return self.media_file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        return False

    def __str__(self):
        return self.title


# music_app/models.py
from django.db import models
from django.contrib.auth.models import User

def music_file_path(instance, filename):
    # Path for individual track files
    return f'music/{instance.album.artist}/{filename}' if hasattr(instance, 'album') else f'music/{instance.artist}/{filename}'

def poster_file_path(instance, filename):
    # Path for album or single poster
    return f'music_posters/{instance.artist}/{filename}'


class Music(models.Model):
    MUSIC_TYPES = [
        ('album', 'Album'),
        ('ep', 'EP'),
        ('single', 'Single'),
        ('mixtape', 'Mixtape'),
    ]

    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, blank=True, null=True)
    music_type = models.CharField(max_length=20, choices=MUSIC_TYPES, default='single')
    file = models.FileField(upload_to='music/')
    poster = models.ImageField(upload_to='music_posters/', blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)
    download_count = models.PositiveIntegerField(default=0)  # ✅ added

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.artist}")
            slug = base_slug
            counter = 1
            while Music.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} by {self.artist}"


class Album(models.Model):
    """Represents an Album or EP"""
    ALBUM_TYPES = [
        ('album', 'Album'),
        ('ep', 'EP'),
    ]

    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    music_type = models.CharField(max_length=20, choices=ALBUM_TYPES)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    poster = models.ImageField(upload_to='album_posters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_music_type_display()}) by {self.artist}"


class Track(models.Model):
    """Represents a track that belongs to an Album or EP"""
    album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=music_file_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0)  # ✅ added

    def __str__(self):
        return f"{self.title} - {self.album.title} by {self.album.artist}"


from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth.models import User

class Video(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    
    # Video files
    video_mp4 = models.FileField(upload_to='videos/', blank=True, null=True)
    video_webm = models.FileField(upload_to='videos/', blank=True, null=True)
    
    poster = models.ImageField(upload_to='videos/posters/', blank=True, null=True)
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    upload_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-upload_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:200]
            slug = base_slug
            i = 1
            while Video.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('media_app:video_detail', args=[self.slug])
