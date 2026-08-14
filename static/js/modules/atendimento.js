// static/js/modules/atendimento.js

const ATENDIMENTO_URLS = {
    cadastrar: "/modulos/atendimento/cadastrar/",
    checkin: (agendamentoId) => `/modulos/atendimento/checkin/${agendamentoId}/`,
    fila: "/modulos/atendimento/fila/",
    buscarPacientes: "/modulos/pacientes/buscar/",
    buscarEntidades: "/modulos/pacientes/entidades/buscar/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.atendimento = function () {
    carregarFilaAtendimento();
};

function atendimentoCsrfToken() {
    const nome = "csrftoken=";
    const partes = document.cookie.split(";");
    for (let parte of partes) {
        parte = parte.trim();
        if (parte.startsWith(nome)) return decodeURIComponent(parte.substring(nome.length));
    }
    return "";
}

// -------------------------------------------------------------------------
// Modal: abrir / fechar / alternar plano
// -------------------------------------------------------------------------

function openAtendimentoModal() {
    const form = document.getElementById("form-novo-atendimento");
    form.reset();
    document.getElementById("atendimento-paciente-codigo").value = "";
    document.getElementById("entidadeSelecionada").value = "";
    document.getElementById("selected-patient-card").classList.add("hidden");
    document.getElementById("modalErroAtendimento").classList.add("hidden");
    togglePlanoOptions();
    document.getElementById("modal-atendimento").classList.remove("hidden");
}

function closeAtendimentoModal() {
    document.getElementById("modal-atendimento").classList.add("hidden");
}

function togglePlanoOptions() {
    const convenio = document.querySelector('input[name="tipo_plano"]:checked')?.value === "convenio";
    document.getElementById("convenio-options").classList.toggle("hidden", !convenio);
}

// -------------------------------------------------------------------------
// Pesquisa de paciente (real)
// -------------------------------------------------------------------------

let atendimentoDebouncePaciente;

function filterPatients(termo) {
    const drop = document.getElementById("patient-dropdown");
    document.getElementById("atendimento-paciente-codigo").value = "";
    clearTimeout(atendimentoDebouncePaciente);

    if (!termo.trim()) {
        drop.classList.add("hidden");
        return;
    }

    atendimentoDebouncePaciente = setTimeout(async () => {
        try {
            const resposta = await fetch(`${ATENDIMENTO_URLS.buscarPacientes}?q=${encodeURIComponent(termo)}`, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
            });
            const dados = await resposta.json();
            const pacientes = dados.ok ? dados.pacientes : [];

            drop.innerHTML = pacientes.length
                ? pacientes.map((p) => `
                    <div class="px-4 py-2.5 hover:bg-orange-50 cursor-pointer text-sm text-gray-700 border-b border-gray-50" data-codigo="${p.codigo}" data-nome="${p.nome.replace(/"/g, "&quot;")}">
                        <span class="font-medium">${p.nome}</span> <span class="text-xs text-gray-400 block">${p.codigo}${p.responsavel ? " — Resp: " + p.responsavel : ""}</span>
                    </div>`).join("")
                : `<div class="px-4 py-3 text-sm text-gray-400">Nenhum paciente encontrado</div>`;

            drop.querySelectorAll("[data-codigo]").forEach((el) => {
                el.onclick = () => selectPatient(el.dataset.codigo, el.dataset.nome);
            });

            drop.classList.remove("hidden");
        } catch (e) {
            drop.classList.add("hidden");
        }
    }, 250);
}

function selectPatient(codigo, nome) {
    document.getElementById("atendimento-paciente-codigo").value = codigo;
    document.getElementById("input-search-paciente").value = nome;
    document.getElementById("selected-patient-name").textContent = nome;
    document.getElementById("selected-patient-card").classList.remove("hidden");
    document.getElementById("patient-dropdown").classList.add("hidden");
}

function clearSelectedPatient() {
    document.getElementById("atendimento-paciente-codigo").value = "";
    document.getElementById("input-search-paciente").value = "";
    document.getElementById("selected-patient-card").classList.add("hidden");
}

// -------------------------------------------------------------------------
// Pesquisa de entidade vinculada (mesmo endpoint já usado no Paciente)
// -------------------------------------------------------------------------

let atendimentoDebounceEntidade;

document.addEventListener("input", (e) => {
    if (e.target && e.target.id === "inputPesquisaEntidade") {
        const input = e.target;
        const drop = document.getElementById("dropdownEntidades");
        const hidden = document.getElementById("entidadeSelecionada");
        const termo = input.value.trim();

        hidden.value = "";
        clearTimeout(atendimentoDebounceEntidade);

        if (!termo) {
            drop.classList.add("hidden");
            return;
        }

        atendimentoDebounceEntidade = setTimeout(async () => {
            try {
                const resposta = await fetch(`${ATENDIMENTO_URLS.buscarEntidades}?q=${encodeURIComponent(termo)}`, {
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                });
                const dados = await resposta.json();
                const entidades = dados.ok ? dados.entidades : [];

                drop.innerHTML = entidades.length
                    ? entidades.map((x) => `
                        <div class="px-4 py-2.5 hover:bg-orange-50 cursor-pointer text-sm flex justify-between" data-id="${x.id}" data-nome="${x.nome.replace(/"/g, "&quot;")}">
                            <span class="font-medium">${x.nome}</span>
                            <span class="text-xs text-orange-600">${x.tipo}</span>
                        </div>`).join("")
                    : `<div class="px-4 py-3 text-sm text-gray-400">Nenhuma entidade encontrada</div>`;

                drop.querySelectorAll("[data-id]").forEach((el) => {
                    el.onclick = () => {
                        input.value = el.dataset.nome;
                        hidden.value = el.dataset.id;
                        drop.classList.add("hidden");
                    };
                });

                drop.classList.remove("hidden");
            } catch (e) {
                drop.classList.add("hidden");
            }
        }, 250);
    }
});

