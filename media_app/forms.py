from django import forms
from .models import Movie, Episode, Series, Season

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'video_file']


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['title','description','poster','trailer','release_date','genres','is_published','rating']


# media_app/forms.py
from django import forms
from .models import Season

from django import forms
from .models import Season

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['series', 'number']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fetch_from_api()   # ⭐ auto fetch details
        if commit:
            instance.save()
        return instance

from django import forms
from .models import Episode, Season
from django.core.files.base import ContentFile
from django.utils.text import slugify
from datetime import timedelta
import requests
import os
from django.conf import settings  # Make sure TMDB_API_KEY is in settings

# forms.py
from django import forms
from .models import Episode, Season
import requests, os
from django.core.files.base import ContentFile
from datetime import timedelta

import os
import requests
from urllib.parse import quote
from difflib import SequenceMatcher
from django import forms
from django.core.files.base import ContentFile
from .models import Episode, Season
from django.conf import settings

TMDB_API_KEY = settings.TMDB_API_KEY  # make sure this is set in settings.py

class EpisodeForm(forms.ModelForm):
    class Meta:
        model = Episode
        fields = ['season', 'episode_number', 'video_file']

    season = forms.ModelChoiceField(
        queryset=Season.objects.select_related('series').all(),
        label="Series - Season",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    episode_number = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    video_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    def save(self, commit=True):
        episode = super().save(commit=False)

        series_title = episode.season.series.title
        season_number = episode.season.number
        episode_number = episode.episode_number

        # URL encode the series title
        encoded_title = quote(series_title)

        # Search series on TMDB
        search_url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={encoded_title}"
        try:
            search_res = requests.get(search_url).json()
            results = search_res.get('results', [])

            if results:
                # Pick best match by comparing series names
                best_match = max(
                    results,
                    key=lambda r: SequenceMatcher(None, r['name'].lower(), series_title.lower()).ratio()
                )
                tmdb_id = best_match['id']

                # Fetch season details
                season_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_number}?api_key={TMDB_API_KEY}"
                season_res = requests.get(season_url).json()
                episodes_data = season_res.get('episodes', [])

                # Find the specific episode
                ep_data = next((e for e in episodes_data if e['episode_number'] == episode_number), None)

                if ep_data:
                    episode.title = ep_data.get('name', f"Episode {episode_number}")
                    episode.description = ep_data.get('overview', "")
                    episode.rating = ep_data.get('vote_average', None)

                    # Poster
                    poster_path = ep_data.get('still_path')
                    if poster_path:
                        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        episode.poster = ContentFile(
                            requests.get(poster_url).content,
                            name=os.path.basename(poster_path)
                        )

                    # Print debug info
                    print(f"Fetched episode: {episode.title}, Rating: {episode.rating}")

                else:
                    episode.title = f"Episode {episode_number}"
                    print(f"Episode {episode_number} not found in season {season_number} on TMDB.")

            else:
                episode.title = f"Episode {episode_number}"
                print(f"No TMDB results for series '{series_title}'. Using default title.")

        except Exception as e:
            episode.title = f"Episode {episode_number}"
            print("TMDB fetch failed:", e)

        if commit:
            episode.save()

        return episode

from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["name", "email", "rating", "comment"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your name",
                "required": True
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Your email",
                "required": True
            }),
            "rating": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 5,
                "placeholder": "Rate 1–5"
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Write your review..."
            }),
        }


# music_app/forms.py
from django import forms
from .models import Music, Album, Track

class MusicUploadForm(forms.ModelForm):
    class Meta:
        model = Music
        fields = ['title', 'artist', 'genre', 'music_type', 'file', 'poster']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'artist': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'music_type': forms.Select(attrs={'class': 'form-select', 'id': 'musicTypeSelect'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'singleFileInput'}),
            'poster': forms.FileInput(attrs={'class': 'form-control'}),
        }
