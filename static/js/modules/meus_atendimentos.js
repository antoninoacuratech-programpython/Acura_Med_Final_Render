// static/js/modules/meus_atendimentos.js

const MEUS_ATENDIMENTOS_URLS = {
    fila: "/modulos/meus_atendimentos/fila/",
    iniciar: (id) => `/modulos/atendimento/${id}/iniciar/`,
    concluir: (id) => `/modulos/atendimento/${id}/concluir/`,
    cadastrarPrescricao: "/modulos/prescricoes/cadastrar/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.meus_atendimentos = function () {
    carregarMeusAtendimentos();
};

function meusAtendimentosCsrfToken() {
    const nome = "csrftoken=";
    const partes = document.cookie.split(";");
    for (let parte of partes) {
        parte = parte.trim();
        if (parte.startsWith(nome)) return decodeURIComponent(parte.substring(nome.length));
    }
    return "";
}

const MEUS_ATENDIMENTOS_BADGES = {
    aguardando: "bg-blue-50 text-blue-600",
    em_atendimento: "bg-amber-50 text-amber-600",
    concluido: "bg-teal-50 text-teal-600",
};

async function carregarMeusAtendimentos() {
    const corpo = document.getElementById("meus-atendimentos-body");
    if (!corpo) return;

    try {
        const resposta = await fetch(MEUS_ATENDIMENTOS_URLS.fila, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const dados = await resposta.json();
        const lista = dados.ok ? dados.atendimentos : [];

        corpo.innerHTML = lista.length
            ? lista.map((a) => {
                const badge = MEUS_ATENDIMENTOS_BADGES[a.status] || "bg-gray-100 text-gray-500";
                const acao = a.status === "concluido"
                    ? `<span class="text-xs text-gray-400">Concluído</span>`
                    : `<button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="atenderPaciente(${a.id}, '${a.paciente.replace(/'/g, "\\'")}')">Atender</button>`;

                return `
                    <tr class="hover:bg-gray-50/50 transition" data-search="${a.paciente.toLowerCase()} ${a.paciente_codigo.toLowerCase()}">
                        <td class="py-4 px-4 font-medium">${a.paciente}</td>
                        <td class="py-4 px-4 text-gray-500">${a.tipo_atendimento || "—"}</td>
                        <td class="py-4 px-4 text-gray-500">${a.prioridade || "—"}</td>
                        <td class="py-4 px-4"><span class="${badge} text-xs font-medium px-3 py-1 rounded-full">${a.status_display}</span></td>
                        <td class="py-4 px-4 text-right">${acao}</td>
                    </tr>`;
            }).join("")
            : `<tr><td class="py-6 px-4 text-center text-gray-400" colspan="5">Sem atendimentos hoje.</td></tr>`;
    } catch (e) {
        corpo.innerHTML = `<tr><td class="py-6 px-4 text-center text-gray-400" colspan="5">Erro ao carregar os atendimentos.</td></tr>`;
    }
}

function filterMeusAtendimentos(termo) {
    const alvo = termo.trim().toLowerCase();
    document.querySelectorAll("#meus-atendimentos-body tr[data-search]").forEach((linha) => {
        linha.style.display = linha.dataset.search.includes(alvo) ? "" : "none";
    });
}

// -------------------------------------------------------------------------
// Atender: marca em_atendimento e abre o modal de prescrição
// -------------------------------------------------------------------------

async function atenderPaciente(atendimentoId, nomePaciente) {
    try {
        const resposta = await fetch(MEUS_ATENDIMENTOS_URLS.iniciar(atendimentoId), {
            method: "POST",
            headers: { "X-CSRFToken": meusAtendimentosCsrfToken() },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            window.showToast?.(resultado.erro || "Erro ao iniciar atendimento.", "error");
            return;
        }

        carregarMeusAtendimentos();
        openPrescricaoModal(atendimentoId, nomePaciente);
    } catch (e) {
        window.showToast?.("Falha de conexão ao iniciar atendimento.", "error");
    }
}

// -------------------------------------------------------------------------
// Modal de prescrição
// -------------------------------------------------------------------------

function openPrescricaoModal(atendimentoId, nomePaciente) {
    document.getElementById("prescricao-paciente-nome").textContent = nomePaciente;
    document.getElementById("prescricao-atendimento-id").value = atendimentoId;
    document.getElementById("itens-prescricao").innerHTML = "";
    document.getElementById("modalErroPrescricao").classList.add("hidden");
    document.getElementById("form-prescricao").reset();
    document.getElementById("prescricao-atendimento-id").value = atendimentoId; // reset() limpa o hidden também

    adicionarLinhaPrescricao(); // começa sempre com uma linha pronta

    document.getElementById("modal-prescricao").classList.remove("hidden");
}

function closePrescricaoModal() {
    document.getElementById("modal-prescricao").classList.add("hidden");
}

function adicionarLinhaPrescricao() {
    const template = document.getElementById("template-linha-prescricao");
    const clone = template.content.cloneNode(true);
    document.getElementById("itens-prescricao").appendChild(clone);
}

async function submitPrescricao(event) {
    event.preventDefault();

    const form = document.getElementById("form-prescricao");
    const erroEl = document.getElementById("modalErroPrescricao");
    const btn = document.getElementById("btnEnviarPrescricao");
    erroEl.classList.add("hidden");

    if (!document.getElementById("itens-prescricao").children.length) {
        erroEl.textContent = "Adicione pelo menos um medicamento.";
        erroEl.classList.remove("hidden");
        return;
    }

    btn.disabled = true;
    btn.classList.add("opacity-60", "cursor-not-allowed");

    try {
        const resposta = await fetch(MEUS_ATENDIMENTOS_URLS.cadastrarPrescricao, {
            method: "POST",
            headers: { "X-CSRFToken": meusAtendimentosCsrfToken() },
            body: new FormData(form),
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            erroEl.textContent = resultado.erro || "Erro ao enviar prescrição.";
            erroEl.classList.remove("hidden");
            return;
        }

        window.showToast?.(resultado.mensagem || "Prescrição enviada à farmácia.");

        // Consulta terminada: fecha o modal e marca o atendimento como concluído.
        const atendimentoId = document.getElementById("prescricao-atendimento-id").value;
        await fetch(MEUS_ATENDIMENTOS_URLS.concluir(atendimentoId), {
            method: "POST",
            headers: { "X-CSRFToken": meusAtendimentosCsrfToken() },
        });

        closePrescricaoModal();
        carregarMeusAtendimentos();
    } catch (e) {
        erroEl.textContent = "Falha de conexão. Tente novamente.";
        erroEl.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        btn.classList.remove("opacity-60", "cursor-not-allowed");
    }
}