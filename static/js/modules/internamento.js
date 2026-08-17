// static/js/modules/internamento.js

const INTERNAMENTO_URLS = {
    naveCadastrar: "/modulos/internamento/naves/cadastrar/",
    naveEliminar: (id) => `/modulos/internamento/naves/${id}/eliminar/`,
    quartoCadastrar: "/modulos/internamento/quartos/cadastrar/",
    quartoEliminar: (id) => `/modulos/internamento/quartos/${id}/eliminar/`,
    modulo: "/modulos/internamento/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.internamento = function () { };

function internamentoCsrfToken() {
    const nome = "csrftoken=";
    const partes = document.cookie.split(";");
    for (let parte of partes) {
        parte = parte.trim();
        if (parte.startsWith(nome)) return decodeURIComponent(parte.substring(nome.length));
    }
    return "";
}

async function internamentoEnviar(url, formData) {
    const resposta = await fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": internamentoCsrfToken() },
        body: formData,
    });
    return resposta.json();
}

async function internamentoRecarregarPainel() {
    try {
        const resposta = await fetch(INTERNAMENTO_URLS.modulo);
        const html = await resposta.text();
        const workspace = document.getElementById("workspace");
        if (workspace) {
            workspace.innerHTML = html;
            if (window.moduleInitializers && window.moduleInitializers.internamento) {
                window.moduleInitializers.internamento();
            }
        }
    } catch (erro) {
        console.error("Erro ao recarregar painel de internamento:", erro);
    }
}

// -------------------------------------------------------------------------
// Nave
// -------------------------------------------------------------------------

function openNaveModal() {
    document.getElementById("form-nave").reset();
    document.getElementById("modal-nave").classList.remove("hidden");
}

function closeNaveModal() {
    document.getElementById("modal-nave").classList.add("hidden");
}

async function submitNave(event) {
    event.preventDefault();
    const dados = await internamentoEnviar(INTERNAMENTO_URLS.naveCadastrar, new FormData(event.target));

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeNaveModal();
    internamentoRecarregarPainel();
}

async function eliminarNave(id, nome) {
    if (!confirm(`Tem a certeza que deseja eliminar a nave "${nome}"?`)) return;

    const dados = await internamentoEnviar(INTERNAMENTO_URLS.naveEliminar(id), new FormData());

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    internamentoRecarregarPainel();
}

// -------------------------------------------------------------------------
// Quarto
// -------------------------------------------------------------------------

function openQuartoModal() {
    document.getElementById("form-quarto").reset();
    document.getElementById("modal-quarto").classList.remove("hidden");
}

function closeQuartoModal() {
    document.getElementById("modal-quarto").classList.add("hidden");
}

async function submitQuarto(event) {
    event.preventDefault();
    const dados = await internamentoEnviar(INTERNAMENTO_URLS.quartoCadastrar, new FormData(event.target));

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeQuartoModal();
    internamentoRecarregarPainel();
}

async function eliminarQuarto(id, numero) {
    if (!confirm(`Tem a certeza que deseja eliminar o quarto "${numero}"?`)) return;

    const dados = await internamentoEnviar(INTERNAMENTO_URLS.quartoEliminar(id), new FormData());

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    internamentoRecarregarPainel();
}