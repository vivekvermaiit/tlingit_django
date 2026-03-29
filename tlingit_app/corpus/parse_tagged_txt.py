import re
from .constants import TAG_PLACEHOLDER


def parse_metadata(lines, metadata=None):
    if metadata is None:
        metadata = {}
    for line in lines:
        line = line.strip()
        if not line.startswith("{"):
            continue
        line_clean = line.strip("{}")
        if "=" in line_clean:
            key, _, value = line_clean.partition("=")
            metadata[key.strip().lower()] = value.strip()
    return metadata


def parse_lines_with_pages(lines):
    current_page = None
    content = []
    for line in lines:
        line = line.strip()
        page_match = re.match(r"\{Page\s*=\s*(\S+)\}", line)
        if page_match:
            current_page = page_match.group(1)
            continue
        line_match = re.match(r"^(\d+)\t(.+)$", line)
        if line_match:
            line_number = int(line_match.group(1))
            text = line_match.group(2).strip()
            content.append({
                "page": current_page,
                "line_number": line_number,
                "text": text
            })
    return content


def parse_word_tag_pairs(text):
    """
    Parse a tagged line into (word, tag) pairs.
    e.g. "Ha|INTJ wé|DET x̱ʼeewóosʼ|VERB," -> [("Ha", "INTJ"), ("wé", "DET"), ("x̱ʼeewóosʼ,", "VERB")]
    Untagged tokens get TAG_PLACEHOLDER.
    Punctuation after tag belongs to word, not tag.
    """
    tokens = text.split()
    pairs = []
    for token in tokens:
        if "|" in token:
            # Split on first | only
            word_part, tag_part = token.split("|", 1)
            # Any trailing punctuation after the tag belongs to the word
            tag_match = re.match(r"([A-Z_?]+)(.*)", tag_part)
            if tag_match:
                tag = tag_match.group(1)
                trailing = tag_match.group(2)
                word = word_part + trailing
            else:
                tag = tag_part
                word = word_part
            pairs.append((word, tag))
        else:
            pairs.append((token, TAG_PLACEHOLDER))
    return pairs


def is_tagged_line(text):
    """Check if a line contains any tagged tokens."""
    return bool(re.search(r"\w\|[A-Z_]+", text))


def strip_tags_from_text(text):
    """Remove tags from text, keeping words and punctuation."""
    tokens = text.split()
    words = []
    for token in tokens:
        if "|" in token:
            word_part, tag_part = token.split("|", 1)
            tag_match = re.match(r"([A-Z_?]+)(.*)", tag_part)
            trailing = tag_match.group(2) if tag_match else ""
            words.append(word_part + trailing)
        else:
            words.append(token)
    return " ".join(words)


def group_into_sentences(lines):
    """Group lines into sentences based on sentence-ending punctuation."""
    sentence_boundaries = [
        i for i, line in enumerate(lines)
        if re.search(r"[a-záéíóúýÿʼ][.?!]$", line["line_tlingit"])
    ]

    sentences = []
    start_idx = 0
    sentence_number = 1

    for end_idx in sentence_boundaries:
        sentence_lines = lines[start_idx:end_idx + 1]
        sentences.append({
            "sentence_number": sentence_number,
            "sentence_tlingit": " ".join(l["line_tlingit"] for l in sentence_lines).strip(),
            "sentence_english": " ".join(l["line_english"] for l in sentence_lines).strip(),
            "lines": sentence_lines
        })
        sentence_number += 1
        start_idx = end_idx + 1

    # Fallback for dangling lines
    if start_idx < len(lines):
        sentence_lines = lines[start_idx:]
        sentences.append({
            "sentence_number": sentence_number,
            "sentence_tlingit": " ".join(l["line_tlingit"] for l in sentence_lines).strip(),
            "sentence_english": " ".join(l["line_english"] for l in sentence_lines).strip(),
            "lines": sentence_lines
        })

    return sentences


def parse_txt_to_json(tlingit_lines_raw, english_lines_raw=None):
    """
    Parse tlingit text file (and optionally english translation file)
    into the JSON structure used for ingestion.
    Returns (json_data, tag_data) where tag_data is {line_number: [(word, tag), ...]}
    """
    metadata = parse_metadata(tlingit_lines_raw)
    if english_lines_raw:
        metadata = parse_metadata(english_lines_raw, metadata)

    tlingit_parsed = parse_lines_with_pages(tlingit_lines_raw)
    tag_data = {}  # line_number -> list of (word, tag) pairs

    # Build clean tlingit lines and extract tags
    tlingit_clean = []
    for item in tlingit_parsed:
        if is_tagged_line(item["text"]):
            pairs = parse_word_tag_pairs(item["text"])
            tag_data[item["line_number"]] = pairs
            clean_text = strip_tags_from_text(item["text"])
        else:
            clean_text = item["text"]
        tlingit_clean.append({
            "page": item["page"],
            "line_number": item["line_number"],
            "text": clean_text
        })

    if english_lines_raw:
        english_parsed = parse_lines_with_pages(english_lines_raw)
        tlingit_by_ln = {l["line_number"]: l for l in tlingit_clean}
        english_by_ln = {l["line_number"]: l for l in english_parsed}
        common_lns = sorted(set(tlingit_by_ln.keys()) & set(english_by_ln.keys()))

        aligned_lines = [
            {
                "line_number": ln,
                "line_tlingit": tlingit_by_ln[ln]["text"],
                "line_english": english_by_ln[ln]["text"],
                "page_tlingit": tlingit_by_ln[ln]["page"],
                "page_english": english_by_ln[ln]["page"],
            }
            for ln in common_lns
        ]

        sentences = group_into_sentences(aligned_lines)
        number = metadata.get("number", "")

        json_data = {
            "number": number,
            "title": metadata.get("title", ""),
            "author": metadata.get("author", ""),
            "clan": metadata.get("clan", ""),
            "source": metadata.get("source", ""),
            "transcriber": metadata.get("transcriber", ""),
            "translator": metadata.get("translator", ""),
            "orthography": metadata.get("orthography", ""),
            "dialect": metadata.get("dialect", ""),
            "sentences": sentences
        }
    else:
        json_data = None  # text-only update, no structure rebuild

    return json_data, tag_data, tlingit_clean