document.addEventListener("click", (e) => {
    const drop = document.getElementById("dropdownEntidades");
    const input = document.getElementById("inputPesquisaEntidade");
    if (drop && !drop.contains(e.target) && e.target !== input) drop.classList.add("hidden");

    const dropP = document.getElementById("patient-dropdown");
    const inputP = document.getElementById("input-search-paciente");
    if (dropP && !dropP.contains(e.target) && e.target !== inputP) dropP.classList.add("hidden");
});

// -------------------------------------------------------------------------
// Submeter novo atendimento
// -------------------------------------------------------------------------

async function submitAtendimento(event) {
    event.preventDefault();

    const form = document.getElementById("form-novo-atendimento");
    const erroEl = document.getElementById("modalErroAtendimento");
    const btn = document.getElementById("btnSalvarAtendimento");
    erroEl.classList.add("hidden");

    if (!document.getElementById("atendimento-paciente-codigo").value) {
        erroEl.textContent = "Selecione um paciente.";
        erroEl.classList.remove("hidden");
        return;
    }

    btn.disabled = true;
    btn.classList.add("opacity-60", "cursor-not-allowed");

    try {
        const resposta = await fetch(ATENDIMENTO_URLS.cadastrar, {
            method: "POST",
            headers: { "X-CSRFToken": atendimentoCsrfToken() },
            body: new FormData(form),
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            erroEl.textContent = resultado.erro || "Erro ao registar atendimento.";
            erroEl.classList.remove("hidden");
            return;
        }

        closeAtendimentoModal();
        window.showToast?.(resultado.mensagem || "Atendimento registado.");
        carregarFilaAtendimento();
    } catch (e) {
        erroEl.textContent = "Falha de conexão. Tente novamente.";
        erroEl.classList.remove("hidden");
    } finally {
        btn.disabled = false;
        btn.classList.remove("opacity-60", "cursor-not-allowed");
    }
}

// -------------------------------------------------------------------------
// Fila do dia
// -------------------------------------------------------------------------

const ATENDIMENTO_BADGES = {
    aguardando: "bg-blue-50 text-blue-600",
    em_atendimento: "bg-amber-50 text-amber-600",
    concluido: "bg-teal-50 text-teal-600",
    cancelado: "bg-gray-100 text-gray-500",
    aguardando_chegada: "bg-pink-50 text-pink-600",
};

async function carregarFilaAtendimento() {
    const corpo = document.getElementById("fila-atendimento-body");
    if (!corpo) return;

    try {
        const resposta = await fetch(ATENDIMENTO_URLS.fila, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const dados = await resposta.json();
        const fila = dados.ok ? dados.fila : [];

        atualizarCartoesFila(fila);

        corpo.innerHTML = fila.length
            ? fila.map((item) => {
                const badgeClasse = ATENDIMENTO_BADGES[item.status] || "bg-gray-100 text-gray-500";
                const acao = item.tipo === "agendamento_pendente"
                    ? `<button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="fazerCheckin(${item.id})">Check-in</button>`
                    : `<button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm">Atender</button>`;

                return `
                    <tr class="hover:bg-gray-50/50 transition" data-search="${item.paciente.toLowerCase()} ${item.paciente_codigo.toLowerCase()}">
                        <td class="py-4 px-4 font-medium">${item.paciente}</td>
                        <td class="py-4 px-4 text-gray-500">${item.profissional || "—"}</td>
                        <td class="py-4 px-4 text-gray-500">${item.prioridade || "—"}</td>
                        <td class="py-4 px-4"><span class="${badgeClasse} text-xs font-medium px-3 py-1 rounded-full">${item.status_display}</span></td>
                        <td class="py-4 px-4 text-right">${acao}</td>
                    </tr>`;
            }).join("")
            : `<tr><td class="py-6 px-4 text-center text-gray-400" colspan="5">Ninguém na fila hoje.</td></tr>`;
    } catch (e) {
        corpo.innerHTML = `<tr><td class="py-6 px-4 text-center text-gray-400" colspan="5">Erro ao carregar a fila.</td></tr>`;
    }
}

function atualizarCartoesFila(fila) {
    const contar = (status) => fila.filter((i) => i.status === status).length;
    document.getElementById("stat-aguardando").textContent = contar("aguardando");
    document.getElementById("stat-em-atendimento").textContent = contar("em_atendimento");
    document.getElementById("stat-concluidos").textContent = contar("concluido");
    document.getElementById("stat-aguardando-chegada").textContent = contar("aguardando_chegada");
}

function filterFilaAtendimento(termo) {
    const alvo = termo.trim().toLowerCase();
    document.querySelectorAll("#fila-atendimento-body tr[data-search]").forEach((linha) => {
        linha.style.display = linha.dataset.search.includes(alvo) ? "" : "none";
    });
}

async function fazerCheckin(agendamentoId) {
    try {
        const resposta = await fetch(ATENDIMENTO_URLS.checkin(agendamentoId), {
            method: "POST",
            headers: { "X-CSRFToken": atendimentoCsrfToken() },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            window.showToast?.(resultado.erro || "Erro ao fazer check-in.", "error");
            return;
        }

        window.showToast?.(resultado.mensagem);
        carregarFilaAtendimento();
    } catch (e) {
        window.showToast?.("Falha de conexão ao fazer check-in.", "error");
    }
}