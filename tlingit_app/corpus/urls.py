from django.urls import path
from . import views

urlpatterns = [
    path("entries/<str:number>/", views.corpus_entry_detail, name="corpus_entry_detail"),
    path('sentences/<int:id>/', views.sentence_detail, name='sentence_detail'),
    path("lines/", views.lines_view, name="lines"),
    path("api/lines/<int:line_id>/tags/", views.update_line_tags, name="update_line_tags"),

]
