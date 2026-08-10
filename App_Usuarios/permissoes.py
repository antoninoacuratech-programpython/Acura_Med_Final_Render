from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .perfil_permissao import PerfilPermissao


def tem_permissao(user, codigo):
    if not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not user.perfil:
        return False

    return PerfilPermissao.objects.filter(
        perfil=user.perfil,
        permissao__codigo=codigo,
        permissao__ativo=True,
    ).exists()


def requer_permissao(codigo, redirect_url="dashboard"):
    """
    Decorator para views baseadas em função. Usa a convenção de código
    "modulo.acao" no singular (ex: "paciente.cadastrar", "paciente.eliminar").

    Uso:
        @login_required
        @requer_permissao("paciente.cadastrar")
        def cadastrar_paciente(request):
            ...
    """
    def decorador(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not tem_permissao(request.user, codigo):
                messages.error(request, "Você não tem permissão para acessar esta página.")
                return redirect(redirect_url)
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorador
