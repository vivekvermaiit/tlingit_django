from .models import CorpusEntry, Sentence, Line, LineTag
from .constants import TAG_PLACEHOLDER


def ingest_json(json_data, tag_data, existing_tlingit_lines=None, number=None):
    """
    json_data: full entry dict (None if text-only update)
    tag_data: {line_number: [(word, tag), ...]}
    existing_tlingit_lines: parsed tlingit lines for line count check (text-only mode)
    Returns (success, message)
    """
    lines_changed = 0
    if json_data is not None:
        # Full create or update
        number = json_data["number"]
        entry = CorpusEntry.objects.filter(number=number).first()

        if entry:
            # Validate line count
            all_new_lines = [
                line
                for sentence in json_data["sentences"]
                for line in sentence["lines"]
            ]
            existing_line_count = Line.objects.filter(
                sentence__corpus_entry=entry
            ).count()
            if len(all_new_lines) != existing_line_count:
                return False, (
                    f"Line count mismatch: file has {len(all_new_lines)} lines "
                    f"but DB has {existing_line_count} lines. Aborting."
                )

            # Update entry metadata only if changed
            changed = False
            for field in ["title", "author", "clan", "source", "transcriber",
                          "translator", "orthography", "dialect"]:
                if getattr(entry, field) != json_data.get(field, ""):
                    setattr(entry, field, json_data.get(field, ""))
                    changed = True
            if changed:
                entry.save()

            # Update sentences and lines only if changed
            for sentence_data in json_data["sentences"]:
                sentence = Sentence.objects.filter(
                    corpus_entry=entry,
                    sentence_number=sentence_data["sentence_number"]
                ).first()
                if sentence:
                    sentence_changed = False
                    if sentence.sentence_tlingit != sentence_data["sentence_tlingit"]:
                        sentence.sentence_tlingit = sentence_data["sentence_tlingit"]
                        sentence_changed = True
                    if sentence.sentence_english != sentence_data["sentence_english"]:
                        sentence.sentence_english = sentence_data["sentence_english"]
                        sentence_changed = True
                    if sentence_changed:
                        sentence.save()

                    for line_data in sentence_data["lines"]:
                        line = Line.objects.filter(
                            sentence=sentence,
                            line_number=line_data["line_number"]
                        ).first()
                        if line:
                            line_changed = False
                            for field in ["line_tlingit", "line_english", "page_tlingit", "page_english"]:
                                if getattr(line, field) != line_data[field]:
                                    setattr(line, field, line_data[field])
                                    line_changed = True
                            if line_changed:
                                lines_changed += 1
                                line.save()

        else:
            # Create new entry
            entry = CorpusEntry.objects.create(
                number=json_data["number"],
                title=json_data.get("title", ""),
                author=json_data.get("author", ""),
                clan=json_data.get("clan", ""),
                source=json_data.get("source", ""),
                transcriber=json_data.get("transcriber", ""),
                translator=json_data.get("translator", ""),
                orthography=json_data.get("orthography", ""),
                dialect=json_data.get("dialect", ""),
            )
            for sentence_data in json_data["sentences"]:
                sentence = Sentence.objects.create(
                    corpus_entry=entry,
                    sentence_number=sentence_data["sentence_number"],
                    sentence_tlingit=sentence_data["sentence_tlingit"],
                    sentence_english=sentence_data["sentence_english"],
                )
                for line_data in sentence_data["lines"]:
                    Line.objects.create(
                        sentence=sentence,
                        line_number=line_data["line_number"],
                        line_tlingit=line_data["line_tlingit"],
                        line_english=line_data["line_english"],
                        page_tlingit=line_data["page_tlingit"],
                        page_english=line_data["page_english"],
                    )

    else:
        # Text-only update — entry must exist
        if not number:
            return False, "Could not determine entry number from file."
        entry = CorpusEntry.objects.filter(number=number).first()

        if not entry:
            return False, f"Entry {number} does not exist. Provide both files to create a new entry."

        # Validate line count
        existing_line_count = Line.objects.filter(sentence__corpus_entry=entry).count()
        if len(existing_tlingit_lines) != existing_line_count:
            return False, (
                f"Line count mismatch: file has {len(existing_tlingit_lines)} lines "
                f"but DB has {existing_line_count} lines. Aborting."
            )

    tags_updated = 0
    for line_number, pairs in tag_data.items():
        line = Line.objects.filter(
            sentence__corpus_entry=entry,
            line_number=line_number
        ).first()
        if line:
            tag_string = " ".join(tag for _, tag in pairs)
            existing_tag = LineTag.objects.filter(line=line).first()
            if existing_tag is None:
                LineTag.objects.create(line=line, tag_tlingit=tag_string)
                tags_updated += 1
            elif existing_tag.tag_tlingit != tag_string:
                existing_tag.tag_tlingit = tag_string
                existing_tag.save()
                tags_updated += 1

    return True, (
        f"Successfully ingested entry {entry.number}. "
        f"Lines changed: {lines_changed}, "
        f"tags updated: {tags_updated}."
    )
