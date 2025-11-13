from rest_framework import serializers
from django.contrib.auth.models import User
from .models import EmployeeProfile, Skill, EmployeeSkill, EmployeeImage
from workplaces.models import Workplace  # Исправляем импорт


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer(read_only=True)
    skill_id = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source='skill',
        write_only=True
    )

    class Meta:
        model = EmployeeSkill
        fields = ['id', 'skill', 'skill_id', 'level']


class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = ['id', 'image', 'order']


class WorkplaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workplace
        fields = ['id', 'desk_number', 'additional_info']


class EmployeeProfileListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка сотрудников"""
    skills = serializers.SerializerMethodField()
    workplace = WorkplaceSerializer(read_only=True)
    work_experience_days = serializers.ReadOnlyField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'first_name', 'last_name', 'middle_name',
            'gender', 'skills', 'workplace', 'work_experience_days',
            'main_image', 'hire_date'
        ]

    def get_skills(self, obj):
        """Получаем навыки сотрудника"""
        skills = obj.employeeskill_set.all()[:3]  # Первые 3 навыка
        return EmployeeSkillSerializer(skills, many=True).data

    def get_main_image(self, obj):
        """Получаем первое изображение сотрудника"""
        first_image = obj.images.first()
        if first_image:
            return EmployeeImageSerializer(first_image).data
        return None


class EmployeeProfileDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о сотруднике"""
    skills = EmployeeSkillSerializer(many=True, read_only=True, source='employeeskill_set')
    images = EmployeeImageSerializer(many=True, read_only=True)
    workplace = WorkplaceSerializer(read_only=True)
    work_experience_days = serializers.ReadOnlyField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user', 'first_name', 'last_name', 'middle_name',
            'gender', 'description', 'hire_date', 'work_experience_days',
            'skills', 'images', 'workplace'
        ]


class EmployeeProfileCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания и обновления сотрудника"""
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    skills_data = EmployeeSkillSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user_id', 'first_name', 'last_name', 'middle_name',
            'gender', 'description', 'hire_date', 'skills_data'
        ]

    def create(self, validated_data):
        skills_data = validated_data.pop('skills_data', [])
        employee = EmployeeProfile.objects.create(**validated_data)

        # Создаем навыки сотрудника
        for skill_data in skills_data:
            EmployeeSkill.objects.create(employee=employee, **skill_data)

        return employee

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills_data', None)

        # Обновляем основные поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Обновляем навыки если они предоставлены
        if skills_data is not None:
            # Удаляем старые навыки
            instance.employeeskill_set.all().delete()
            # Создаем новые навыки
            for skill_data in skills_data:
                EmployeeSkill.objects.create(employee=instance, **skill_data)

        return instance


class WorkplaceUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления рабочего места"""
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=EmployeeProfile.objects.all(),
        source='employee',
        required=False,
        allow_null=True
    )

    class Meta:
        model = Workplace
        fields = ['id', 'desk_number', 'employee_id', 'additional_info']

    def validate(self, data):
        """Валидация для проверки соседних столов"""
        workplace = Workplace(**data)

        try:
            # Используем существующий метод clean для валидации
            workplace.clean()
        except Exception as e:
            raise serializers.ValidationError(str(e))

        return data