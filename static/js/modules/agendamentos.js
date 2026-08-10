(function () {
    "use strict";

    window.moduleInitializers = window.moduleInitializers || {};

    window.moduleInitializers.agendamentos = function () {
        const pagina = document.getElementById("agendamentosPage");
        if (!pagina) return;

        const urlCadastrar = pagina.dataset.urlCadastrar;
        const urlDetalheTemplate = pagina.dataset.urlDetalheTemplate;
        const urlAtualizarTemplate = pagina.dataset.urlAtualizarTemplate;
        const urlStatusTemplate = pagina.dataset.urlStatusTemplate;
        const urlEliminarTemplate = pagina.dataset.urlEliminarTemplate;

        const ID_PLACEHOLDER = "999999999";

        const modal = document.getElementById("modalAgendamento");
        const overlay = document.getElementById("overlayAgendamento");
        const form = document.getElementById("formAgendamento");
        const titulo = document.getElementById("modalAgendamentoTitulo");
        const erroBox = document.getElementById("erroAgendamento");
        const campoId = document.getElementById("agendamentoId");
        const btnSalvarTexto = document.getElementById("btnSalvarAgendamentoTexto");
        const btnSalvar = document.getElementById("btnSalvarAgendamento");

        const modalEliminar = document.getElementById("modalConfirmarEliminarAgendamento");
        const overlayEliminar = document.getElementById("overlayConfirmarEliminarAgendamento");
        const descricaoEliminar = document.getElementById("descricaoAgendamentoEliminar");

        let idParaEliminar = null;

        function getCookie(nome) {
            const valor = `; ${document.cookie}`;
            const partes = valor.split(`; ${nome}=`);
            if (partes.length === 2) return partes.pop().split(";").shift();
            return null;
        }

        const csrftoken = getCookie("csrftoken");

        function montarUrl(template, id) {
            return template.replace(ID_PLACEHOLDER, id);
        }

        function toast(mensagem, tipo) {
            if (typeof window.showToast === "function") {
                window.showToast(mensagem, tipo || "success");
            }
        }

        function mostrarErro(mensagem) {
            erroBox.textContent = mensagem;
            erroBox.classList.remove("hidden");
        }

        function limparErro() {
            erroBox.textContent = "";
            erroBox.classList.add("hidden");
        }

        function recarregarModulo() {
            if (typeof window.loadModule === "function") {
                window.loadModule("agendamentos", "Agendamentos");
            } else {
                window.location.reload();
            }
        }

        // ---------------------------------------------------------------
        // Abrir / Fechar modal
        // ---------------------------------------------------------------

        function abrirModal() {
            modal.classList.remove("hidden");
            modal.classList.add("flex");
            document.body.classList.add("overflow-hidden");
        }

        function fecharModal() {
            modal.classList.add("hidden");
            modal.classList.remove("flex");
            document.body.classList.remove("overflow-hidden");
            form.reset();
            campoId.value = "";
            limparErro();
        }

        function prepararModoCriar() {
            form.reset();
            campoId.value = "";
            titulo.textContent = "Novo Agendamento";
            btnSalvarTexto.textContent = "Criar Agendamento";
            document.getElementById("duracaoMinutos").value = 30;
            limparErro();
            abrirModal();
        }

        function preencherFormulario(agendamento) {
            campoId.value = agendamento.id;
            document.getElementById("pacienteSelect").value = agendamento.paciente_id || "";
            document.getElementById("profissionalSelect").value = agendamento.profissional_id || "";
            document.getElementById("departamentoSelect").value = agendamento.departamento_id || "";
            document.getElementById("especialidadeSelect").value = agendamento.especialidade_id || "";
            document.getElementById("dataHora").value = agendamento.data_hora || "";
            document.getElementById("duracaoMinutos").value = agendamento.duracao_minutos || 30;
            document.getElementById("statusSelect").value = agendamento.status || "agendado";
            document.getElementById("motivo").value = agendamento.motivo || "";
            document.getElementById("observacoes").value = agendamento.observacoes || "";
        }

        async function prepararModoEditar(id) {
            limparErro();
            titulo.textContent = "Editar Agendamento";
            btnSalvarTexto.textContent = "Guardar Alterações";

            try {
                const resposta = await fetch(montarUrl(urlDetalheTemplate, id));
                const dados = await resposta.json();

                if (!dados.ok) {
                    toast(dados.erro || "Não foi possível carregar o agendamento.", "error");
                    return;
                }

                preencherFormulario(dados.agendamento);
                abrirModal();
            } catch (erro) {
                toast("Erro de ligação ao carregar o agendamento.", "error");
            }
        }

        // ---------------------------------------------------------------
        // Submeter formulário (criar / atualizar)
        // ---------------------------------------------------------------

        form.addEventListener("submit", async function (evento) {
            evento.preventDefault();
            limparErro();

            const id = campoId.value;
            const url = id ? montarUrl(urlAtualizarTemplate, id) : urlCadastrar;
            const dadosFormulario = new FormData(form);

            btnSalvar.disabled = true;
            btnSalvar.classList.add("opacity-60", "cursor-not-allowed");

            try {
                const resposta = await fetch(url, {
                    method: "POST",
                    headers: { "X-CSRFToken": csrftoken },
                    body: dadosFormulario,
                });

                const dados = await resposta.json();

                if (!dados.ok) {
                    mostrarErro(dados.erro || "Não foi possível guardar o agendamento.");
                    return;
                }

                fecharModal();
                toast(dados.mensagem);
                recarregarModulo();
            } catch (erro) {
                mostrarErro("Erro de ligação. Tente novamente.");
            } finally {
                btnSalvar.disabled = false;
                btnSalvar.classList.remove("opacity-60", "cursor-not-allowed");
            }
        });

        // ---------------------------------------------------------------
        // Alteração rápida de status (select na tabela)
        // ---------------------------------------------------------------

        async function alterarStatus(id, novoStatus) {
            try {
                const corpo = new URLSearchParams({ status: novoStatus });
                const resposta = await fetch(montarUrl(urlStatusTemplate, id), {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken,
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    body: corpo,
                });

                const dados = await resposta.json();

                if (!dados.ok) {
                    toast(dados.erro || "Não foi possível alterar o status.", "error");
                    return;
                }

                toast(dados.mensagem);
            } catch (erro) {
                toast("Erro de ligação ao alterar o status.", "error");
            }
        }

        // ---------------------------------------------------------------
        // Eliminar
        // ---------------------------------------------------------------

        function abrirConfirmacaoEliminar(id, descricao) {
            idParaEliminar = id;
            descricaoEliminar.textContent = descricao;
            modalEliminar.classList.remove("hidden");
            modalEliminar.classList.add("flex");
        }

        function fecharConfirmacaoEliminar() {
            idParaEliminar = null;
            modalEliminar.classList.add("hidden");
            modalEliminar.classList.remove("flex");
        }

        async function confirmarEliminar() {
            if (!idParaEliminar) return;

            try {
                const resposta = await fetch(montarUrl(urlEliminarTemplate, idParaEliminar), {
                    method: "POST",
                    headers: { "X-CSRFToken": csrftoken },
                });

                const dados = await resposta.json();
                fecharConfirmacaoEliminar();

                if (!dados.ok) {
                    toast(dados.erro || "Não foi possível eliminar o agendamento.", "error");
                    return;
                }

                toast(dados.mensagem);
                recarregarModulo();
            } catch (erro) {
                fecharConfirmacaoEliminar();
                toast("Erro de ligação ao eliminar o agendamento.", "error");
            }
        }

        // ---------------------------------------------------------------
        // Pesquisa em tempo real
        // ---------------------------------------------------------------

        function aplicarPesquisa() {
            const campoPesquisa = document.getElementById("pesquisaAgendamento");
            const termo = campoPesquisa.value.trim().toLowerCase();
            const linhas = document.querySelectorAll(".linha-agendamento");
            const semResultado = document.getElementById("semResultadoPesquisa");
            let visiveis = 0;

            linhas.forEach((linha) => {
                const corresponde =
                    linha.dataset.paciente.includes(termo) || linha.dataset.profissional.includes(termo);
                linha.classList.toggle("hidden", !corresponde);
                if (corresponde) visiveis += 1;
            });

            semResultado.classList.toggle("hidden", visiveis !== 0 || linhas.length === 0);
        }

        // ---------------------------------------------------------------
        // Ligação dos eventos (DOM recém-injetado — sem listeners antigos)
        // ---------------------------------------------------------------

        document.getElementById("btnNovoAgendamento").addEventListener("click", prepararModoCriar);
        document.getElementById("btnFecharModalAgendamento").addEventListener("click", fecharModal);
        document.getElementById("btnCancelarAgendamento").addEventListener("click", fecharModal);
        overlay.addEventListener("click", fecharModal);

        document.getElementById("btnCancelarEliminarAgendamento").addEventListener("click", fecharConfirmacaoEliminar);
        overlayEliminar.addEventListener("click", fecharConfirmacaoEliminar);
        document.getElementById("btnConfirmarEliminarAgendamento").addEventListener("click", confirmarEliminar);

        const pesquisaInput = document.getElementById("pesquisaAgendamento");
        if (pesquisaInput) pesquisaInput.addEventListener("input", aplicarPesquisa);

        document.getElementById("tabelaAgendamentos").addEventListener("click", function (evento) {
            const botao = evento.target.closest("button[data-action]");
            if (!botao) return;

            const acao = botao.dataset.action;
            const id = botao.dataset.id;

            if (acao === "editar") prepararModoEditar(id);
            if (acao === "eliminar") abrirConfirmacaoEliminar(id, botao.dataset.descricao);
        });

        document.getElementById("tabelaAgendamentos").addEventListener("change", function (evento) {
            const select = evento.target.closest("select[data-action='status']");
            if (!select) return;
            alterarStatus(select.dataset.id, select.value);
        });

        document.addEventListener("keydown", function (evento) {
            if (evento.key !== "Escape") return;
            if (!modal.classList.contains("hidden")) fecharModal();
            if (!modalEliminar.classList.contains("hidden")) fecharConfirmacaoEliminar();
        });
    };
})();