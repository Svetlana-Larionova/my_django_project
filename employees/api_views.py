from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, ExpressionWrapper, fields
from datetime import date
from django.utils import timezone

from .models import EmployeeProfile
from workplaces.models import Workplace  # Исправляем импорт
from .serializers import (
    EmployeeProfileListSerializer,
    EmployeeProfileDetailSerializer,
    EmployeeProfileCreateUpdateSerializer,
    WorkplaceUpdateSerializer
)
from .filters import EmployeeProfileFilter
from .permissions import EmployeePermissions, IsCaretaker, IsAdministrator


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    """ViewSet для управления сотрудниками"""
    permission_classes = [IsAuthenticated, EmployeePermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_class = EmployeeProfileFilter

    def get_queryset(self):
        queryset = EmployeeProfile.objects.select_related(
            'user', 'workplace'
        ).prefetch_related(
            'images', 'employeeskill_set__skill'
        ).all()

        # Применяем фильтрацию по стажу
        min_experience = self.request.query_params.get('min_experience')
        max_experience = self.request.query_params.get('max_experience')

        if min_experience or max_experience:
            # Вычисляем стаж в днях
            today = timezone.now().date()
            queryset = queryset.annotate(
                experience_days=ExpressionWrapper(
                    today - F('hire_date'),
                    output_field=fields.DurationField()
                )
            )

            if min_experience:
                queryset = queryset.filter(
                    experience_days__days__gte=int(min_experience)
                )
            if max_experience:
                queryset = queryset.filter(
                    experience_days__days__lte=int(max_experience)
                )

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeProfileListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmployeeProfileCreateUpdateSerializer
        return EmployeeProfileDetailSerializer

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Поиск сотрудников по имени и фамилии"""
        query = request.query_params.get('q', '')
        if query:
            employees = self.get_queryset().filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(middle_name__icontains=query)
            )
            serializer = self.get_serializer(employees, many=True)
            return Response(serializer.data)
        return Response([])


class WorkplaceViewSet(viewsets.ModelViewSet):
    """ViewSet для управления рабочими местами"""
    queryset = Workplace.objects.select_related('employee').all()
    serializer_class = WorkplaceUpdateSerializer
    permission_classes = [IsAuthenticated, IsCaretaker | IsAdministrator]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Для чтения разрешаем всем аутентифицированным
            return [IsAuthenticated()]
        return super().get_permissions()