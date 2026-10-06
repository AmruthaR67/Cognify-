from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static


from core import views

urlpatterns = [ 

    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    # Landing page
    path("", views.landing, name="landing"),

    # Authentication
    path("register/", views.register_view, name="register"),
    path("verify/", views.verify_otp, name="verify"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Main application
    path("dashboard/", views.dashboard, name="dashboard"),

    path(
        "notebook/create/",
        views.create_notebook,
        name="create_notebook",
    ),

    path(
        "notebook/<int:notebook_id>/",
        views.workspace,
        name="workspace",
    ),
    path(
    "notebook/<int:notebook_id>/summary/",
    views.generate_summary,
    name="generate_summary",
),
path(
    "notebook/<int:notebook_id>/ask/",
    views.ask_question,
    name="ask_question",
),
    # Upload sources
    path(
        "notebook/<int:notebook_id>/upload/",
        views.upload_source,
        name="upload_source",
    ),

    # Delete source
    path(
        "source/<int:source_id>/delete/",
        views.delete_source,
        name="delete_source",
    ),

    # AI outputs
    path(
        "notebook/<int:notebook_id>/generate/<str:kind>/",
        views.generate_output,
        name="generate_output",
    ),

    # Other modules
    path("history/", views.history, name="history"),
    path("saved/", views.saved_results, name="saved"),
    path("profile/", views.profile, name="profile"),
    path("settings/", views.settings_page, name="settings"),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )