import os
from . import models
from django.shortcuts import get_object_or_404, render, redirect
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from .models import Movie, Series, Season, Episode, Ad,Music
from .forms import MovieForm, EpisodeForm, SeriesForm, SeasonForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Series

# -------------------
# SIGN UP
# -------------------
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('media_app:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'media_app/auth/signup.html', {'form': form})

# -------------------
# SIGN IN
# -------------------
def signin_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Logged in successfully!")
            return redirect('media_app:dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'media_app/auth/signin.html', {'form': form})

# -------------------
# DASHBOARD
# -------------------
@login_required
def dashboard_view(request):
    # Example: show latest series
    latest_series = Series.objects.all().order_by('-id')[:5]
    return render(request, 'media_app/dashboard/user_dashboard.html', {'latest_series': latest_series})




def privacy_policy(request):
    return render(request, "media_app/privacy_policy.html")

def terms_conditions(request):
    return render(request, "media_app/terms.html")

def faq_page(request):
    return render(request, "media_app/faq.html")

# -------------------
# SERIES DETAIL
# -------------------
# @login_required
# def series_detail(request, series_slug):
#     series = get_object_or_404(Series, slug=series_slug)
#     seasons = series.seasons.all()
#     return render(request, 'media_app/series_detail.html', {'series': series, 'seasons': seasons})

def index(request):
    movies = Movie.objects.filter(is_published=True).order_by('-upload_date')
    series_list = Series.objects.filter(is_published=True).order_by('title')
    ads = Ad.objects.filter(posted_by_admin=True).order_by('-created_at')  # get only admin-posted ads
    music_files = Music.objects.all().order_by('-uploaded_at')  # get all uploaded music

    return render(request, 'media_app/index.html', {
        'movies': movies,
        'series_list': series_list,
        'ads': ads,
        'music_files': music_files,  # pass music to template
    })



def movie_list(request):
    movies = Movie.objects.filter(is_published=True).order_by('-upload_date')
    return render(request, 'media_app/movie_list.html', {'movies': movies})


def contact_us(request):
    movies = Movie.objects.filter(is_published=True).order_by('-upload_date')
    return render(request, 'media_app/contact_us.html', {'movies': movies})
def about_us(request):
    movies = Movie.objects.filter(is_published=True).order_by('-upload_date')
    return render(request, 'media_app/about_us.html', {'movies': movies})
def terms(request):
    movies = Movie.objects.filter(is_published=True).order_by('-upload_date')
    return render(request, 'media_app/terms.html', {'movies': movies})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from .models import Movie, Series, Season, Episode, Review
from .forms import ReviewForm


def movie_detail(request, slug):
    """Display movie details and handle reviews."""
    movie = get_object_or_404(Movie, slug=slug, is_published=True)
    content_type = ContentType.objects.get_for_model(Movie)
    reviews = Review.objects.filter(content_type=content_type, object_id=movie.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.content_type = content_type
            review.object_id = movie.id
            if request.user.is_authenticated:
                review.user = request.user
                review.name = request.user.get_full_name() or request.user.username
                review.email = request.user.email
            review.save()
            return redirect(request.path)
    else:
        form = ReviewForm()

    return render(request, "media_app/movie_detail.html", {
        "movie": movie,
        "media_type": "movie",
        "form": form,
        "reviews": reviews,
    })


def episode_detail(request, series_slug, season_number, episode_slug):
    """Display episode details and handle reviews."""
    series = get_object_or_404(Series, slug=series_slug, is_published=True)
    season = get_object_or_404(series.seasons, number=season_number)
    episode = get_object_or_404(season.episodes, slug=episode_slug, is_published=True)

    content_type = ContentType.objects.get_for_model(Episode)
    reviews = Review.objects.filter(content_type=content_type, object_id=episode.id)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.content_type = content_type
            review.object_id = episode.id
            if request.user.is_authenticated:
                review.user = request.user
                review.name = request.user.get_full_name() or request.user.username
                review.email = request.user.email
            review.save()
            return redirect(request.path)
    else:
        form = ReviewForm()

    return render(request, "media_app/episode_detail.html", {
        "episode": episode,
        "media_type": "episode",
        "form": form,
        "reviews": reviews,
    })



def series_detail(request, series_slug):
    # Fetch the series
    series = get_object_or_404(Series, slug=series_slug, is_published=True)
    
    # Fetch all seasons and prefetch episodes for efficiency
    seasons = series.seasons.prefetch_related('episodes').all()
    

    return render(request, 'media_app/series_detail.html', {
        'series': series,
        'seasons': seasons
    })



def season_detail(request, series_slug, season_number):
    series = get_object_or_404(Series, slug=series_slug, is_published=True)
    season = get_object_or_404(series.seasons, number=season_number)
    episodes = season.episodes.filter(is_published=True)
    return render(request, 'media_app/season_detail.html', {
        'series': series,
        'season': season,
        'episodes': episodes
    })


def series_list(request):
    series = Series.objects.filter(is_published=True).order_by('title')
    return render(request, 'media_app/series_list.html', {'series_list': series})

# def episode_detail(request, series_slug, season_number, episode_slug):
#     series = get_object_or_404(Series, slug=series_slug, is_published=True)
#     season = get_object_or_404(series.seasons, number=season_number)
#     episode = get_object_or_404(season.episodes, slug=episode_slug, is_published=True)
#     return render(request, 'media_app/episode_detail.html', {'episode': episode})


# Download handler (streams file)
def _stream_file_response(file_field, filename=None):
    # file_field is a FieldFile
    if not file_field:
        raise Http404("File not found")
    file_path = file_field.path
    if not os.path.exists(file_path):
        raise Http404("File not found")
    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=filename or os.path.basename(file_path))
    return response

from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import F
from .models import Movie

def movie_download(request, slug):
    movie = get_object_or_404(Movie, slug=slug, is_published=True)
    if not movie.video_file:
        raise Http404("No video file available")
    
    # Optionally restrict to logged-in users:
    # if not request.user.is_authenticated:
    #     return HttpResponseForbidden("Login required to download")

    movie.download_count = F('download_count') + 1
    movie.save(update_fields=['download_count'])
    movie.refresh_from_db(fields=['download_count'])
    
    return FileResponse(
        open(movie.video_file.path, 'rb'),
        as_attachment=True,
        filename=f"{movie.title}.mp4"
    )





from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import F
from .models import Episode

def episode_download(request, series_slug, season_number, episode_slug):
    # Get the episode
    episode = get_object_or_404(
        Episode,
        season__series__slug=series_slug,
        season__number=season_number,
        slug=episode_slug,
        is_published=True
    )

    # Increment download count using F expression
    episode.download_count = F('download_count') + 1
    episode.save(update_fields=['download_count'])
    episode.refresh_from_db(fields=['download_count'])

    # Serve the video file
    if not episode.video_file:
        raise Http404("No video file available")
    
    return FileResponse(
        open(episode.video_file.path, 'rb'),
        as_attachment=True,
        filename=f"{episode.season.series.title}-S{episode.season.number}E{episode.episode_number}-{episode.title}.mp4"
    )


# Optional staff-only uploader views (if you want to allow admin from site)

import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.conf import settings
from .forms import MovieForm
from .models import Movie, Genre

@user_passes_test(lambda u: u.is_staff)
def upload_movie(request):
    """
    Staff-only view: upload movie file + title.
    Automatically fetch TMDb info (description, poster, genres, trailer, rating, release_date)
    """
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            # Step 1: Save movie with minimal info (title + video_file)
            movie = form.save(commit=False)
            movie.uploaded_by = request.user
            movie.save()
            form.save_m2m()  # save any M2M (genres will be updated later from TMDb)

            # Step 2: Fetch TMDb info
            try:
                # TMDb search API
                search_url = f"https://api.themoviedb.org/3/search/movie?api_key={settings.TMDB_API_KEY}&query={movie.title}"
                response = requests.get(search_url, timeout=10)
                response.raise_for_status()
                results = response.json().get("results", [])

                if results:
                    tmdb_data = results[0]  # Take the first result

                    # Basic info
                    movie.tmdb_id = tmdb_data.get("id")
                    movie.description = tmdb_data.get("overview", "")
                    movie.release_date = tmdb_data.get("release_date") or None
                    movie.rating = tmdb_data.get("vote_average")

                    # Poster
                    poster_path = tmdb_data.get("poster_path")
                    if poster_path:
                        movie.poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                        # Download poster into ImageField
                        img = requests.get(movie.poster_url, stream=True, timeout=10)
                        if img.status_code == 200:
                            movie.poster.save(
                                f"{slugify(movie.title)}.jpg",
                                ContentFile(img.content),
                                save=False
                            )

                    # Genres
                    genre_ids = tmdb_data.get("genre_ids", [])
                    if genre_ids:
                        genre_list_url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={settings.TMDB_API_KEY}"
                        all_genres = requests.get(genre_list_url, timeout=10).json().get("genres", [])
                        for g_id in genre_ids:
                            for g in all_genres:
                                if g["id"] == g_id:
                                    genre_obj, _ = Genre.objects.get_or_create(name=g["name"])
                                    movie.genres.add(genre_obj)

                    # Trailer (YouTube key)
                    videos_url = f"https://api.themoviedb.org/3/movie/{movie.tmdb_id}/videos?api_key={settings.TMDB_API_KEY}"
                    videos = requests.get(videos_url, timeout=10).json().get("results", [])
                    for vid in videos:
                        if vid.get("site") == "YouTube" and vid.get("type") == "Trailer":
                            movie.trailer_key = vid.get("key")
                            break

                    movie.save()
                    messages.success(request, f"'{movie.title}' uploaded successfully with TMDb info!")
                else:
                    messages.warning(request, f"No TMDb info found for '{movie.title}'. Saved with minimal info.")

            except requests.RequestException as e:
                messages.warning(request, f"Movie saved but TMDb fetch failed: {e}")

            return redirect(movie.get_absolute_url())
    else:
        form = MovieForm()

    return render(request, "media_app/upload_movie.html", {"form": form})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse

from .models import Episode, Season
import requests
from django.core.files.base import ContentFile
import os
from datetime import timedelta

@user_passes_test(lambda u: u.is_staff)
def upload_episode(request):
    if request.method == 'POST':
        form = EpisodeForm(request.POST, request.FILES)
        if form.is_valid():
            ep = form.save(commit=False)
            
            # Fetch other episode details from external API
            season = ep.season
            series_title = season.series.title
            season_number = season.number
            episode_number = ep.episode_number

            api_url = f"https://example.com/api/series/{series_title}/season/{season_number}/episode/{episode_number}/"
            response = requests.get(api_url)
            if response.status_code == 200:
                data = response.json()
                ep.title = data.get('title')
                ep.description = data.get('description')
                ep.is_published = data.get('is_published', True)
                
                # Fetch poster
                poster_url = data.get('poster_url')
                if poster_url:
                    ep.poster = ContentFile(requests.get(poster_url).content, name=os.path.basename(poster_url))
                
                # Fetch trailer
                trailer_url = data.get('trailer_url')
                if trailer_url:
                    ep.trailer = ContentFile(requests.get(trailer_url).content, name=os.path.basename(trailer_url))
                
                # Set duration
                duration_seconds = data.get('duration_seconds')
                if duration_seconds:
                    ep.duration = timedelta(seconds=duration_seconds)
            else:
                form.add_error('episode_number', 'Episode not found in external API.')
                return render(request, 'media_app/upload_episode.html', {'form': form})

            ep.save()
            return redirect('media_app:episode_detail', series_slug=ep.season.series.slug, season_number=ep.season.number, episode_slug=ep.slug)
    else:
        form = EpisodeForm()

    return render(request, 'media_app/upload_episode.html', {'form': form})


# AJAX endpoint to fetch episode details without submitting
def fetch_episode_details(request):
    season_id = request.GET.get('season_id')
    episode_number = request.GET.get('episode_number')

    try:
        season = Season.objects.select_related('series').get(id=season_id)
        series_title = season.series.title
        season_number = season.number

        api_url = f"https://example.com/api/series/{series_title}/season/{season_number}/episode/{episode_number}/"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            return JsonResponse({
                'success': True,
                'title': data.get('title'),
                'description': data.get('description'),
                'poster_url': data.get('poster_url'),
                'trailer_url': data.get('trailer_url'),
                'duration_seconds': data.get('duration_seconds')
            })
        else:
            return JsonResponse({'success': False, 'message': 'Episode not found in API'})
    except Season.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Season not found'})



# views.py
from django.shortcuts import render
from django.db.models import Q, Count, F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import FieldError

from .models import Movie, Series, Genre

from django.shortcuts import render
from django.db.models import Q
from .models import Movie, Series

def search(request):
    query = request.GET.get('q', '').strip()
    genre = request.GET.get('genre', '').strip()
    year = request.GET.get('year', '').strip()
    country = request.GET.get('country', '').strip()
    sort_by = request.GET.get('sort', 'recent')

    # Start with base querysets
    movies = Movie.objects.filter(is_published=True)
    series = Series.objects.filter(is_published=True)

    # Text search (title or description)
    if query:
        movies = movies.filter(Q(title__icontains=query) | Q(description__icontains=query))
        series = series.filter(Q(title__icontains=query) | Q(description__icontains=query))

    # Filter by genre
    if genre:
        movies = movies.filter(genres__name__icontains=genre)
        series = series.filter(genres__name__icontains=genre)

    # Filter by release year
    if year:
        movies = movies.filter(release_date__year=year)
        series = series.filter(release_date__year=year)

    # Filter by country (if exists)
    if country:
        if 'country' in [f.name for f in Movie._meta.get_fields()]:
            movies = movies.filter(country__icontains=country)
        if 'country' in [f.name for f in Series._meta.get_fields()]:
            series = series.filter(country__icontains=country)

    # Sorting
    if sort_by == 'downloads':
        if 'download_count' in [f.name for f in Movie._meta.get_fields()]:
            movies = movies.order_by('-download_count')
        if 'download_count' in [f.name for f in Series._meta.get_fields()]:
            series = series.order_by('-download_count')
    else:
        movies = movies.order_by('-upload_date')
        series = series.order_by('-release_date')

    # Combine results
    results = list(movies) + list(series)

    context = {
        'query': query,
        'genre': genre,
        'year': year,
        'country': country,
        'sort_by': sort_by,
        'results': results,
    }
    return render(request, 'media_app/search_results.html', context)

# views.py

# views.py

import zipfile
import os
import shutil
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import yt_dlp
from datetime import datetime

def download_from_link(request):
    if "downloads_history" not in request.session:
        request.session["downloads_history"] = []

    if request.method == "POST":
        link = request.POST.get("link")
        download_type = request.POST.get("type")  # 'video' or 'audio'
        quality = request.POST.get("quality", "720")  # 320, 720, 1080

        if not link:
            return JsonResponse({"status": "error", "message": "Please provide a valid link."})

        # Create downloads folder
        output_dir = os.path.join(settings.MEDIA_ROOT, "downloads")
        os.makedirs(output_dir, exist_ok=True)

        ffmpeg_path = r"C:\Users\HP\Downloads\ffmpeg-8.0-essentials_build\ffmpeg-8.0-essentials_build\bin\ffmpeg.exe"

        progress_info = {"percent": 0, "status": "pending", "filename": "", "link": link, "type": download_type, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

        # Add to history
        downloads_history = request.session["downloads_history"]
        downloads_history.append(progress_info)
        request.session["downloads_history"] = downloads_history

        def progress_hook(d):
            if d["status"] == "downloading":
                downloaded = d.get("downloaded_bytes", 0)
                total = d.get("total_bytes") or d.get("total_bytes_estimate", 1)
                progress_info["percent"] = int(downloaded / total * 100)
            elif d["status"] == "finished":
                progress_info["percent"] = 100
                progress_info["status"] = "completed"

            request.session.modified = True

        ydl_opts = {
            "ffmpeg_location": ffmpeg_path,
            "progress_hooks": [progress_hook],
            "quiet": True,
            "merge_output_format": "mp4",
            "noplaylist": False,
            "outtmpl": os.path.join(output_dir, "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"),
        }

        if download_type == "audio":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "128"}],
            })
        else:
            ydl_opts["format"] = f"bestvideo[height<={quality}]+bestaudio/best/best"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)

            # Handle playlists
            if "entries" in info:
                playlist_title = info.get("title") or "playlist"
                folder_path = os.path.join(output_dir, playlist_title)
                zip_filename = f"{playlist_title}.zip"
                zip_path = os.path.join(output_dir, zip_filename)
                shutil.make_archive(base_name=zip_path.replace(".zip", ""), format="zip", root_dir=folder_path)
                progress_info["filename"] = zip_filename
                progress_info["status"] = "completed"
                filename_to_return = zip_filename
            else:
                filename = ydl.prepare_filename(info)
                progress_info["filename"] = os.path.basename(filename)
                filename_to_return = os.path.basename(filename)
                progress_info["status"] = "completed"

            request.session.modified = True

            return JsonResponse({"status": "success", "filename": filename_to_return, "is_playlist": "entries" in info})

        except Exception as e:
            progress_info["status"] = "retry"
            request.session.modified = True
            return JsonResponse({"status": "error", "message": f"Download Error: {str(e)}"})

    # GET request: show page and history
    downloads_history = request.session.get("downloads_history", [])
    return render(request, "media_app/download_video.html", {"MEDIA_URL": settings.MEDIA_URL, "downloads_history": downloads_history})

