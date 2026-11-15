from django.urls import path
from . views import (about_us, contact_us, dashboard_view, download_from_link, download_music, download_progress, faq_page, index,episode_detail, episode_download, movie_detail, movie_download,
                     movie_list, music_detail, music_list, privacy_policy, season_detail, series_detail, series_list, signin_view, signup_view, terms, terms_conditions, 
                     upload_episode, upload_movie,search, upload_music, )
from . import api_views
from django.contrib.auth import views as auth_views
from media_app import views
app_name = 'media_app'
urlpatterns = [
    
    path('', index, name='index'),
    path('signup/', signup_view, name='signup'),
    path('signin/', signin_view, name='signin'),
    path('signout/', auth_views.LogoutView.as_view(next_page='media_app:signin'), name='signout'),
    path("privacy-policy/", privacy_policy, name="privacy_policy"),
    path("terms-and-conditions/", terms_conditions, name="terms_conditions"),
    path("faq/", faq_page, name="faq_page"),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('movies/', movie_list, name='movie_list'),
    path('terms/', terms, name='terms'),
    path('about_us/', about_us, name='about_us'),
    path('contact_us/', contact_us, name='contact_us'),
    path('movie/<slug:slug>/', movie_detail, name='movie_detail'),
    path('movie/<slug:slug>/download/', movie_download, name='movie_download'),

    path('series/', series_list, name='series_list'),
   
    path('series/<slug:series_slug>/season/<int:season_number>/', season_detail, name='season_detail'),
    path('series/<slug:series_slug>/season/<int:season_number>/episode/<slug:episode_slug>/', episode_detail, name='episode_detail'),
    path('series/<slug:series_slug>/season/<int:season_number>/episode/<slug:episode_slug>/download/', episode_download, name='episode_download'),
    path('series/<slug:series_slug>/', series_detail, name='series_detail'),
    path('series/<slug:series_slug>/', series_list, name='series_list'),
    

    # optional staff uploader URLs
    path('upload/movie/', upload_movie, name='upload_movie'),
    path('upload/episode/', upload_episode, name='upload_episode'),
    
    # path("download-link/", download_from_link, name="download_from_link"),
    path("download-progress/", download_progress, name="download_progress"),
    path('download-link/', download_from_link, name='download_from_link'),
    path('search/', search, name='search'),
    
    # music download
    path('upload/', upload_music, name='upload_music'),
    path('list/', music_list, name='music_list'),
    path('music/<slug:slug>/', music_detail, name='music_detail'),

    path('download/<int:music_id>/', download_music, name='download_music'),
    
    # api
    path('api/series/', api_views.SeriesListAPIView.as_view(), name='api_series_list'),
    path('api/series/<slug:slug>/', api_views.SeriesDetailAPIView.as_view(), name='api_series_detail'),
]
