from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasAdminToken

from .models import Enrollment
from .serializers import EnrollmentSerializer


class EnrollmentCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EnrollmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Enrollment saved successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminEnrollmentListView(APIView):
    permission_classes = [HasAdminToken]

    def get(self, request):
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 50))
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
