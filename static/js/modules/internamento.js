// static/js/modules/internamento.js

const INTERNAMENTO_URLS = {
    naveCadastrar: "/modulos/internamento/naves/cadastrar/",
    naveEliminar: (id) => `/modulos/internamento/naves/${id}/eliminar/`,
    quartoCadastrar: "/modulos/internamento/quartos/cadastrar/",
    quartoEliminar: (id) => `/modulos/internamento/quartos/${id}/eliminar/`,
    internados: "/modulos/internamento/internados/",
    darAlta: (id) => `/modulos/internamento/${id}/alta/`,
    modulo: "/modulos/internamento/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.internamento = function () {
    atualizarBadgeInternados();
};

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

// -------------------------------------------------------------------------
// Internados (lista + Dar Alta)
// -------------------------------------------------------------------------

function internamentoFormatarDataHora(isoString) {
    if (!isoString) return "—";
    const data = new Date(isoString);
    return data.toLocaleString("pt-PT", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

async function atualizarBadgeInternados() {
    try {
        const resposta = await fetch(INTERNAMENTO_URLS.internados);
        const dados = await resposta.json();
        const badge = document.getElementById("internados-badge");
        if (!badge) return;

        const total = dados.ok ? dados.internamentos.length : 0;
        badge.textContent = total;
        badge.classList.toggle("hidden", total === 0);
    } catch (erro) {
        // silencioso
    }
}

function openInternadosModal() {
    document.getElementById("modal-internados").classList.remove("hidden");
    document.getElementById("input-search-internados").value = "";
    carregarInternados();
}

function closeInternadosModal() {
    document.getElementById("modal-internados").classList.add("hidden");
}

async function carregarInternados() {
    const corpo = document.getElementById("internados-body");
    corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(INTERNAMENTO_URLS.internados);
        const dados = await resposta.json();

        if (!dados.ok || dados.internamentos.length === 0) {
            corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Ninguém internado neste momento.</td></tr>`;
            return;
        }

        corpo.innerHTML = dados.internamentos.map((i) => `
            <tr class="hover:bg-gray-50/50 transition" data-search="${i.paciente.toLowerCase()} ${i.paciente_codigo.toLowerCase()} ${(i.bi || "").toLowerCase()}">
                <td class="py-4 px-4 font-medium">${i.paciente}</td>
                <td class="py-4 px-4 text-gray-500">${i.bi || "—"}</td>
                <td class="py-4 px-4 text-gray-500">${i.nave} — Quarto ${i.quarto}</td>
                <td class="py-4 px-4 text-gray-500">${i.medico}</td>
                <td class="py-4 px-4 text-gray-500 whitespace-nowrap">${internamentoFormatarDataHora(i.data_entrada)}</td>
                <td class="py-4 px-4 text-right">
                    <button class="bg-teal-600 hover:bg-teal-700 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="confirmarAlta(${i.id}, '${i.paciente.replace(/'/g, "\\'")}')">Dar Alta</button>
                </td>
            </tr>
        `).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Erro ao carregar internados.</td></tr>`;
    }
}

function filterInternados(termo) {
    const alvo = termo.trim().toLowerCase();
    document.querySelectorAll("#internados-body tr[data-search]").forEach((linha) => {
        linha.style.display = linha.dataset.search.includes(alvo) ? "" : "none";
    });
}

async function confirmarAlta(id, nome) {
    if (!confirm(`Confirmar alta de ${nome}? O quarto ficará com uma vaga livre.`)) return;

    const dados = await internamentoEnviar(INTERNAMENTO_URLS.darAlta(id), new FormData());

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    carregarInternados();
    atualizarBadgeInternados();
    internamentoRecarregarPainel();
}