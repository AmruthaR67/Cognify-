import os
import win32com.client


def generate_wav_audio(text, output_path):

    if text is None:
        raise ValueError("Audio text is None.")

    text = str(text).strip()

    if not text:
        raise ValueError("Audio text is empty.")

    print("======================================")
    print("SAPI AUDIO GENERATION")
    print("TEXT TYPE:", type(text).__name__)
    print("TEXT LENGTH:", len(text))
    print("OUTPUT PATH:", output_path)
    print("======================================")

    output_directory = os.path.dirname(output_path)

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )

    speaker = win32com.client.Dispatch(
        "SAPI.SpVoice"
    )

    stream = win32com.client.Dispatch(
        "SAPI.SpFileStream"
    )

    try:

        stream.Open(
            output_path,
            3,
            False
        )

        speaker.AudioOutputStream = stream

        print("SAPI SPEAKING...")

        speaker.Speak(text)

        print("SAPI SPEAKING FINISHED")

    finally:

        try:
            speaker.AudioOutputStream = None
        except Exception:
            pass

        try:
            stream.Close()
        except Exception:
            pass

    if not os.path.exists(output_path):
        raise RuntimeError(
            "SAPI did not create the WAV file."
        )

    file_size = os.path.getsize(output_path)

    if file_size == 0:
        raise RuntimeError(
            "SAPI created an empty WAV file."
        )

    print("WAV CREATED:", output_path)
    print("WAV SIZE:", file_size, "bytes")

    return output_path