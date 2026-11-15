"""WSGI entry point for Vercel deployment."""
import os
import sys

from django.core.wsgi import get_wsgi_application

# Make the project root importable (Vercel runs from /vercel/path0)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_project.settings')

application = get_wsgi_application()
# Vercel's Python builder looks for a module-level `app`
app = application
