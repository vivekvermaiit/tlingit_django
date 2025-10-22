import json
import os
from django.core.management.base import BaseCommand
from corpus.models import CorpusEntry, Sentence, Line
from django.conf import settings

class Command(BaseCommand):
    help = "Seed the database with corpus entries from JSON files"

    def handle(self, *args, **options):
        # Path to the json_entries folder
        json_dir = os.path.join(settings.BASE_DIR, "json_entries")
        if not os.path.exists(json_dir):
            self.stderr.write(self.style.ERROR(f"Directory not found: {json_dir}"))
            return

        json_files = sorted([f for f in os.listdir(json_dir) if f.endswith(".json")])
        self.stdout.write(f"Seeding {len(json_files)} corpus entries from {json_dir}...")

        for filename in json_files:
            file_path = os.path.join(json_dir, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Create the CorpusEntry
                corpus_entry = CorpusEntry.objects.create(
                    number=data.get("number"),
                    title=data.get("title"),
                    author=data.get("author"),
                    clan=data.get("clan"),
                    source=data.get("source"),
                    transcriber=data.get("transcriber"),
                    translator=data.get("translator"),
                    orthography=data.get("orthography"),
                    dialect=data.get("dialect"),
                )

                # Create nested sentences and lines
                for s in data.get("sentences", []):
                    sentence = Sentence.objects.create(
                        sentence_number=s.get("sentence_number"),
                        sentence_tlingit=s.get("sentence_tlingit"),
                        sentence_english=s.get("sentence_english"),
                        corpus_entry=corpus_entry,
                    )

                    for l in s.get("lines", []):
                        Line.objects.create(
                            line_number=l.get("line_number"),
                            line_tlingit=l.get("line_tlingit"),
                            line_english=l.get("line_english"),
                            page_tlingit=l.get("page_tlingit"),
                            page_english=l.get("page_english"),
                            sentence=sentence,
                        )

                self.stdout.write(self.style.SUCCESS(f"Seeded: {filename}"))

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Failed to seed {filename}: {e}"))

        self.stdout.write(self.style.SUCCESS("Done seeding corpus entries."))
