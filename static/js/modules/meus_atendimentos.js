// static/js/modules/meus_atendimentos.js

const MEUS_ATENDIMENTOS_URLS = {
    fila: "/modulos/meus_atendimentos/fila/",
    iniciar: (id) => `/modulos/atendimento/${id}/iniciar/`,
    ficha: (id) => `/modulos/meus_atendimentos/ficha/${id}/`,
    cadastrarConsulta: (atendimentoId) => `/modulos/atendimento/${atendimentoId}/consulta/`,
    cadastrarPrescricao: "/modulos/prescricoes/cadastrar/",
    cadastrarSolicitacaoExame: "/modulos/laboratorio/solicitacoes/cadastrar/",
    resultados: "/modulos/laboratorio/resultados/",
    resultadoDetalhe: (id) => `/modulos/laboratorio/resultados/${id}/`,
    quartosDisponiveis: "/modulos/internamento/quartos/disponiveis/",
    cadastrarInternamento: "/modulos/internamento/cadastrar/",
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
    // reaberto) e garante pelo menos uma linha pronta (medicamento ou
    // exame, consoante a conduta), ou carrega os quartos se for Internar.
    const marcado = document.querySelector('input[name="conduta"]:checked');
    if (marcado) {
        mudarConduta(marcado.value);
    }
}

function mudarConduta(valor) {
    ["SOLICITAR_EXAME", "INTERNAR", "ALTA", "PRESCRICAO"].forEach((c) => {
        document.getElementById(`painel-conduta-${c}`)?.classList.toggle("hidden", c !== valor);
    });

    if (valor === "PRESCRICAO" && !document.getElementById("itens-prescricao-ficha").children.length) {
        adicionarLinhaPrescricaoFicha();
    }

    if (valor === "SOLICITAR_EXAME" && !document.getElementById("itens-exame-ficha").children.length) {
        adicionarLinhaExameFicha();
    }

    if (valor === "INTERNAR") {
        carregarQuartosDisponiveis();
    }
}

