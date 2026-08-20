// static/js/modules/internamento.js

const INTERNAMENTO_URLS = {
    naveCadastrar: "/modulos/internamento/naves/cadastrar/",
    naveEliminar: (id) => `/modulos/internamento/naves/${id}/eliminar/`,
    quartoCadastrar: "/modulos/internamento/quartos/cadastrar/",
    quartoEliminar: (id) => `/modulos/internamento/quartos/${id}/eliminar/`,
    internados: "/modulos/internamento/internados/",
    darAlta: (id) => `/modulos/internamento/${id}/alta/`,
    evolucoes: (internamentoId) => `/modulos/internamento/${internamentoId}/evolucoes/`,
    cadastrarEvolucao: (internamentoId) => `/modulos/internamento/${internamentoId}/evolucoes/cadastrar/`,
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
                    <button class="bg-purple-600 hover:bg-purple-700 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="abrirPrescricaoExameInternamento(${i.atendimento_id}, '${i.paciente.replace(/'/g, "\\'")}')">Prescrever / Exame</button>
                    <button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="abrirEvolucao(${i.id}, '${i.paciente.replace(/'/g, "\\'")}')">Evolução</button>
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

// -------------------------------------------------------------------------
// Nova Requisição de Medicamentos à Farmácia
// -------------------------------------------------------------------------

function openRequisicaoInternaModal() {
    document.getElementById("form-requisicao-interna").reset();
    document.getElementById("itens-requisicao-interna").innerHTML = "";
    document.getElementById("modalErroRequisicaoInterna").classList.add("hidden");
    adicionarLinhaRequisicaoInterna();
    document.getElementById("modal-requisicao-interna").classList.remove("hidden");
}

function closeRequisicaoInternaModal() {
    document.getElementById("modal-requisicao-interna").classList.add("hidden");
}

function adicionarLinhaRequisicaoInterna() {
    const template = document.getElementById("template-linha-requisicao-interna");
    const clone = template.content.cloneNode(true);
    document.getElementById("itens-requisicao-interna").appendChild(clone);
}

async function submitRequisicaoInterna(event) {
    event.preventDefault();
    const erroEl = document.getElementById("modalErroRequisicaoInterna");
    erroEl.classList.add("hidden");

    if (!document.getElementById("itens-requisicao-interna").children.length) {
        erroEl.textContent = "Adicione pelo menos um medicamento.";
        erroEl.classList.remove("hidden");
        return;
    }

    const dados = await internamentoEnviar("/modulos/farmacia/requisicoes/cadastrar/", new FormData(event.target));

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeRequisicaoInternaModal();
}

// -------------------------------------------------------------------------
// Evolução Clínica
// -------------------------------------------------------------------------

let evolucaoInternamentoId = null;

const EVOLUCAO_CORES = {
    MEDICA: "border-blue-200 bg-blue-50/40",
    ENFERMAGEM: "border-teal-200 bg-teal-50/40",
    OUTRA: "border-gray-200 bg-gray-50/40",
};

function abrirEvolucao(internamentoId, nomePaciente) {
    evolucaoInternamentoId = internamentoId;
    document.getElementById("evolucao-paciente-nome").textContent = nomePaciente;
    document.getElementById("evolucao-texto").value = "";
    document.getElementById("modalErroEvolucao").classList.add("hidden");
    document.getElementById("modal-evolucao").classList.remove("hidden");
    carregarEvolucoes();
}

function closeEvolucaoModal() {
    document.getElementById("modal-evolucao").classList.add("hidden");
    evolucaoInternamentoId = null;
}

async function carregarEvolucoes() {
    const timeline = document.getElementById("evolucao-timeline");
    timeline.innerHTML = `<p class="text-center text-gray-400 py-6">A carregar...</p>`;

    try {
        const resposta = await fetch(INTERNAMENTO_URLS.evolucoes(evolucaoInternamentoId));
        const dados = await resposta.json();

        if (!dados.ok || dados.evolucoes.length === 0) {
            timeline.innerHTML = `<p class="text-center text-gray-400 py-6">Ainda sem notas de evolução.</p>`;
            return;
        }

        timeline.innerHTML = dados.evolucoes.map((e) => `
            <div class="border ${EVOLUCAO_CORES[e.tipo] || "border-gray-200"} rounded-xl p-3">
                <div class="flex items-center justify-between mb-1">
                    <span class="text-xs font-bold text-gray-700">${e.tipo_display}</span>
                    <span class="text-xs text-gray-400">${internamentoFormatarDataHora(e.criado_em)}</span>
                </div>
                <p class="text-sm text-gray-700">${e.texto}</p>
                <p class="text-xs text-gray-400 mt-1">— ${e.profissional}</p>
            </div>
        `).join("");
    } catch (erro) {
        timeline.innerHTML = `<p class="text-center text-gray-400 py-6">Erro ao carregar evolução.</p>`;
    }
}

