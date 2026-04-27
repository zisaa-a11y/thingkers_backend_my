from django.urls import path

from .views import (
    AdminTeamMemberDetailView,
    AdminTeamMemberListCreateView,
    AdminTeamMemberReorderView,
    AdminTeamMemberToggleStatusView,
    TeamMemberDetailView,
    TeamMemberListView,
)

urlpatterns = [
    path("team-members", TeamMemberListView.as_view()),
    path("team-members/<uuid:pk>", TeamMemberDetailView.as_view()),
    path("admin/team-members", AdminTeamMemberListCreateView.as_view()),
    path("admin/team-members/reorder", AdminTeamMemberReorderView.as_view()),
    path("admin/team-members/<uuid:pk>", AdminTeamMemberDetailView.as_view()),
    path("admin/team-members/<uuid:pk>/toggle-status", AdminTeamMemberToggleStatusView.as_view()),
]
