from django_filters import rest_framework as filters
from .models import EmployeeProfile


class EmployeeProfileFilter(filters.FilterSet):
    """Фильтры для сотрудников"""
    min_experience = filters.NumberFilter(
        field_name='work_experience_days',
        lookup_expr='gte',
        method='filter_by_experience'
    )
    max_experience = filters.NumberFilter(
        field_name='work_experience_days',
        lookup_expr='lte',
        method='filter_by_experience'
    )
    skills = filters.CharFilter(method='filter_by_skills')
    skill_names = filters.CharFilter(method='filter_by_skill_names')

    class Meta:
        model = EmployeeProfile
        fields = ['gender', 'skills']

    def filter_by_experience(self, queryset, name, value):
        """Фильтрация по стажу работы"""
        # Стаж вычисляется динамически, поэтому фильтрация будет в представлении
        return queryset

    def filter_by_skills(self, queryset, name, value):
        """Фильтрация по ID навыков"""
        skill_ids = [int(x) for x in value.split(',')]
        return queryset.filter(employeeskill__skill_id__in=skill_ids).distinct()

    def filter_by_skill_names(self, queryset, name, value):
        """Фильтрация по названиям навыков"""
        skill_names = [x.strip() for x in value.split(',')]
        return queryset.filter(employeeskill__skill__name__in=skill_names).distinct()