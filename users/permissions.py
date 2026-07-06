from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
        Permette l'accesso solo agli utenti con ruolo ADMIN.
    """

    def has_permission(self, request, view) -> bool:
        """
        Verifica che l'utente sia autenticato e abbia ruolo ADMIN.
        :param request: Richiesta HTTP
        :param view: vista che richiede il permesse
        :return: True se l'utente è Admin, False altrimenti
        """
        return bool(request.user and request.user.is_authenticated and request.user.role == 'ADMIN')


class IsManagerUser(permissions.BasePermission):
    """
        Permette l'accesso solo agli utenti con ruolo MANAGER.
    """
    def has_permission(self, request, view) -> bool:
        """
        Verifica che l'utente sia autenticato e abbia ruolo MANAGER.
        :param request: Richiesta HTTP
        :param view: vista che richiede il permesso
        :return: True se l'utente è Manager, False altrimenti
        """
        return bool(request.user and request.user.is_authenticated and request.user.role == 'MANAGER')


class IsManagerOrAdmin(permissions.BasePermission):
    """
        Permette l'accesso agli utenti con ruolo MANAGER o ADMIN.
    """
    def has_permission(self, request, view) -> bool:
        """
        Verifica che l'utente sia autenticato e abbia ruolo MANAGER o ADMIN.
        :param request: Richiesta HTTP
        :param view: vista che richiede il permesso
        :return: True se l'utente è Manager o Admin, False altrimenti
        """
        return bool(request.user and request.user.is_authenticated and request.user.role in ('MANAGER', 'ADMIN'))