# New view to get progress
def download_progress(request):
    progress = request.session.get('download_progress', {"percent": 0})
    return JsonResponse(progress)


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from .models import Movie, Series, Episode, Review
from .forms import ReviewForm

def media_detail(request, media_type, slug, season_number=None, episode_slug=None):
    # Determine which object is being viewed
    if media_type == "movie":
        media_obj = get_object_or_404(Movie, slug=slug)
    elif media_type == "series":
        if episode_slug:
            media_obj = get_object_or_404(Episode, slug=episode_slug, season__number=season_number, season__series__slug=slug)
        else:
            media_obj = get_object_or_404(Series, slug=slug)
    else:
        return redirect('index')

    # Reviews
    content_type = ContentType.objects.get_for_model(media_obj)
    reviews = Review.objects.filter(content_type=content_type, object_id=media_obj.id)

    # Review submission
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.content_type = content_type
            review.object_id = media_obj.id
            if request.user.is_authenticated:
                review.user = request.user
                review.name = request.user.get_full_name() or request.user.username
                review.email = request.user.email
            review.save()
            return redirect(request.path)
    else:
        form = ReviewForm()
        # Hide name/email if user is logged in
        if request.user.is_authenticated:
            form.fields['name'].widget = forms.HiddenInput()
            form.fields['email'].widget = forms.HiddenInput()

    return render(request, 'media_app/media_detail.html', {
        'media': media_obj,
        'reviews': reviews,
        'form': form,
        'media_type': media_type,
    })

