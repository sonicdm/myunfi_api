import mimetypes


def guess_mime_type(content):
    """
    Guess the mime type of the content based on the HTTP header
    binary
    text
    json
    blob

    """
    if content is None:
        return None
    return mimetypes.guess_type(content)[0]