async function carregarQuartosDisponiveis() {
    const select = document.getElementById("internamento-quarto-id");
    const valorAnterior = select.value;

    try {
        const resposta = await fetch(MEUS_ATENDIMENTOS_URLS.quartosDisponiveis, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const dados = await resposta.json();

        if (!dados.ok || dados.quartos.length === 0) {
            select.innerHTML = `<option value="">Nenhum quarto com vaga disponível</option>`;
            return;
        }

        select.innerHTML = `<option value="">Seleccione...</option>` + dados.quartos.map((q) =>
            `<option value="${q.id}">${q.nave} — Quarto ${q.numero} (${q.tipo}) — ${q.vagas_disponiveis} vaga(s)</option>`
        ).join("");

        if (valorAnterior) select.value = valorAnterior;
    } catch (e) {
        select.innerHTML = `<option value="">Erro ao carregar quartos</option>`;
    }
}

function adicionarLinhaExameFicha() {
    const template = document.getElementById("template-linha-exame-ficha");
    const clone = template.content.cloneNode(true);
    document.getElementById("itens-exame-ficha").appendChild(clone);
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

    // Mesma lógica para Solicitar Exame: envia a solicitação primeiro,
    // só finaliza a consulta se isso tiver sucesso.
    if (finalizar && condutaSelecionada === "SOLICITAR_EXAME") {
        if (!document.getElementById("itens-exame-ficha").children.length) {
            erroEl.textContent = "Adicione pelo menos um exame antes de finalizar.";
            erroEl.classList.remove("hidden");
            return;
        }

        const dadosExame = new FormData();
        dadosExame.append("solicitacao_atendimento_id", atendimentoId);
        dadosExame.append("solicitacao_observacoes", form.observacoes_condutas.value);

        document.querySelectorAll("#itens-exame-ficha select[name='item_tipo_exame_id[]']").forEach((el) => dadosExame.append("item_tipo_exame_id[]", el.value));
        document.querySelectorAll("#itens-exame-ficha input[name='item_observacoes[]']").forEach((el) => dadosExame.append("item_observacoes[]", el.value));

        try {
            const respostaExame = await fetch(MEUS_ATENDIMENTOS_URLS.cadastrarSolicitacaoExame, {
                method: "POST",
                headers: { "X-CSRFToken": meusAtendimentosCsrfToken() },
                body: dadosExame,
            });
            const resultadoExame = await respostaExame.json();

            if (!respostaExame.ok || !resultadoExame.ok) {
                erroEl.textContent = resultadoExame.erro || "Erro ao enviar a solicitação ao laboratório.";
                erroEl.classList.remove("hidden");
                return;
            }
        } catch (e) {
            erroEl.textContent = "Falha de conexão ao enviar a solicitação de exame.";
            erroEl.classList.remove("hidden");
            return;
        }
    }

    // Mesma lógica para Internar: envia o internamento primeiro (com
    // verificação de vaga no backend), só finaliza a consulta se tiver
    // sucesso.
    if (finalizar && condutaSelecionada === "INTERNAR") {
        const quartoId = document.getElementById("internamento-quarto-id").value;
        if (!quartoId) {
            erroEl.textContent = "Seleccione um quarto antes de finalizar.";
            erroEl.classList.remove("hidden");
            return;
        }

        const dadosInternamento = new FormData();
        dadosInternamento.append("internamento_atendimento_id", atendimentoId);
        dadosInternamento.append("internamento_quarto_id", quartoId);
        dadosInternamento.append("internamento_motivo", document.getElementById("internamento-motivo").value);
        dadosInternamento.append("internamento_observacoes", form.observacoes_condutas.value);

        try {
            const respostaInternamento = await fetch(MEUS_ATENDIMENTOS_URLS.cadastrarInternamento, {
                method: "POST",
                headers: { "X-CSRFToken": meusAtendimentosCsrfToken() },
                body: dadosInternamento,
            });
            const resultadoInternamento = await respostaInternamento.json();

            if (!respostaInternamento.ok || !resultadoInternamento.ok) {
                erroEl.textContent = resultadoInternamento.erro || "Erro ao registar o internamento.";
                erroEl.classList.remove("hidden");
                return;
            }
        } catch (e) {
            erroEl.textContent = "Falha de conexão ao registar o internamento.";
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

// -------------------------------------------------------------------------
// Resultados de Exames (o médico consulta, só-leitura)
// -------------------------------------------------------------------------

function meusAtendimentosFormatarDataHora(isoString) {
    if (!isoString) return "—";
    const data = new Date(isoString);
    return data.toLocaleString("pt-PT", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function openResultadosModal() {
    document.getElementById("modal-resultados").classList.remove("hidden");
    carregarResultados();
}

function closeResultadosModal() {
    document.getElementById("modal-resultados").classList.add("hidden");
}

async function carregarResultados() {
    const corpo = document.getElementById("resultados-body");
    corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(MEUS_ATENDIMENTOS_URLS.resultados);
        const dados = await resposta.json();

        if (!dados.ok || dados.solicitacoes.length === 0) {
            corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">Ainda sem resultados concluídos.</td></tr>`;
            return;
        }

        corpo.innerHTML = dados.solicitacoes.map((s) => `
            <tr class="hover:bg-gray-50/50 transition">
                <td class="py-4 px-4 font-medium">${s.paciente}</td>
                <td class="py-4 px-4 text-gray-500">${s.total_itens}</td>
                <td class="py-4 px-4 text-gray-500 whitespace-nowrap">${meusAtendimentosFormatarDataHora(s.concluido_em)}</td>
                <td class="py-4 px-4 text-right">
                    <button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="abrirDetalheResultado(${s.id})">Ver</button>
                </td>
            </tr>
        `).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">Erro ao carregar resultados.</td></tr>`;
    }
}

function renderizarParametrosResultado(item) {
    const grupos = {};
    item.parametros.forEach((p) => {
        const chave = p.subgrupo || "GERAL";
        if (!grupos[chave]) grupos[chave] = [];
        grupos[chave].push(p);
    });

    let html = "";

    Object.keys(grupos).forEach((subgrupo) => {
        const linhas = grupos[subgrupo];

        html += `
            <div class="bg-[#2D3250] text-white px-4 py-2 text-xs font-bold uppercase tracking-wider">${subgrupo}</div>
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="border-b border-gray-100 bg-gray-50">
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Parâmetro</th>
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Resultado</th>
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Unidade</th>
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Referência</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-50 text-sm">
                    ${linhas.map((p) => `
                        <tr>
                            <td class="py-2.5 px-4 font-medium text-gray-800">${p.nome}</td>
                            <td class="py-2.5 px-4 font-semibold text-gray-800">${p.valor || "—"}</td>
                            <td class="py-2.5 px-4 text-gray-500">${p.unidade || "—"}</td>
                            <td class="py-2.5 px-4 text-gray-500">${p.referencia || "—"}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>`;
    });

    return html;
}

async function abrirDetalheResultado(id) {
    document.getElementById("modal-detalhe-resultado").classList.remove("hidden");
    const container = document.getElementById("resultado-itens-container");
    container.innerHTML = `<p class="text-center text-gray-400 py-6">A carregar...</p>`;

    try {
        const resposta = await fetch(MEUS_ATENDIMENTOS_URLS.resultadoDetalhe(id));
        const dados = await resposta.json();

        if (!dados.ok) {
            container.innerHTML = `<p class="text-center text-gray-400 py-6">Erro ao carregar o resultado.</p>`;
            return;
        }

        const s = dados.solicitacao;
        document.getElementById("resultado-paciente-nome").textContent = s.paciente;

        container.innerHTML = s.itens.map((item) => {
            if (item.tipo_resultado_exame === "MULTIPARAMETRO") {
                return `
                    <div class="border border-gray-200 rounded-xl overflow-hidden">
                        <div class="p-4">
                            <p class="font-semibold text-gray-800">${item.tipo_exame}</p>
                            <p class="text-xs text-gray-400">${item.departamento}</p>
                        </div>
                        ${renderizarParametrosResultado(item)}
                        <p class="text-xs text-gray-400 px-4 py-2 border-t border-gray-100">Resultado registado em ${meusAtendimentosFormatarDataHora(item.data_resultado)}</p>
                    </div>`;
            }

            return `
                <div class="border border-gray-200 rounded-xl p-4">
                    <p class="font-semibold text-gray-800">${item.tipo_exame}</p>
                    <p class="text-xs text-gray-400 mb-2">${item.departamento}</p>
                    <p class="text-sm text-gray-700 bg-gray-50 rounded-lg p-3">${item.resultado || "—"}</p>
                    <p class="text-xs text-gray-400 mt-2">Resultado registado em ${meusAtendimentosFormatarDataHora(item.data_resultado)}</p>
                </div>`;
        }).join("");
    } catch (erro) {
        container.innerHTML = `<p class="text-center text-gray-400 py-6">Erro ao carregar o resultado.</p>`;
    }
}

function closeDetalheResultadoModal() {
    document.getElementById("modal-detalhe-resultado").classList.add("hidden");
}