# ACURA MED — Frontend organizado

Esta versão separa o dashboard monolítico em Base + Topbar + Menubar + Workspace + módulos.

## Fluxo
- `base/base.html`: shell da aplicação.
- `base/topbar.html`: Topbar permanente.
- `base/menubar.html`: Menu permanente.
- `navigation.js`: carrega `/modulos/<modulo>/` dentro de `#workspace`.
- Cada módulo possui `painel.html`, `modais.html`, CSS e JS próprios.

## Módulos presentes na fonte atual
Dashboard, Atendimento, Encaminhamento, Convênios, Colaboradores, Pacientes, Agendamentos e Configurações.

## Django
O frontend espera que cada URL `/modulos/<modulo>/` devolva o `painel.html` do módulo, com o respetivo `modais.html` incluído. As views/URLs Django não foram incluídas porque esta entrega é somente frontend.

## Ícones
Copie a pasta `icons/` que já existe no seu projeto para `static/icons/`.
