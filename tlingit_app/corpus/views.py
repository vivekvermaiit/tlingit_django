from django.shortcuts import render, get_object_or_404
from .models import CorpusEntry
from .models import Sentence

# import logging
# logger = logging.getLogger('corpus')
# logger.debug("DEBUG TEST from view")
# logger.warning("WARNING TEST from view")


def corpus_entry_detail(request, number):
    corpus_entry = CorpusEntry.objects.filter(number=number).first()
    return render(request, "corpus/corpus_entry_detail.html", {
        "corpus_entry": corpus_entry,
    })


# views.py
def sentence_detail(request, id):
    # show_context -> show previous and next sentences
    # page_tlingit -> current Tlingit page
    # page_english -> current English page
    # line_number -> line number as seen in the tlingit corpus github
    # scope -> either both, tlingit, or english (for highlighting)
    # keyword_text -> text to highlight
    sentence = get_object_or_404(Sentence.objects.select_related('corpus_entry'), pk=id)
    corpus_entry = sentence.corpus_entry

    keyword_text = request.GET.get("keyword_text") or ""
    keyword_regex = request.GET.get("keyword_regex") or ""
    show_context = request.GET.get("show_context") is not None
    page_tlingit = request.GET.get("page_tlingit")
    page_english = request.GET.get("page_english")
    line_number = request.GET.get("line_number") or ""
    scope = request.GET.get("scope")

    prev_sentence = next_sentence = None
    if show_context:
        prev_sentence = (
            Sentence.objects
            .filter(corpus_entry_id=corpus_entry.id, sentence_number__lt=sentence.sentence_number)
            .order_by("-sentence_number")
            .first()
        )
        next_sentence = (
            Sentence.objects
            .filter(corpus_entry_id=corpus_entry.id, sentence_number__gt=sentence.sentence_number)
            .order_by("sentence_number")
            .first()
        )

    context = {
        "sentence": sentence,
        "corpus_entry": corpus_entry,
        "keyword_text": keyword_text,
        "keyword_regex": keyword_regex,
        "show_context": show_context,
        "page_tlingit": page_tlingit,
        "page_english": page_english,
        "line_number": line_number,
        "scope": scope,
        "prev_sentence": prev_sentence,
        "next_sentence": next_sentence,
        "combo": f"{keyword_text},{keyword_regex}"
    }
    return render(request, "corpus/sentence_detail.html", context)
