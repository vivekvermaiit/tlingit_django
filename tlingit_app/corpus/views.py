from django.shortcuts import render, get_object_or_404
from .models import CorpusEntry

def corpus_entry_detail(request, number):
    corpus_entry = CorpusEntry.objects.filter(number=number).first()
    return render(request, "corpus_entry_detail.html", {
        "corpus_entry": corpus_entry,
    })
