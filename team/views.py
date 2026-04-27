from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import HasAdminToken

from .models import TeamMember
from .serializers import (
    TeamMemberReorderSerializer,
    TeamMemberSerializer,
    TeamMemberStatusSerializer,
)


class TeamMemberListView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request):
        queryset = TeamMember.objects.filter(is_active=True).order_by("display_order", "full_name", "created_at")
        data = TeamMemberSerializer(queryset, many=True, context={"request": _request}).data
        return Response(data, status=status.HTTP_200_OK)


class TeamMemberDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        member = get_object_or_404(TeamMember, pk=pk, is_active=True)
        serializer = TeamMemberSerializer(member, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminTeamMemberListCreateView(APIView):
    permission_classes = [HasAdminToken]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        try:
            page = int(request.query_params.get("page", 1))
            limit = int(request.query_params.get("limit", 25))
        except ValueError:
            return Response({"message": "Invalid pagination params"}, status=status.HTTP_400_BAD_REQUEST)

        page = max(page, 1)
        limit = min(max(limit, 1), 100)
        offset = (page - 1) * limit

        queryset = TeamMember.objects.all()

        search = (request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(full_name__icontains=search)
                | Q(designation__icontains=search)
                | Q(short_title__icontains=search)
                | Q(email__icontains=search)
            )

        active_filter = (request.query_params.get("isActive") or "").strip().lower()
        if active_filter in {"true", "1", "yes"}:
            queryset = queryset.filter(is_active=True)
        elif active_filter in {"false", "0", "no"}:
            queryset = queryset.filter(is_active=False)

        ordering_map = {
            "displayOrder": "display_order",
            "-displayOrder": "-display_order",
            "fullName": "full_name",
            "-fullName": "-full_name",
            "createdAt": "created_at",
            "-createdAt": "-created_at",
            "updatedAt": "updated_at",
            "-updatedAt": "-updated_at",
        }
        ordering = request.query_params.get("ordering", "displayOrder")
        queryset = queryset.order_by(ordering_map.get(ordering, "display_order"), "full_name")

        total = queryset.count()
        members = queryset[offset : offset + limit]

        return Response(
            {
                "data": TeamMemberSerializer(members, many=True, context={"request": request}).data,
                "total": total,
                "page": page,
                "limit": limit,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = TeamMemberSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            member = serializer.save()
            response_data = TeamMemberSerializer(member, context={"request": request}).data
            return Response(
                {"message": "Team member created successfully", "data": response_data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminTeamMemberDetailView(APIView):
    permission_classes = [HasAdminToken]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, pk):
        member = get_object_or_404(TeamMember, pk=pk)
        data = TeamMemberSerializer(member, context={"request": request}).data
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        member = get_object_or_404(TeamMember, pk=pk)
        serializer = TeamMemberSerializer(member, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Team member updated successfully",
                    "data": TeamMemberSerializer(member, context={"request": request}).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        member = get_object_or_404(TeamMember, pk=pk)
        serializer = TeamMemberSerializer(member, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Team member updated successfully",
                    "data": TeamMemberSerializer(member, context={"request": request}).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, _request, pk):
        member = get_object_or_404(TeamMember, pk=pk)
        member.delete()
        return Response({"message": "Team member deleted successfully"}, status=status.HTTP_200_OK)


class AdminTeamMemberToggleStatusView(APIView):
    permission_classes = [HasAdminToken]

    def patch(self, request, pk):
        member = get_object_or_404(TeamMember, pk=pk)

        if "isActive" in request.data:
            serializer = TeamMemberStatusSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            member.is_active = serializer.validated_data["isActive"]
        else:
            member.is_active = not member.is_active

        member.save(update_fields=["is_active", "updated_at"])
        return Response(
            {
                "message": "Team member status updated successfully",
                "data": TeamMemberSerializer(member, context={"request": request}).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminTeamMemberReorderView(APIView):
    permission_classes = [HasAdminToken]

    def post(self, request):
        serializer = TeamMemberReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data["items"]
        member_ids = [item["id"] for item in items]
        members = {member.id: member for member in TeamMember.objects.filter(id__in=member_ids)}

        if len(members) != len(member_ids):
            return Response({"message": "One or more team members were not found"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            for item in items:
                member = members[item["id"]]
                member.display_order = item["displayOrder"]
            TeamMember.objects.bulk_update(members.values(), ["display_order"])

        return Response({"message": "Display order updated successfully"}, status=status.HTTP_200_OK)
