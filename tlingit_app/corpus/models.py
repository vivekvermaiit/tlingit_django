from django.db import models


class CorpusEntry(models.Model):
    number = models.CharField(max_length=255, null=False)
    title = models.CharField(max_length=255, null=False)
    author = models.CharField(max_length=255, blank=True, null=True)
    clan = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    transcriber = models.CharField(max_length=255, blank=True, null=True)
    translator = models.CharField(max_length=255, blank=True, null=True)
    orthography = models.CharField(max_length=255, blank=True, null=True)
    dialect = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Sentence(models.Model):
    sentence_number = models.IntegerField(null=False)
    sentence_tlingit = models.TextField(null=False)
    sentence_english = models.TextField(null=False)
    corpus_entry = models.ForeignKey(CorpusEntry, on_delete=models.CASCADE, related_name='sentences')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['sentence_tlingit']),
            models.Index(fields=['sentence_english']),
        ]


class Line(models.Model):
    line_number = models.IntegerField(null=False)
    line_tlingit = models.TextField(null=False)
    line_english = models.TextField(null=False)
    page_tlingit = models.CharField(max_length=255, null=False)
    page_english = models.CharField(max_length=255, null=False)
    sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE, related_name='lines')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['line_tlingit']),
            models.Index(fields=['line_english']),
        ]
