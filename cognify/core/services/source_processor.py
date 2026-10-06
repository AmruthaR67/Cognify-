import io
import ipaddress
import socket

import requests
import json
import re

from bs4 import BeautifulSoup
from pypdf import PdfReader

from urllib.parse import (
    urlparse,
    urljoin,
    parse_qs,
)

from youtube_transcript_api import (
    YouTubeTranscriptApi,
)


MAX_CONTENT_SIZE = 10 * 1024 * 1024
REQUEST_TIMEOUT = 20

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0 Safari/537.36"
)


class SourceProcessingError(Exception):
    pass


def validate_url(url):

    if not url:
        raise SourceProcessingError(
            "Please enter a URL."
        )

    url = url.strip()

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise SourceProcessingError(
            "Only HTTP and HTTPS URLs are supported."
        )

    if not parsed.hostname:
        raise SourceProcessingError(
            "Please enter a valid URL."
        )

    if parsed.username or parsed.password:
        raise SourceProcessingError(
            "URLs containing login credentials are not allowed."
        )

    hostname = parsed.hostname.lower()

    if hostname in (
        "localhost",
        "localhost.localdomain",
    ):
        raise SourceProcessingError(
            "Local URLs are not allowed."
        )

    try:

        addresses = socket.getaddrinfo(
            hostname,
            None
        )

        checked_ips = set()

        for address in addresses:

            ip_string = address[4][0]

            if ip_string in checked_ips:
                continue

            checked_ips.add(ip_string)

            ip = ipaddress.ip_address(
                ip_string
            )

            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_reserved
                or ip.is_multicast
            ):
                raise SourceProcessingError(
                    "Private or local URLs are not allowed."
                )

    except socket.gaierror:

        raise SourceProcessingError(
            "Unable to find this website. "
            "Please check the URL."
        )

    return url


def detect_source_type(
    url,
    content_type=""
):

    url_lower = url.lower()
    content_type = content_type.lower()

    # YouTube
    if (
        "youtube.com" in url_lower
        or "youtu.be" in url_lower
    ):
        return "youtube"

    # Instagram / Facebook
    if (
        "instagram.com" in url_lower
        or "facebook.com" in url_lower
    ):
        return "social"

    # PDF
    if (
        "application/pdf" in content_type
        or url_lower.endswith(".pdf")
    ):
        return "pdf"

    # Google Docs / Drive
    if (
        "docs.google.com" in url_lower
        or "drive.google.com" in url_lower
    ):
        return "document"

    # HTML
    if (
        "text/html" in content_type
        or not content_type
    ):
        return "web"

    return "other"


def clean_html(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    for tag in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "footer",
        "header",
        "aside",
        "form",
        "iframe",
        "svg",
    ]):

        tag.decompose()

    title = ""

    if soup.title:

        title = soup.title.get_text(
            " ",
            strip=True
        )

    description = ""

    description_tag = soup.find(
        "meta",
        attrs={
            "name": "description"
        }
    )

    if description_tag:

        description = (
            description_tag.get(
                "content",
                ""
            )
            .strip()
        )

    if not title:

        og_title = soup.find(
            "meta",
            property="og:title"
        )

        if og_title:

            title = og_title.get(
                "content",
                ""
            ).strip()

    if not description:

        og_description = soup.find(
            "meta",
            property="og:description"
        )

        if og_description:

            description = og_description.get(
                "content",
                ""
            ).strip()

    main_content = (
        soup.find("article")
        or soup.find("main")
        or soup.body
        or soup
    )

    text = main_content.get_text(
        "\n",
        strip=True
    )

    lines = []

    for line in text.splitlines():

        line = " ".join(
            line.split()
        )

        if line:

            lines.append(line)

    text = "\n".join(lines)

    return {
        "title": title,
        "description": description,
        "text": text,
    }


def extract_pdf_text(content):

    try:

        reader = PdfReader(
            io.BytesIO(content)
        )

        pages = []

        for page in reader.pages:

            try:

                page_text = page.extract_text()

                if page_text:

                    pages.append(
                        page_text.strip()
                    )

            except Exception:

                continue

        return "\n\n".join(
            pages
        ).strip()

    except Exception as error:

        raise SourceProcessingError(
            f"Unable to read this PDF: {error}"
        )


def extract_youtube_video_id(url):

    parsed = urlparse(url)

    hostname = (
        parsed.hostname or ""
    ).lower()

    # youtu.be/VIDEO_ID
    if hostname == "youtu.be":

        video_id = (
            parsed.path
            .strip("/")
            .split("/")[0]
        )

        return video_id or None

    # youtube.com
    if (
        "youtube.com" in hostname
        or "youtube-nocookie.com" in hostname
    ):

        # /watch?v=VIDEO_ID
        if parsed.path == "/watch":

            return (
                parse_qs(
                    parsed.query
                )
                .get(
                    "v",
                    [None]
                )[0]
            )

        # /shorts/VIDEO_ID
        if parsed.path.startswith(
            "/shorts/"
        ):

            return (
                parsed.path
                .split("/shorts/")[1]
                .split("/")[0]
            )

        # /embed/VIDEO_ID
        if parsed.path.startswith(
            "/embed/"
        ):

            return (
                parsed.path
                .split("/embed/")[1]
                .split("/")[0]
            )

    return None


