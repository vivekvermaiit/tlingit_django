import re
from django import template
from django.utils.safestring import mark_safe
import logging


register = template.Library()

logger = logging.getLogger(__name__)


@register.filter
def highlight_text(text, args):
    """
    Usage:
      {{ text|highlight_text:"keyword_text,keyword_regex" }}
    """
    keyword_text = None
    keyword_regex = None

    if args:
        parts = args.split(",", 1)
        keyword_text = parts[0] if parts[0] else None
        if len(parts) > 1:
            keyword_regex = parts[1] if parts[1] else None

    css_class = 'keyword-highlight'

    if not (keyword_text or keyword_regex):
        return text

    regex = None
    if keyword_regex:
        try:
            regex = re.compile(f"({keyword_regex})", re.IGNORECASE)
        except re.error:
            if keyword_text:
                regex = re.compile(re.escape(keyword_text), re.IGNORECASE)
    elif keyword_text:
        regex = re.compile(f"({re.escape(keyword_text)})", re.IGNORECASE)

    if not regex:
        return text

    highlighted = regex.sub(f"<span class='{css_class}'>\\1</span>", text)
    return mark_safe(highlighted)
