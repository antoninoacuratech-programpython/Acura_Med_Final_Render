// static/js/modules/meus_atendimentos.js

const MEUS_ATENDIMENTOS_URLS = {
    fila: "/modulos/meus_atendimentos/fila/",
    iniciar: (id) => `/modulos/atendimento/${id}/iniciar/`,
    ficha: (id) => `/modulos/meus_atendimentos/ficha/${id}/`,
    cadastrarConsulta: (atendimentoId) => `/modulos/atendimento/${atendimentoId}/consulta/`,
    cadastrarPrescricao: "/modulos/prescricoes/cadastrar/",
};

// O mesmo script serve tanto a fila (lista) como a ficha (formulário) —
// initModule chama sempre este initializer, por isso ele decide o que
// inicializar consoante o que encontra no DOM.
window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.meus_atendimentos = function () {
    if (document.getElementById("meus-atendimentos-body")) {
        carregarMeusAtendimentos();
    }
    if (document.getElementById("form-ficha-atendimento")) {
        initFichaAtendimento();
    }
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

// -------------------------------------------------------------------------
// FILA
// -------------------------------------------------------------------------

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
                    : `<button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="atenderPaciente(${a.id})">Atender</button>`;

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

// Atender: marca em_atendimento e navega para a Ficha completa (não é modal).
async function atenderPaciente(atendimentoId) {
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

        window.loadModule("meus_atendimentos", "Ficha de Atendimento", {
            url: MEUS_ATENDIMENTOS_URLS.ficha(atendimentoId),
        });
    } catch (e) {
        window.showToast?.("Falha de conexão ao iniciar atendimento.", "error");
    }
}

// -------------------------------------------------------------------------
// FICHA DE ATENDIMENTO
// -------------------------------------------------------------------------

function initFichaAtendimento() {
    // Mostra o painel da conduta já seleccionada (caso seja um rascunho
    // reaberto) e garante pelo menos uma linha de medicamento se a
    // conduta já for Prescrição.
    const marcado = document.querySelector('input[name="conduta"]:checked');
    if (marcado) {
        mudarConduta(marcado.value);
        if (marcado.value === "PRESCRICAO" && !document.getElementById("itens-prescricao-ficha").children.length) {
            adicionarLinhaPrescricaoFicha();
        }
    }
}

function mudarConduta(valor) {
    ["SOLICITAR_EXAME", "INTERNAR", "ALTA", "PRESCRICAO"].forEach((c) => {
        document.getElementById(`painel-conduta-${c}`)?.classList.toggle("hidden", c !== valor);
    });

    if (valor === "PRESCRICAO" && !document.getElementById("itens-prescricao-ficha").children.length) {
        adicionarLinhaPrescricaoFicha();
    }
}

function adicionarLinhaPrescricaoFicha() {
    const template = document.getElementById("template-linha-prescricao-ficha");
    const clone = template.content.cloneNode(true);
    document.getElementById("itens-prescricao-ficha").appendChild(clone);
}

async function guardarFicha(finalizar) {
    const form = document.getElementById("form-ficha-atendimento");
    const erroEl = document.getElementById("modalErroFicha");
    const atendimentoId = form.dataset.atendimentoId;
    erroEl.classList.add("hidden");

    const condutaSelecionada = document.querySelector('input[name="conduta"]:checked')?.value || "";

    if (finalizar && !condutaSelecionada) {
        erroEl.textContent = "Selecione uma conduta antes de finalizar o atendimento.";
        erroEl.classList.remove("hidden");
        return;
    }

    // Se a conduta for Prescrição e for finalizar, a receita tem de ir
    // primeiro — só finalizamos a consulta depois de a farmácia já ter
    // a receita, para nunca fechar um atendimento sem a receita enviada.
    if (finalizar && condutaSelecionada === "PRESCRICAO") {
        if (!document.getElementById("itens-prescricao-ficha").children.length) {
            erroEl.textContent = "Adicione pelo menos um medicamento antes de finalizar.";
            erroEl.classList.remove("hidden");
            return;
        }

        const dadosPrescricao = new FormData();
        dadosPrescricao.append("prescricao_atendimento_id", atendimentoId);
        dadosPrescricao.append("prescricao_observacoes", form.observacoes_condutas.value);

        document.querySelectorAll("#itens-prescricao-ficha select[name='item_medicamento_id[]']").forEach((el) => dadosPrescricao.append("item_medicamento_id[]", el.value));
        document.querySelectorAll("#itens-prescricao-ficha input[name='item_dosagem[]']").forEach((el) => dadosPrescricao.append("item_dosagem[]", el.value));
        document.querySelectorAll("#itens-prescricao-ficha select[name='item_via[]']").forEach((el) => dadosPrescricao.append("item_via[]", el.value));
        document.querySelectorAll("#itens-prescricao-ficha input[name='item_frequencia[]']").forEach((el) => dadosPrescricao.append("item_frequencia[]", el.value));
        document.querySelectorAll("#itens-prescricao-ficha input[name='item_duracao_dias[]']").forEach((el) => dadosPrescricao.append("item_duracao_dias[]", el.value));
        document.querySelectorAll("#itens-prescricao-ficha input[name='item_quantidade[]']").forEach((el) => dadosPrescricao.append("item_quantidade[]", el.value));

        try {
            const respostaPrescricao = await fetch(MEUS_ATENDIMENTOS_URLS.cadastrarPrescricao, {
                method: "POST",
                headers: { "X-CSRFToken": meusAtendimentosCsrfToken() },
                body: dadosPrescricao,
            });
            const resultadoPrescricao = await respostaPrescricao.json();

            if (!respostaPrescricao.ok || !resultadoPrescricao.ok) {
                erroEl.textContent = resultadoPrescricao.erro || "Erro ao enviar a receita à farmácia.";
                erroEl.classList.remove("hidden");
                return; // não finaliza a consulta se a receita falhar
            }
        } catch (e) {
            erroEl.textContent = "Falha de conexão ao enviar a receita.";
            erroEl.classList.remove("hidden");
            return;
        }
    }

    const dadosConsulta = new FormData(form);
    dadosConsulta.set("finalizar", finalizar ? "1" : "0");

    try {
        const resposta = await fetch(MEUS_ATENDIMENTOS_URLS.cadastrarConsulta(atendimentoId), {
            method: "POST",
            headers: { "X-CSRFToken": meusAtendimentosCsrfToken() },
            body: dadosConsulta,
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            erroEl.textContent = resultado.erro || "Erro ao guardar a ficha.";
            erroEl.classList.remove("hidden");
            return;
        }

        window.showToast?.(resultado.mensagem);

        if (finalizar) {
            window.loadModule("meus_atendimentos", "Meus Atendimentos");
        }
    } catch (e) {
        erroEl.textContent = "Falha de conexão. Tente novamente.";
        erroEl.classList.remove("hidden");
    }
}