def get_youtube_metadata(url):

    try:

        response = requests.get(
            "https://www.youtube.com/oembed",
            params={
                "url": url,
                "format": "json",
            },
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": USER_AGENT
            },
        )

        if response.status_code == 200:

            data = response.json()

            return {
                "title": data.get(
                    "title",
                    ""
                ),
                "author": data.get(
                    "author_name",
                    ""
                ),
                "thumbnail": data.get(
                    "thumbnail_url",
                    ""
                ),
            }

    except Exception:

        pass

    return {
        "title": "YouTube Video",
        "author": "",
        "thumbnail": "",
    }

def process_youtube(url):
    metadata = get_youtube_metadata(url)
    video_id = extract_youtube_video_id(url)

    if not video_id:
        return {
            "source_url": url,
            "source_type": "youtube",
            "title": "YouTube Video",
            "author": "",
            "description": "",
            "thumbnail": "",
            "text": "",
            "transcript": "",
            "metadata": {},
            "chapters": [],
            "access_status": "failed",
            "access_message": "Could not extract the YouTube video ID.",
        }

    transcript_text = ""
    transcript_language = ""
    transcript_generated = False
    transcript_errors = []

    try:
        api = YouTubeTranscriptApi()

        # Get every transcript YouTube exposes for this video.
        transcript_list = api.list(video_id)

        available_transcripts = list(transcript_list)

        print(
            f"YouTube transcripts found for {video_id}: "
            f"{len(available_transcripts)}"
        )

        for transcript in available_transcripts:
            print(
                " -",
                transcript.language_code,
                "|",
                transcript.language,
                "| generated:",
                transcript.is_generated,
            )

        if not available_transcripts:
            transcript_errors.append(
                "YouTube returned no available caption tracks."
            )

        # Preferred languages.
        preferred_languages = [
            "en",
            "en-US",
            "en-GB",
            "hi",
            "ta",
            "te",
            "kn",
            "ml",
        ]

        def transcript_sort_key(transcript):
            try:
                language_rank = preferred_languages.index(
                    transcript.language_code
                )
            except ValueError:
                language_rank = len(preferred_languages)

            # Manual captions before auto-generated captions
            # when language is otherwise equal.
            generated_rank = 1 if transcript.is_generated else 0

            return language_rank, generated_rank

        candidates = sorted(
            available_transcripts,
            key=transcript_sort_key
        )

        # Try each available transcript until one actually fetches.
        for transcript in candidates:

            try:
                print(
                    "Trying YouTube transcript:",
                    transcript.language_code,
                    transcript.language,
                    "generated=",
                    transcript.is_generated,
                )

                fetched_transcript = transcript.fetch()

                parts = []

                for snippet in fetched_transcript:
                    snippet_text = getattr(
                        snippet,
                        "text",
                        ""
                    )

                    if snippet_text:
                        parts.append(
                            str(snippet_text).strip()
                        )

                candidate_text = " ".join(parts).strip()

                if candidate_text:

                    transcript_text = candidate_text
                    transcript_language = (
                        transcript.language_code
                    )
                    transcript_generated = (
                        transcript.is_generated
                    )

                    print(
                        "YouTube transcript SUCCESS:",
                        transcript_language,
                        "characters:",
                        len(transcript_text),
                    )

                    break

            except Exception as error:

                error_message = (
                    f"{type(error).__name__}: {error}"
                )

                print(
                    "YouTube transcript fetch failed:",
                    error_message
                )

                transcript_errors.append(
                    error_message
                )

    except Exception as error:

        error_message = (
            f"{type(error).__name__}: {error}"
        )

        print(
            "YouTube transcript list failed:",
            error_message
        )

        transcript_errors.append(
            error_message
        )

    # ---------------------------------------------------------
    # SUCCESS
    # ---------------------------------------------------------

    if transcript_text:

        return {
            "source_url": url,
            "source_type": "youtube",

            "title": metadata.get(
                "title",
                "YouTube Video"
            ),

            "author": metadata.get(
                "author",
                ""
            ),

            "description": "",

            "thumbnail": metadata.get(
                "thumbnail",
                ""
            ),

            # IMPORTANT:
            # Both fields receive the transcript.
            "text": transcript_text,
            "transcript": transcript_text,

            "metadata": {
                "platform": "YouTube",
                "video_id": video_id,
                "transcript_language": transcript_language,
                "transcript_generated": transcript_generated,
            },

            "chapters": [],

            "access_status": "success",

            "access_message": (
                "YouTube transcript retrieved successfully."
            ),
        }

    # ---------------------------------------------------------
    # PARTIAL
    # ---------------------------------------------------------

    error_details = ""

    if transcript_errors:
        error_details = (
            " Diagnostic details: "
            + " | ".join(transcript_errors[:3])
        )

    return {
        "source_url": url,
        "source_type": "youtube",

        "title": metadata.get(
            "title",
            "YouTube Video"
        ),

        "author": metadata.get(
            "author",
            ""
        ),

        "description": "",

        "thumbnail": metadata.get(
            "thumbnail",
            ""
        ),

        "text": "",
        "transcript": "",

        "metadata": {
            "platform": "YouTube",
            "video_id": video_id,
        },

        "chapters": [],

        "access_status": "partial",

        "access_message": (
            "The YouTube video was found, "
            "but its transcript could not be retrieved."
            + error_details
        ),
    }

