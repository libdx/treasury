"""project URL Configuration
"""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("api/", include("project.apps.api.urls")),
    path("admin/", admin.site.urls),
]