async function submitEvolucao() {
    const erroEl = document.getElementById("modalErroEvolucao");
    erroEl.classList.add("hidden");

    const texto = document.getElementById("evolucao-texto").value.trim();
    if (!texto) {
        erroEl.textContent = "Escreva a nota de evolução antes de guardar.";
        erroEl.classList.remove("hidden");
        return;
    }

    const formData = new FormData();
    formData.append("evolucao_tipo", document.getElementById("evolucao-tipo").value);
    formData.append("evolucao_texto", texto);

    const dados = await internamentoEnviar(INTERNAMENTO_URLS.cadastrarEvolucao(evolucaoInternamentoId), formData);

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    document.getElementById("evolucao-texto").value = "";
    carregarEvolucoes();
}

// -------------------------------------------------------------------------
// Prescrever / Solicitar Exame durante o Internamento
// -------------------------------------------------------------------------

let peiAtendimentoId = null;

function abrirPrescricaoExameInternamento(atendimentoId, nomePaciente) {
    peiAtendimentoId = atendimentoId;
    document.getElementById("pei-paciente-nome").textContent = nomePaciente;
    document.getElementById("itens-prescricao-internamento").innerHTML = "";
    document.getElementById("itens-exame-internamento").innerHTML = "";
    document.getElementById("modalErroPrescricaoInternamento").classList.add("hidden");
    document.getElementById("modalErroExameInternamento").classList.add("hidden");
    adicionarLinhaPrescricaoInternamento();
    adicionarLinhaExameInternamento();
    document.getElementById("modal-prescricao-exame-internamento").classList.remove("hidden");
}

function closePrescricaoExameInternamentoModal() {
    document.getElementById("modal-prescricao-exame-internamento").classList.add("hidden");
    peiAtendimentoId = null;
}

function adicionarLinhaPrescricaoInternamento() {
    const template = document.getElementById("template-linha-prescricao-internamento");
    document.getElementById("itens-prescricao-internamento").appendChild(template.content.cloneNode(true));
}

function adicionarLinhaExameInternamento() {
    const template = document.getElementById("template-linha-exame-internamento");
    document.getElementById("itens-exame-internamento").appendChild(template.content.cloneNode(true));
}

async function submitPrescricaoInternamento() {
    const erroEl = document.getElementById("modalErroPrescricaoInternamento");
    erroEl.classList.add("hidden");

    if (!document.getElementById("itens-prescricao-internamento").children.length) {
        erroEl.textContent = "Adicione pelo menos um medicamento.";
        erroEl.classList.remove("hidden");
        return;
    }

    const formData = new FormData();
    formData.append("prescricao_atendimento_id", peiAtendimentoId);
    document.querySelectorAll("#itens-prescricao-internamento select[name='item_medicamento_id[]']").forEach((el) => formData.append("item_medicamento_id[]", el.value));
    document.querySelectorAll("#itens-prescricao-internamento input[name='item_dosagem[]']").forEach((el) => formData.append("item_dosagem[]", el.value));
    document.querySelectorAll("#itens-prescricao-internamento input[name='item_frequencia[]']").forEach((el) => formData.append("item_frequencia[]", el.value));
    document.querySelectorAll("#itens-prescricao-internamento input[name='item_quantidade[]']").forEach((el) => formData.append("item_quantidade[]", el.value));

    const dados = await internamentoEnviar("/modulos/prescricoes/cadastrar/", formData);

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    document.getElementById("itens-prescricao-internamento").innerHTML = "";
    adicionarLinhaPrescricaoInternamento();
}

async function submitExameInternamento() {
    const erroEl = document.getElementById("modalErroExameInternamento");
    erroEl.classList.add("hidden");

    if (!document.getElementById("itens-exame-internamento").children.length) {
        erroEl.textContent = "Adicione pelo menos um exame.";
        erroEl.classList.remove("hidden");
        return;
    }

    const formData = new FormData();
    formData.append("solicitacao_atendimento_id", peiAtendimentoId);
    document.querySelectorAll("#itens-exame-internamento select[name='item_tipo_exame_id[]']").forEach((el) => formData.append("item_tipo_exame_id[]", el.value));

    const dados = await internamentoEnviar("/modulos/laboratorio/solicitacoes/cadastrar/", formData);

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    document.getElementById("itens-exame-internamento").innerHTML = "";
    adicionarLinhaExameInternamento();
}