# music_app/views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import MusicUploadForm
from .models import Music
from django.contrib.auth.decorators import login_required
import mimetypes
import os
from django.conf import settings





from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import MusicUploadForm
from .models import Music, Album, Track


def upload_music(request):
    if request.method == 'POST':
        form = MusicUploadForm(request.POST, request.FILES)
        music_type = request.POST.get('music_type')

        if music_type in ['album', 'ep']:
            # Create Album/EP and its tracks
            title = request.POST.get('title')
            artist = request.POST.get('artist')
            poster = request.FILES.get('poster')

            album = Album.objects.create(
                title=title,
                artist=artist,
                music_type=music_type,
                uploaded_by=request.user,
                poster=poster
            )

            # Handle multiple track uploads
            track_files = request.FILES.getlist('tracks')
            for file in track_files:
                Track.objects.create(album=album, title=file.name.split('.')[0], file=file)

            return redirect('music_list')  # change to your view name
        else:
            # Single or Mixtape
            if form.is_valid():
                music = form.save(commit=False)
                music.uploaded_by = request.user
                music.save()
                return redirect('music_list')
    else:
        form = MusicUploadForm()

    return render(request, 'media_app/upload_music.html', {'form': form})


from django.shortcuts import render, get_object_or_404
from django.http import FileResponse
from .models import Music

def music_list(request):
    """Show all uploaded music."""
    music_files = Music.objects.all().order_by('-uploaded_at')
    return render(request, 'media_app/music_list.html', {'music_files': music_files})


def music_detail(request, slug):
    """Show a single music detail."""
    music = get_object_or_404(Music, slug=slug)
    return render(request, 'media_app/music_detail.html', {'music': music})


from django.http import FileResponse, Http404
from .models import Music, Track

def download_music(request, music_id):
    try:
        music = Music.objects.get(pk=music_id)
        music.download_count += 1  # increase counter
        music.save(update_fields=['download_count'])
        return FileResponse(open(music.file.path, 'rb'), as_attachment=True)
    except Music.DoesNotExist:
        raise Http404("Music not found")
