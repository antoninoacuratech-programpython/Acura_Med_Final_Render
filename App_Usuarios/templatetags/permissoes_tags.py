from django import template

from App_Usuarios.permissoes import tem_permissao as _tem_permissao

register = template.Library()


@register.filter(name="tem_permissao")
def tem_permissao(user, codigo):
    """
    Uso no template: {% if request.user|tem_permissao:"paciente.gerir" %}
    Reaproveita a mesma função usada pelo decorator requer_permissao,
    para o menu e as views nunca ficarem dessincronizados.
    """
    return _tem_permissao(user, codigo)