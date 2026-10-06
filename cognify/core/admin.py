from django.contrib import admin
from .models import Notebook, Source


@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "category",
        "created_at",
    )


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "notebook",
        "file",
        "uploaded_at",
    )