from django.urls import path
from . import views

urlpatterns = [
    path("entries/<str:number>/", views.corpus_entry_detail, name="corpus_entry_detail"),
]
