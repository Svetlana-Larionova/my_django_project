from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import EmployeeProfile, Skill, EmployeeSkill
from workplaces.models import Workplace  # Исправляем импорт
from datetime import date


class Command(BaseCommand):
    help = 'Create test users with different permissions and sample data'

    def handle(self, *args, **options):
        # Создаем навыки
        backend_skill, _ = Skill.objects.get_or_create(name='бэкенд')
        frontend_skill, _ = Skill.objects.get_or_create(name='фронтенд')
        testing_skill, _ = Skill.objects.get_or_create(name='тестирование')
        management_skill, _ = Skill.objects.get_or_create(name='управление')

        # Создаем посетителя
        visitor, created = User.objects.get_or_create(
            username='visitor',
            defaults={
                'email': 'visitor@example.com',
                'first_name': 'Посетитель',
                'last_name': 'Тестовый'
            }
        )
        visitor.set_password('visitor123')
        visitor.save()

        # Создаем профиль посетителя
        visitor_profile, _ = EmployeeProfile.objects.get_or_create(user=visitor)
        visitor_profile.first_name = 'Посетитель'
        visitor_profile.last_name = 'Тестовый'
        visitor_profile.gender = 'M'
        visitor_profile.hire_date = date(2024, 1, 1)
        visitor_profile.save()

        # Создаем смотрителя
        caretaker, created = User.objects.get_or_create(
            username='caretaker',
            defaults={
                'email': 'caretaker@example.com',
                'first_name': 'Смотритель',
                'last_name': 'Тестовый'
            }
        )
        caretaker.set_password('caretaker123')
        caretaker.save()

        # Создаем профиль смотрителя
        caretaker_profile, _ = EmployeeProfile.objects.get_or_create(user=caretaker)
        caretaker_profile.first_name = 'Смотритель'
        caretaker_profile.last_name = 'Тестовый'
        caretaker_profile.gender = 'M'
        caretaker_profile.hire_date = date(2024, 2, 1)
        caretaker_profile.save()

        # Добавляем навыки смотрителю
        EmployeeSkill.objects.get_or_create(
            employee=caretaker_profile,
            skill=management_skill,
            defaults={'level': 7}
        )

        # Создаем администратора
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Администратор',
                'last_name': 'Тестовый',
                'is_staff': True
            }
        )
        admin.set_password('admin123')
        admin.is_staff = True
        admin.is_superuser = True
        admin.save()

        # Создаем профиль администратора
        admin_profile, _ = EmployeeProfile.objects.get_or_create(user=admin)
        admin_profile.first_name = 'Администратор'
        admin_profile.last_name = 'Тестовый'
        admin_profile.gender = 'M'
        admin_profile.hire_date = date(2024, 3, 1)
        admin_profile.save()

        # Добавляем навыки администратору
        EmployeeSkill.objects.get_or_create(
            employee=admin_profile,
            skill=management_skill,
            defaults={'level': 9}
        )

        # Создаем тестовых сотрудников
        test_users_data = [
            {
                'username': 'developer1',
                'first_name': 'Иван',
                'last_name': 'Разработчиков',
                'skills': [backend_skill],
                'desk_number': '101'
            },
            {
                'username': 'developer2',
                'first_name': 'Петр',
                'last_name': 'Программистов',
                'skills': [frontend_skill],
                'desk_number': '103'
            },
            {
                'username': 'tester1',
                'first_name': 'Мария',
                'last_name': 'Тестировщикова',
                'skills': [testing_skill],
                'desk_number': '105'
            },
            {
                'username': 'manager1',
                'first_name': 'Анна',
                'last_name': 'Менеджерова',
                'skills': [management_skill],
                'desk_number': '107'
            }
        ]

        for user_data in test_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': f"{user_data['username']}@example.com",
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            if created:
                user.set_password('test123')
                user.save()

            # Создаем профиль сотрудника
            profile, _ = EmployeeProfile.objects.get_or_create(user=user)
            profile.first_name = user_data['first_name']
            profile.last_name = user_data['last_name']
            profile.gender = 'M' if user_data['first_name'] in ['Иван', 'Петр'] else 'F'
            profile.hire_date = date(2024, 4, 1)
            profile.save()

            # Добавляем навыки
            for skill in user_data['skills']:
                EmployeeSkill.objects.get_or_create(
                    employee=profile,
                    skill=skill,
                    defaults={'level': 8}
                )

            # Создаем рабочее место
            Workplace.objects.get_or_create(
                desk_number=user_data['desk_number'],
                defaults={'employee': profile}
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created test users and data:\n\n'
                '🔐 Authentication Users:\n'
                'Visitor: visitor / visitor123 (read-only)\n'
                'Caretaker: caretaker / caretaker123 (can move employees)\n'
                'Admin: admin / admin123 (full access)\n\n'
                '👥 Test Employees:\n'
                'developer1 / test123 - Backend Developer\n'
                'developer2 / test123 - Frontend Developer\n'
                'tester1 / test123 - Tester\n'
                'manager1 / test123 - Manager\n\n'
                '🪑 Workplaces created: 101, 103, 105, 107\n'
                '💼 Skills created: бэкенд, фронтенд, тестирование, управление'
            )
        )