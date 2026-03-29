from django.urls import path
from . import views

urlpatterns = [
    path("entries/ingest/", views.ingest_entry, name="ingest_entry"), #needs to be above entries/number to avoid conflict
    path("entries/<str:number>/", views.corpus_entry_detail, name="corpus_entry_detail"),
    path('sentences/<int:id>/', views.sentence_detail, name='sentence_detail'),
    path("lines/", views.lines_view, name="lines"),
    path("api/lines/<int:line_id>/tags/", views.update_line_tags, name="update_line_tags"),
    path("export_tags/", views.export_tags, name="export_tags"),
    path("import_tags/", views.import_tags, name="import_tags"),
]
