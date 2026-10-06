from django.db import models
from django.contrib.auth.models import User

class AskSource(models.Model):

    SOURCE_TYPES = [
        ("web", "Web Page"),
        ("youtube", "YouTube"),
        ("pdf", "PDF"),
        ("document", "Document"),
        ("social", "Social Media"),
        ("other", "Other"),
    ]

    ACCESS_STATUS = [
        ("processing", "Processing"),
        ("success", "Success"),
        ("partial", "Partial"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ask_sources"
    )

    url = models.URLField(
        max_length=2000
    )

    source_type = models.CharField(
        max_length=30,
        choices=SOURCE_TYPES,
        default="other"
    )

    title = models.CharField(
        max_length=500,
        blank=True
    )

    author = models.CharField(
        max_length=300,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    thumbnail = models.URLField(
        max_length=2000,
        blank=True
    )

    text = models.TextField(
        blank=True
    )

    transcript = models.TextField(
        blank=True
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    chapters = models.JSONField(
        default=list,
        blank=True
    )

    access_status = models.CharField(
        max_length=20,
        choices=ACCESS_STATUS,
        default="processing"
    )

    access_message = models.TextField(
        blank=True
    )

    retrieved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title or self.url


class AskOutput(models.Model):

    OUTPUT_TYPES = [
        ("summary", "Summary"),
        ("notes", "Study Notes"),
        ("audio", "Audio"),
        ("video", "Video"),
        ("quiz", "Quiz"),
    ]

    source = models.ForeignKey(
        AskSource,
        on_delete=models.CASCADE,
        related_name="outputs"
    )

    output_type = models.CharField(
        max_length=20,
        choices=OUTPUT_TYPES
    )

    content = models.TextField(
        blank=True
    )

    metadata = models.JSONField(
        default=dict,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.source} - {self.output_type}"


class AskMessage(models.Model):

    source = models.ForeignKey(
        AskSource,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(
        max_length=20
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
    
class Notebook(models.Model):
    CATEGORY_CHOICES = [
        ("AI", "AI & Machine Learning"),
        ("DA", "Data Analytics"),
        ("WEB", "Web Development"),
        ("DBMS", "Database"),
        ("NETWORK", "Computer Networks"),
        ("OTHER", "Other"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notebooks"
    )

    name = models.CharField(max_length=200)

    description = models.TextField(
        blank=True
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="OTHER"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class Source(models.Model):
    notebook = models.ForeignKey(
        Notebook,
        on_delete=models.CASCADE,
        related_name="sources"
    )

    file = models.FileField(
        upload_to="sources/"
    )

    extracted_text = models.TextField(
        blank=True
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.file.name


class ChatMessage(models.Model):
    notebook = models.ForeignKey(
        Notebook,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.question[:50]


class GeneratedResult(models.Model):
    RESULT_TYPES = [
        ("summary", "Summary"),
        ("faq", "FAQs"),
        ("notes", "Study Notes"),
        ("flashcards", "Flashcards"),
        ("quiz", "Quiz"),
        ("diagram", "Diagram"),
        ("video", "Video"),
        ("audio", "Audio"),
    ]

    notebook = models.ForeignKey(
        Notebook,
        on_delete=models.CASCADE,
        related_name="results"
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    kind = models.CharField(
        max_length=30,
        choices=RESULT_TYPES
    )

    title = models.CharField(
        max_length=200
    )

    content = models.TextField()
    video_file = models.FileField(
    upload_to="generated_videos/",
    blank=True,
    null=True
)

    is_saved = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.title
    
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    bio = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.user.username
    