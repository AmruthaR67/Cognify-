import os
import uuid
import pyttsx3

from django.conf import settings


def create_audio(text):
    """
    Convert text into an MP3/WAV audio file locally.
    No API credits required.
    """

    if not text:
        raise ValueError("No text was provided for audio generation.")

    audio_dir = os.path.join(
        settings.MEDIA_ROOT,
        "cognify_audio"
    )

    os.makedirs(
        audio_dir,
        exist_ok=True
    )

    filename = f"{uuid.uuid4()}.wav"

    filepath = os.path.join(
        audio_dir,
        filename
    )

    engine = pyttsx3.init()

    engine.setProperty(
        "rate",
        165
    )

    engine.setProperty(
        "volume",
        1.0
    )

    engine.save_to_file(
        text,
        filepath
    )

    engine.runAndWait()

    engine.stop()

    if not os.path.exists(filepath):
        raise RuntimeError(
            "Audio file was not created."
        )

    return f"cognify_audio/{filename}"