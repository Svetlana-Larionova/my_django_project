from rest_framework import permissions


class IsVisitor(permissions.BasePermission):
    """Права для посетителя - только чтение"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False


class IsCaretaker(permissions.BasePermission):
    """Права для смотрителя - чтение и перемещение между столами"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Разрешаем PATCH для обновления рабочих мест
        if request.method == 'PATCH' and view.__class__.__name__ == 'WorkplaceViewSet':
            return True
        return False


class IsAdministrator(permissions.BasePermission):
    """Права для администратора - полный доступ"""

    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser


class EmployeePermissions(permissions.BasePermission):
    """Комплексные права для сотрудников"""

    def has_permission(self, request, view):
        # Посетитель - только GET
        if request.method in permissions.SAFE_METHODS:
            return True

        # Администратор - полный доступ
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Смотритель - только чтение для сотрудников
        return False