def process_web(url):

    try:

        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            allow_redirects=False,
            stream=True,
            headers={
                "User-Agent": USER_AGENT
            },
        )

    except requests.RequestException as error:

        raise SourceProcessingError(
            f"Unable to access this website: {error}"
        )

    if response.status_code in (
        301,
        302,
        303,
        307,
        308,
    ):

        redirect_location = (
            response.headers.get(
                "Location"
            )
        )

        if not redirect_location:

            raise SourceProcessingError(
                "The website returned an invalid redirect."
            )

        redirect_url = urljoin(
            url,
            redirect_location
        )

        redirect_url = validate_url(
            redirect_url
        )

        try:

            response = requests.get(
                redirect_url,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=False,
                stream=True,
                headers={
                    "User-Agent": USER_AGENT
                },
            )

            url = redirect_url

        except requests.RequestException as error:

            raise SourceProcessingError(
                f"Unable to follow the website redirect: {error}"
            )

    if response.status_code >= 400:

        raise SourceProcessingError(
            f"The website returned HTTP "
            f"{response.status_code}."
        )

    content_type = response.headers.get(
        "Content-Type",
        ""
    ).lower()

    content_length = response.headers.get(
        "Content-Length"
    )

    if content_length:

        try:

            if int(content_length) > MAX_CONTENT_SIZE:

                raise SourceProcessingError(
                    "This file is larger than "
                    "the 10 MB limit."
                )

        except ValueError:

            pass

    content = b""

    try:

        for chunk in response.iter_content(
            chunk_size=8192
        ):

            if not chunk:
                continue

            content += chunk

            if len(content) > MAX_CONTENT_SIZE:

                raise SourceProcessingError(
                    "This file is larger than "
                    "the 10 MB limit."
                )

    except requests.RequestException as error:

        raise SourceProcessingError(
            f"Error downloading the source: {error}"
        )

    source_type = detect_source_type(
        url,
        content_type
    )

    # PDF
    if source_type == "pdf":

        text = extract_pdf_text(
            content
        )

        if not text:

            return {
                "source_url": url,
                "source_type": "pdf",
                "title": "PDF Document",
                "author": "",
                "description": "",
                "thumbnail": "",
                "text": "",
                "transcript": "",
                "metadata": {},
                "chapters": [],
                "access_status": "partial",
                "access_message": (
                    "The PDF was opened, "
                    "but no selectable text "
                    "could be extracted."
                ),
            }

        return {
            "source_url": url,
            "source_type": "pdf",
            "title": "PDF Document",
            "author": "",
            "description": "",
            "thumbnail": "",
            "text": text,
            "transcript": "",
            "metadata": {},
            "chapters": [],
            "access_status": "success",
            "access_message": (
                "PDF processed successfully."
            ),
        }

    # HTML
    if (
        "text/html" in content_type
        or source_type in (
            "web",
            "document",
            "social",
        )
    ):

        try:

            encoding = (
                response.encoding
                or "utf-8"
            )

            html = content.decode(
                encoding,
                errors="replace"
            )

        except Exception:

            html = content.decode(
                "utf-8",
                errors="replace"
            )

        extracted = clean_html(
            html
        )

        if not extracted["text"]:

            return {
                "source_url": url,
                "source_type": source_type,
                "title": extracted["title"],
                "author": "",
                "description": extracted["description"],
                "thumbnail": "",
                "text": "",
                "transcript": "",
                "metadata": {},
                "chapters": [],
                "access_status": "partial",
                "access_message": (
                    "The page was reached, "
                    "but readable content "
                    "could not be extracted."
                ),
            }

        return {
            "source_url": url,
            "source_type": source_type,
            "title": (
                extracted["title"]
                or "Web Page"
            ),
            "author": "",
            "description": extracted["description"],
            "thumbnail": "",
            "text": extracted["text"],
            "transcript": "",
            "metadata": {},
            "chapters": [],
            "access_status": "success",
            "access_message": (
                "Source processed successfully."
            ),
        }

    return {
        "source_url": url,
        "source_type": source_type,
        "title": "",
        "author": "",
        "description": "",
        "thumbnail": "",
        "text": "",
        "transcript": "",
        "metadata": {},
        "chapters": [],
        "access_status": "partial",
        "access_message": (
            "The URL was reached, but Cognify "
            "could not extract readable content."
        ),
    }


def process_url(url):

    url = validate_url(url)

    source_type = detect_source_type(
        url
    )

    if source_type == "youtube":

        return process_youtube(
            url
        )

    return process_web(
        url
    )