/**
 * static/js/modules/ultilizador.js
 * Gestão de Utilizadores (Colaboradores) — AcuraMed
 *
 * Depende de:
 *  - #colaboradoresPage com data-url-cadastrar / data-url-detalhe-template /
 *    data-url-atualizar-template / data-url-status-template / data-url-eliminar-template
 *  - colaboradores/modal.html incluído na mesma página
 *  - static/js/script.js (para o toggle de mostrar/ocultar senha via .toggle-password)
 */

(function () {
    "use strict";

    const pagina = document.getElementById("colaboradoresPage");
    if (!pagina) return;

    const urlCadastrar = pagina.dataset.urlCadastrar;
    const urlDetalheTemplate = pagina.dataset.urlDetalheTemplate;
    const urlAtualizarTemplate = pagina.dataset.urlAtualizarTemplate;
    const urlStatusTemplate = pagina.dataset.urlStatusTemplate;
    const urlEliminarTemplate = pagina.dataset.urlEliminarTemplate;

    const ID_PLACEHOLDER = "999999999";

    const modal = document.getElementById("modalUtilizador");
    const overlay = document.getElementById("overlayUtilizador");
    const form = document.getElementById("formUtilizador");
    const titulo = document.getElementById("modalUtilizadorTitulo");
    const erroBox = document.getElementById("erroUtilizador");
    const campoId = document.getElementById("utilizadorId");
    const labelSenha = document.getElementById("labelSenha");
    const dicaSenha = document.getElementById("dicaSenha");
    const campoSenha = document.getElementById("senha");
    const campoConfirmarSenha = document.getElementById("confirmarSenha");
    const btnSalvarTexto = document.getElementById("btnSalvarUtilizadorTexto");
    const btnSalvar = document.getElementById("btnSalvarUtilizador");

    const modalEliminar = document.getElementById("modalConfirmarEliminar");
    const overlayEliminar = document.getElementById("overlayConfirmarEliminar");
    const nomeUtilizadorEliminar = document.getElementById("nomeUtilizadorEliminar");

    let idParaEliminar = null;

    // ---------------------------------------------------------------
    // Utilitários
    // ---------------------------------------------------------------

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

    function mostrarToast(mensagem, sucesso = true) {
        const toast = document.getElementById("toastUtilizador");
        const icone = document.getElementById("toastUtilizadorIcone");
        const texto = document.getElementById("toastUtilizadorTexto");

        texto.textContent = mensagem;
        icone.className = sucesso
            ? "fa-solid fa-circle-check text-emerald-500"
            : "fa-solid fa-circle-exclamation text-red-500";

        toast.classList.remove("hidden");
        toast.classList.add("flex");

        setTimeout(() => {
            toast.classList.add("hidden");
            toast.classList.remove("flex");
        }, 3200);
    }

    function mostrarErro(mensagem) {
        erroBox.textContent = mensagem;
        erroBox.classList.remove("hidden");
    }

    function limparErro() {
        erroBox.textContent = "";
        erroBox.classList.add("hidden");
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
        titulo.textContent = "Novo Utilizador";
        btnSalvarTexto.textContent = "Criar Utilizador";
        labelSenha.textContent = "Senha";
        dicaSenha.classList.add("hidden");
        campoSenha.required = true;
        campoConfirmarSenha.required = true;
        document.getElementById("isActive").checked = true;
        limparErro();
        abrirModal();
    }

    function preencherFormulario(utilizador) {
        campoId.value = utilizador.id;
        document.getElementById("primeiroNome").value = utilizador.primeiro_nome || "";
        document.getElementById("ultimoNome").value = utilizador.ultimo_nome || "";
        document.getElementById("utilizadorEmail").value = utilizador.email || "";
        document.getElementById("telefone").value = utilizador.telefone || "";
        document.getElementById("cargo").value = utilizador.cargo || "";
        document.getElementById("hospitalSelect").value = utilizador.hospital_id || "";
        document.getElementById("perfilSelect").value = utilizador.perfil_id || "";
        document.getElementById("departamentoSelect").value = utilizador.departamento_id || "";
        document.getElementById("especialidadeSelect").value = utilizador.especialidade_id || "";
        document.getElementById("isActive").checked = !!utilizador.is_active;
    }

    async function prepararModoEditar(id) {
        limparErro();
        titulo.textContent = "Editar Utilizador";
        btnSalvarTexto.textContent = "Guardar Alterações";
        labelSenha.textContent = "Nova Senha";
        dicaSenha.classList.remove("hidden");
        campoSenha.required = false;
        campoConfirmarSenha.required = false;

        try {
            const resposta = await fetch(montarUrl(urlDetalheTemplate, id));
            const dados = await resposta.json();

            if (!dados.ok) {
                mostrarToast(dados.erro || "Não foi possível carregar o utilizador.", false);
                return;
            }

            campoId.value = id;
            preencherFormulario(dados.utilizador);
            abrirModal();
        } catch (erro) {
            mostrarToast("Erro de ligação ao carregar o utilizador.", false);
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
                mostrarErro(dados.erro || "Não foi possível guardar o utilizador.");
                return;
            }

            fecharModal();
            mostrarToast(dados.mensagem);
            setTimeout(() => window.location.reload(), 900);
        } catch (erro) {
            mostrarErro("Erro de ligação. Tente novamente.");
        } finally {
            btnSalvar.disabled = false;
            btnSalvar.classList.remove("opacity-60", "cursor-not-allowed");
        }
    });

    // ---------------------------------------------------------------
    // Ativar / Desativar
    // ---------------------------------------------------------------

    async function alternarStatus(id) {
        try {
            const resposta = await fetch(montarUrl(urlStatusTemplate, id), {
                method: "POST",
                headers: { "X-CSRFToken": csrftoken },
            });

            const dados = await resposta.json();

            if (!dados.ok) {
                mostrarToast(dados.erro || "Não foi possível alterar o status.", false);
                return;
            }

            mostrarToast(dados.mensagem);
            setTimeout(() => window.location.reload(), 900);
        } catch (erro) {
            mostrarToast("Erro de ligação ao alterar o status.", false);
        }
    }

    // ---------------------------------------------------------------
    // Eliminar
    // ---------------------------------------------------------------

    function abrirConfirmacaoEliminar(id, nome) {
        idParaEliminar = id;
        nomeUtilizadorEliminar.textContent = nome;
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
                mostrarToast(dados.erro || "Não foi possível eliminar o utilizador.", false);
                return;
            }

            mostrarToast(dados.mensagem);
            setTimeout(() => window.location.reload(), 900);
        } catch (erro) {
            fecharConfirmacaoEliminar();
            mostrarToast("Erro de ligação ao eliminar o utilizador.", false);
        }
    }

    // ---------------------------------------------------------------
    // Pesquisa em tempo real
    // ---------------------------------------------------------------

    function aplicarPesquisa() {
        const campoPesquisa = document.getElementById("pesquisaUtilizador");
        const termo = campoPesquisa.value.trim().toLowerCase();
        const linhas = document.querySelectorAll(".linha-utilizador");
        const semResultado = document.getElementById("semResultadoPesquisa");
        let visiveis = 0;

        linhas.forEach((linha) => {
            const corresponde =
                linha.dataset.nome.includes(termo) || linha.dataset.email.includes(termo);
            linha.classList.toggle("hidden", !corresponde);
            if (corresponde) visiveis += 1;
        });

        semResultado.classList.toggle("hidden", visiveis !== 0 || linhas.length === 0);
    }

    // ---------------------------------------------------------------
    // Ligação dos eventos
    // ---------------------------------------------------------------

    document.getElementById("btnNovoUtilizador").addEventListener("click", prepararModoCriar);
    document.getElementById("btnFecharModalUtilizador").addEventListener("click", fecharModal);
    document.getElementById("btnCancelarUtilizador").addEventListener("click", fecharModal);
    overlay.addEventListener("click", fecharModal);

    document.getElementById("btnCancelarEliminar").addEventListener("click", fecharConfirmacaoEliminar);
    overlayEliminar.addEventListener("click", fecharConfirmacaoEliminar);
    document.getElementById("btnConfirmarEliminar").addEventListener("click", confirmarEliminar);

    const pesquisaInput = document.getElementById("pesquisaUtilizador");
    if (pesquisaInput) pesquisaInput.addEventListener("input", aplicarPesquisa);

    document.getElementById("tabelaUtilizadores").addEventListener("click", function (evento) {
        const botao = evento.target.closest("button[data-action]");
        if (!botao) return;

        const acao = botao.dataset.action;
        const id = botao.dataset.id;

        if (acao === "editar") prepararModoEditar(id);
        if (acao === "status") alternarStatus(id);
        if (acao === "eliminar") abrirConfirmacaoEliminar(id, botao.dataset.nome);
    });

    document.addEventListener("keydown", function (evento) {
        if (evento.key !== "Escape") return;
        if (!modal.classList.contains("hidden")) fecharModal();
        if (!modalEliminar.classList.contains("hidden")) fecharConfirmacaoEliminar();
    });
})();
