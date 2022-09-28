from django.urls import path

from vote.views import delegate_data, delegate_view, import_delegates, past_votes, staff_view, vote_action, create_question, close_question

app_name = 'vote'

urlpatterns = [
    path('', delegate_view, name="delegate-view"),
    path('vote/', vote_action, name="vote-action"),
    path('data/', delegate_data, name="delegate-data"),
    path('past/', past_votes, name="delegate-data"),
    path('staff/', staff_view, name="staff-view"),
    path('open/', create_question, name="create-question"),
    path('close/', close_question, name="close-question"),
    path('staff/import/', import_delegates, name="import-view"),
]
