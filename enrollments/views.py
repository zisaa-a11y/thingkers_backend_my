from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasAdminToken

from .models import Enrollment
from .serializers import EnrollmentFormOptionsSerializer, EnrollmentSerializer


FEATURED_CONTENT = [
    {
        "slug": "beginner-track",
        "title": "Beginner Track",
        "description": "Start your journey with beginner-friendly lessons and guided exercises.",
    },
    {
        "slug": "intermediate-track",
        "title": "Intermediate Track",
        "description": "Build real-world projects and sharpen your practical development skills.",
    },
    {
        "slug": "advanced-track",
        "title": "Advanced Track",
        "description": "Work on expert-level architecture, optimization, and deployment scenarios.",
    },
]


class EnrollmentCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Enrollment saved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnrollmentFormOptionsView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request):
        payload = {
            "pythonLevelOptions": Enrollment.as_options(Enrollment.LEVEL_CHOICES),
            "preferredBatchOptions": Enrollment.as_options(Enrollment.BATCH_CHOICES),
            "courses": Enrollment.as_options(Enrollment.COURSE_CHOICES),
            "featuredContent": FEATURED_CONTENT,
        }
        serializer = EnrollmentFormOptionsSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class AdminEnrollmentListView(APIView):
    permission_classes = [HasAdminToken]

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 50))
        except ValueError:
            return Response(
                {"message": "Invalid pagination params"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        page = page if page > 0 else 1
        limit = min(max(limit, 1), 100)
        offset = (page - 1) * limit

        queryset = Enrollment.objects.all()
        total = queryset.count()
        enrollments = queryset[offset : offset + limit]
        data = EnrollmentSerializer(enrollments, many=True).data

        if "page" in request.query_params or "limit" in request.query_params:
            return Response(
                {
                    "data": data,
                    "total": total,
                    "page": page,
                    "limit": limit,
                },
                status=status.HTTP_200_OK,
            )

        return Response(data, status=status.HTTP_200_OK)


class AdminEnrollmentDeleteView(APIView):
    permission_classes = [HasAdminToken]

    def delete(self, request, pk):
        if not pk:
            return Response({"message": "Invalid enrollment id"}, status=status.HTTP_400_BAD_REQUEST)
        enrollment = get_object_or_404(Enrollment, pk=pk)
        enrollment.delete()
        return Response(
            {"message": "Enrollment deleted successfully"},
            status=status.HTTP_200_OK,
        )
