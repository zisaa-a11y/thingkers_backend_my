from django.urls import path

from .views import AdminEnrollmentDeleteView, AdminEnrollmentListView, EnrollmentCreateView

urlpatterns = [
    path("python", EnrollmentCreateView.as_view()),
    path("admin/enrollments", AdminEnrollmentListView.as_view()),
    path("admin/enrollments/<uuid:pk>", AdminEnrollmentDeleteView.as_view()),
]
