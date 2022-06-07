import unicodedata

from django.core.exceptions import ValidationError


def form_valid_or_raise(form):
    if not form.is_valid():
        raise ValidationError(form.errors.as_data())


def encode_content_disposition_filename(filename):
    ascii_filename = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    parts = [f'filename="{ascii_filename}"']
    if ascii_filename != filename:
        from django.utils.http import urlquote
        quoted_filename = urlquote(filename)
        parts.append(f'filename*=UTF-8\'\'{quoted_filename}')
    return '; '.join(parts)
