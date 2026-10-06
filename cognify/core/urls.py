from django.urls import path
from . import views
from .views import ask_ai


urlpatterns = [

    # ==============================
    # ASK COGNIFY
    # ==============================

    path(
        "ask-cognify/",
        views.ask_cognify,
        name="ask_cognify",
    ),

    path(
        "ask-cognify/process/",
        views.process_ask_source,
        name="process_ask_source",
    ),

    path(
        "ask-cognify/<int:source_id>/generate/",
        views.generate_ask_output,
        name="generate_ask_output",
    ),

    # ==============================
    # AI
    # ==============================

    path(
        "ask-ai/",
        ask_ai,
        name="ask_ai",
    ),path(
    "ai-tutor/",
    views.ai_tutor,
    name="ai_tutor",
),
path(
    "mock-test/",
    views.mock_test,
    name="mock_test",
),
    # ==============================
    # NOTEBOOKS
    # ==============================

    path(
        "notebooks/",
        views.my_notebooks,
        name="my_notebooks",
    ),

    path(
        "notebook/<int:notebook_id>/",
        views.notebook_detail,
        name="notebook_detail",
    ),

    path(
        "notebook/<int:notebook_id>/add-source/",
        views.add_source,
        name="add_source",
    ),

    path(
        "notebook/<int:notebook_id>/ask/",
        views.ask_question,
        name="ask_question",
    ),

    path(
        "notebook/<int:notebook_id>/summary/",
        views.generate_summary,
        name="generate_summary",
    ),

    path(
        "notebook/<int:notebook_id>/faq/",
        views.generate_faq,
        name="generate_faq",
    ),

    path(
        "notebook/<int:notebook_id>/notes/",
        views.generate_notes,
        name="generate_notes",
    ),

    path(
        "notebook/<int:notebook_id>/flashcards/",
        views.generate_flashcards,
        name="generate_flashcards",
    ),

    path(
        "notebook/<int:notebook_id>/quiz/",
        views.generate_quiz,
        name="generate_quiz",
    ),

    path(
        "notebook/<int:notebook_id>/diagram/",
        views.generate_diagram,
        name="generate_diagram",
    ),

    # ==============================
    # AUDIO / VIDEO
    # ==============================
path(
    "notebook/<int:notebook_id>/audio/",
    views.generate_wav_audio,
    name="generate_audio",
),
    path(
        "notebook/<int:notebook_id>/video/",
        views.generate_video,
        name="generate_video",
    ),

    path(
        "notebook/<int:notebook_id>/video/start/",
        views.start_video_generation,
        name="start_video_generation",
    ),

    path(
        "notebook/<int:notebook_id>/video/status/<int:result_id>/",
        views.video_status,
        name="video_status",
    ),

    # ==============================
    # RESULTS
    # ==============================

    path(
        "result/<int:result_id>/",
        views.result_detail,
        name="result_detail",
    ),

    path(
        "result/<int:result_id>/save/",
        views.save_result,
        name="save_result",
    ),

    path(
        "result/<int:result_id>/summary-status/",
        views.summary_status,
        name="summary_status",
    ),

    # ==============================
    # HISTORY
    # ==============================

    path(
        "history/",
        views.history,
        name="history",
    ),

    # ==============================
    # SAVED
    # ==============================

    path(
        "saved/",
        views.saved_results,
        name="saved_results",
    ),

    path(
        "saved/toggle/<int:result_id>/",
        views.toggle_saved,
        name="toggle_saved",
    ),

    # ==============================
    # PROFILE
    # ==============================

    path(
        "profile/",
        views.profile,
        name="profile",
    ),

    # ==============================
    # SETTINGS
    # ==============================

    path(
        "settings/",
        views.settings_page,
        name="settings_page",
    ),

    # ==============================
    # SECURITY
    # ==============================

    path(
        "security/",
        views.security,
        name="security",
    ),

    # ==============================
    # DASHBOARD
    # ==============================

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    # ==============================
    # DELETE NOTEBOOK
    # ==============================

    path(
        "notebook/<int:notebook_id>/delete/",
        views.delete_notebook,
        name="delete_notebook",
    ),
]