from django.urls import path

from .views import (
    AdminEnrollmentDeleteView,
    AdminEnrollmentListView,
    EnrollmentCreateView,
    EnrollmentFormOptionsView,
)

urlpatterns = [
    path("enrollment/form-options", EnrollmentFormOptionsView.as_view()),
    path("python", EnrollmentCreateView.as_view()),
    path("admin/enrollments", AdminEnrollmentListView.as_view()),
    path("admin/enrollments/<uuid:pk>", AdminEnrollmentDeleteView.as_view()),
]
