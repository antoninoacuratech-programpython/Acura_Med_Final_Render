// static/js/modules/triagem.js

const TRIAGEM_URLS = {
    fila: "/modulos/triagem/fila/",
    salvar: (id) => `/modulos/atendimento/${id}/sinais-vitais/`,
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.triagem = function () {
    carregarFilaTriagem();
};

function triagemCsrfToken() {
    const nome = "csrftoken=";
    const partes = document.cookie.split(";");
    for (let parte of partes) {
        parte = parte.trim();
        if (parte.startsWith(nome)) return decodeURIComponent(parte.substring(nome.length));
    }
    return "";
}

async function carregarFilaTriagem() {
    const corpo = document.getElementById("triagem-body");
    if (!corpo) return;

    try {
        const resposta = await fetch(TRIAGEM_URLS.fila, { headers: { "X-Requested-With": "XMLHttpRequest" } });
        const dados = await resposta.json();
        const lista = dados.ok ? dados.atendimentos : [];

        corpo.innerHTML = lista.length
            ? lista.map((a) => {
                const badge = a.sinais_preenchidos
                    ? `<span class="bg-teal-50 text-teal-600 text-xs font-medium px-3 py-1 rounded-full">Registados</span>`
                    : `<span class="bg-amber-50 text-amber-600 text-xs font-medium px-3 py-1 rounded-full">Pendente</span>`;

                return `
                    <tr class="hover:bg-gray-50/50 transition" data-search="${a.paciente.toLowerCase()} ${a.paciente_codigo.toLowerCase()}">
                        <td class="py-4 px-4 font-medium">${a.paciente}</td>
                        <td class="py-4 px-4 text-gray-500">${a.prioridade || "—"}</td>
                        <td class="py-4 px-4">${badge}</td>
                        <td class="py-4 px-4 text-right">
                            <button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="openSinaisVitaisModal(${a.id}, '${a.paciente.replace(/'/g, "\\'")}')">
                                ${a.sinais_preenchidos ? "Editar" : "Registar"}
                            </button>
                        </td>
                    </tr>`;
            }).join("")
            : `<tr><td class="py-6 px-4 text-center text-gray-400" colspan="4">Ninguém à espera de triagem.</td></tr>`;
    } catch (e) {
        corpo.innerHTML = `<tr><td class="py-6 px-4 text-center text-gray-400" colspan="4">Erro ao carregar a fila.</td></tr>`;
    }
}

function filterTriagem(termo) {
    const alvo = termo.trim().toLowerCase();
    document.querySelectorAll("#triagem-body tr[data-search]").forEach((linha) => {
        linha.style.display = linha.dataset.search.includes(alvo) ? "" : "none";
    });
}

async function openSinaisVitaisModal(atendimentoId, nomePaciente) {
    document.getElementById("sv-paciente-nome").textContent = nomePaciente;
    document.getElementById("form-sinais-vitais").reset();
    document.getElementById("sv-atendimento-id").value = atendimentoId;
    document.getElementById("modalErroSinaisVitais").classList.add("hidden");
    document.getElementById("modal-sinais-vitais").classList.remove("hidden");

    try {
        const resposta = await fetch(TRIAGEM_URLS.salvar(atendimentoId), {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const dados = await resposta.json();
        if (!dados.ok) return;

        const sv = dados.sinais_vitais;
        const form = document.getElementById("form-sinais-vitais");
        form.pressao_arterial.value = sv.pressao_arterial ?? "";
        form.frequencia_cardiaca.value = sv.frequencia_cardiaca ?? "";
        form.frequencia_respiratoria.value = sv.frequencia_respiratoria ?? "";
        form.temperatura.value = sv.temperatura ?? "";
        form.saturacao_o2.value = sv.saturacao_o2 ?? "";
        form.glicemia_capilar.value = sv.glicemia_capilar ?? "";
    } catch (e) {
        // Se a busca falhar, o modal continua aberto e vazio — o
        // enfermeiro ainda consegue preencher de novo sem problema.
    }
}

function closeSinaisVitaisModal() {
    document.getElementById("modal-sinais-vitais").classList.add("hidden");
}

async function submitSinaisVitais(event) {
    event.preventDefault();

    const form = document.getElementById("form-sinais-vitais");
    const erroEl = document.getElementById("modalErroSinaisVitais");
    const atendimentoId = document.getElementById("sv-atendimento-id").value;
    erroEl.classList.add("hidden");

    try {
        const resposta = await fetch(TRIAGEM_URLS.salvar(atendimentoId), {
            method: "POST",
            headers: { "X-CSRFToken": triagemCsrfToken() },
            body: new FormData(form),
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            erroEl.textContent = resultado.erro || "Erro ao guardar sinais vitais.";
            erroEl.classList.remove("hidden");
            return;
        }

        window.showToast?.(resultado.mensagem);
        closeSinaisVitaisModal();
        carregarFilaTriagem();
    } catch (e) {
        erroEl.textContent = "Falha de conexão. Tente novamente.";
        erroEl.classList.remove("hidden");
    }
}