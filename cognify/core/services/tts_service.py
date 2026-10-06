import os
import win32com.client


def generate_audio(text, output_path):
    """
    Generate a WAV audio file using Windows SAPI.
    """

    directory = os.path.dirname(output_path)

    if directory:
        os.makedirs(directory, exist_ok=True)

    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    stream = win32com.client.Dispatch("SAPI.SpFileStream")

    # 3 = create a new file for writing
    stream.Open(output_path, 3, False)

    speaker.AudioOutputStream = stream

    speaker.Speak(text)

    stream.Close()

    return output_path