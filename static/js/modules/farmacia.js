// static/js/modules/farmacia.js
//
// Módulo Farmácia. Carregado uma única vez pelo navigation.js e reiniciado
// a cada troca de módulo via window.moduleInitializers.farmacia().
// Segue o mesmo padrão AJAX + toast dos outros módulos: os forms não têm
// {% csrf_token %} embutido — o token é lido da cookie e enviado no header
// X-CSRFToken em cada fetch().

const FARMACIA_URLS = {
    medicamentoCadastrar: "/modulos/farmacia/medicamentos/cadastrar/",
    medicamentoDetalhe: (id) => `/modulos/farmacia/medicamentos/${id}/`,
    medicamentoAtualizar: (id) => `/modulos/farmacia/medicamentos/${id}/atualizar/`,
    medicamentoEliminar: (id) => `/modulos/farmacia/medicamentos/${id}/eliminar/`,
    loteCadastrar: "/modulos/farmacia/lotes/cadastrar/",
    lotesPorMedicamento: (id) => `/modulos/farmacia/medicamentos/${id}/lotes/`,
    movimentos: "/modulos/farmacia/movimentos/",
    prescricoes: "/modulos/farmacia/prescricoes/",
    prescricaoDetalhe: (id) => `/modulos/farmacia/prescricoes/${id}/`,
    prescricaoDispensar: (id) => `/modulos/farmacia/prescricoes/${id}/dispensar/`,
    prescricaoPendencia: (id) => `/modulos/farmacia/prescricoes/${id}/pendencia/`,
    requisicoes: "/modulos/farmacia/requisicoes/",
    requisicaoDetalhe: (id) => `/modulos/farmacia/requisicoes/${id}/`,
    requisicaoEntregar: (id) => `/modulos/farmacia/requisicoes/${id}/entregar/`,
    requisicaoRejeitar: (id) => `/modulos/farmacia/requisicoes/${id}/rejeitar/`,
    modulo: "/modulos/farmacia/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.farmacia = function () {
    const busca = document.getElementById("input-search-medicamento");
    if (busca) busca.value = "";
    atualizarBadgeReceitas();
    atualizarBadgeRequisicoes();
};

// -------------------------------------------------------------------------
// Helpers
// -------------------------------------------------------------------------

function farmaciaCsrfToken() {
    const nome = "csrftoken=";
    const partes = document.cookie.split(";");
    for (let parte of partes) {
        parte = parte.trim();
        if (parte.startsWith(nome)) {
            return decodeURIComponent(parte.substring(nome.length));
        }
    }
    return "";
}

function farmaciaFormatarData(isoDate) {
    if (!isoDate) return "—";
    const [ano, mes, dia] = isoDate.split("-");
    return `${dia}/${mes}/${ano}`;
}

async function farmaciaEnviar(url, formData) {
    const resposta = await fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": farmaciaCsrfToken() },
        body: formData,
    });
    const dados = await resposta.json();
    return dados;
}

async function farmaciaRecarregarPainel() {
    try {
        const resposta = await fetch(FARMACIA_URLS.modulo);
        const html = await resposta.text();
        const workspace = document.getElementById("workspace");
        if (workspace) {
            workspace.innerHTML = html;
            if (window.moduleInitializers && window.moduleInitializers.farmacia) {
                window.moduleInitializers.farmacia();
            }
        }
    } catch (erro) {
        console.error("Erro ao recarregar painel de farmácia:", erro);
    }
}

// -------------------------------------------------------------------------
// Medicamento
// -------------------------------------------------------------------------

function openMedicamentoModal(id) {
    const modal = document.getElementById("modal-medicamento");
    const form = document.getElementById("form-medicamento");
    const titulo = document.getElementById("titulo-modal-medicamento");
    const wrapperAtivo = document.getElementById("medicamento-ativo-wrapper");

    form.reset();
    document.getElementById("medicamento-id-input").value = "";
    wrapperAtivo.classList.add("hidden");
    wrapperAtivo.classList.remove("flex");

    if (id) {
        titulo.textContent = "Editar Medicamento";
        document.getElementById("medicamento-id-input").value = id;
        wrapperAtivo.classList.remove("hidden");
        wrapperAtivo.classList.add("flex");

        fetch(FARMACIA_URLS.medicamentoDetalhe(id))
            .then((r) => r.json())
            .then((dados) => {
                if (!dados.ok) {
                    window.showToast(dados.erro, "erro");
                    return;
                }
                const m = dados.medicamento;
                document.getElementById("medicamento-codigo").value = m.codigo;
                document.getElementById("medicamento-nome").value = m.nome;
                document.getElementById("medicamento-principio-ativo").value = m.principio_ativo;
                document.getElementById("medicamento-concentracao").value = m.concentracao;
                document.getElementById("medicamento-classe-terapeutica").value = m.classe_terapeutica;
                document.getElementById("medicamento-forma-farmaceutica").value = m.forma_farmaceutica;
                document.getElementById("medicamento-unidade-medida").value = m.unidade_medida;
                document.getElementById("medicamento-controlado").checked = m.controlado;
                document.getElementById("medicamento-ativo").checked = m.ativo;
            })
            .catch(() => window.showToast("Erro ao carregar dados do medicamento.", "erro"));
    } else {
        titulo.textContent = "Novo Medicamento";
    }

    modal.classList.remove("hidden");
}

function closeMedicamentoModal() {
    const modal = document.getElementById("modal-medicamento");
    modal.classList.add("hidden");
    document.getElementById("form-medicamento").reset();
}

function editarMedicamento(id) {
    openMedicamentoModal(id);
}

async function submitMedicamento(event) {
    event.preventDefault();
    const form = event.target;
    const id = document.getElementById("medicamento-id-input").value;
    const url = id ? FARMACIA_URLS.medicamentoAtualizar(id) : FARMACIA_URLS.medicamentoCadastrar;

    const dados = await farmaciaEnviar(url, new FormData(form));

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeMedicamentoModal();
    farmaciaRecarregarPainel();
}

async function eliminarMedicamento(id, nome) {
    if (!confirm(`Tem a certeza que deseja eliminar "${nome}"?`)) return;

    const dados = await farmaciaEnviar(FARMACIA_URLS.medicamentoEliminar(id), new FormData());

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    farmaciaRecarregarPainel();
}

function filterMedicamentos(query) {
    const termo = query.trim().toLowerCase();
    const linhas = document.querySelectorAll("#medicamento-table-body tr[data-id]");

    linhas.forEach((linha) => {
        const alvo = [
            linha.dataset.nome || "",
            linha.dataset.codigo || "",
            linha.dataset.principio || "",
        ].join(" ");
        linha.style.display = alvo.includes(termo) ? "" : "none";
    });
}

// -------------------------------------------------------------------------
// Lotes
// -------------------------------------------------------------------------

function openLotesModal(medicamentoId, nome) {
    document.getElementById("lotes-medicamento-nome").textContent = nome;
    document.getElementById("lote-medicamento-id").value = medicamentoId;
    document.getElementById("form-lote").reset();
    document.getElementById("lote-medicamento-id").value = medicamentoId;

    document.getElementById("modal-lotes").classList.remove("hidden");
    farmaciaCarregarLotes(medicamentoId);
}

function closeLotesModal() {
    document.getElementById("modal-lotes").classList.add("hidden");
    document.getElementById("form-lote").reset();
}

async function farmaciaCarregarLotes(medicamentoId) {
    const corpo = document.getElementById("lotes-table-body");
    corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(FARMACIA_URLS.lotesPorMedicamento(medicamentoId));
        const dados = await resposta.json();

        if (!dados.ok || dados.lotes.length === 0) {
            corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">Nenhum lote com stock disponível.</td></tr>`;
            return;
        }

        corpo.innerHTML = dados.lotes.map((lote) => {
            let badge;
            if (lote.vencido) {
                badge = `<span class="bg-red-50 text-red-600 text-xs font-medium px-3 py-1 rounded-full">Vencido</span>`;
            } else if (lote.dias_para_vencer <= 30) {
                badge = `<span class="bg-amber-50 text-amber-600 text-xs font-medium px-3 py-1 rounded-full">A vencer</span>`;
            } else {
                badge = `<span class="bg-teal-50 text-teal-600 text-xs font-medium px-3 py-1 rounded-full">Ok</span>`;
            }

            return `
                <tr class="hover:bg-gray-50/50 transition">
                    <td class="py-3 px-4 font-medium">${lote.numero_lote}</td>
                    <td class="py-3 px-4 text-gray-500">${farmaciaFormatarData(lote.validade)}</td>
                    <td class="py-3 px-4 text-gray-500">${lote.quantidade}</td>
                    <td class="py-3 px-4">${badge}</td>
                </tr>
            `;
        }).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">Erro ao carregar lotes.</td></tr>`;
    }
}

async function submitLote(event) {
    event.preventDefault();
    const form = event.target;
    const medicamentoId = document.getElementById("lote-medicamento-id").value;

    const dados = await farmaciaEnviar(FARMACIA_URLS.loteCadastrar, new FormData(form));

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    form.reset();
    document.getElementById("lote-medicamento-id").value = medicamentoId;
    farmaciaCarregarLotes(medicamentoId);
}

// -------------------------------------------------------------------------
// Histórico de Movimentos
// -------------------------------------------------------------------------

function openHistoricoModal() {
    document.getElementById("modal-historico").classList.remove("hidden");
    carregarHistorico();
}

function closeHistoricoModal() {
    document.getElementById("modal-historico").classList.add("hidden");
}

function exportarHistoricoPdf() {
    const params = new URLSearchParams();
    const medicamentoId = document.getElementById("historico-filtro-medicamento").value;
    const tipo = document.getElementById("historico-filtro-tipo").value;
    const dataInicio = document.getElementById("historico-filtro-data-inicio").value;
    const dataFim = document.getElementById("historico-filtro-data-fim").value;

    if (medicamentoId) params.set("medicamento_id", medicamentoId);
    if (tipo) params.set("tipo", tipo);
    if (dataInicio) params.set("data_inicio", dataInicio);
    if (dataFim) params.set("data_fim", dataFim);

    window.open(`/modulos/farmacia/relatorios/movimentos/pdf/?${params.toString()}`, "_blank");
}

async function carregarHistorico() {
    const corpo = document.getElementById("historico-body");
    corpo.innerHTML = `<tr><td colspan="7" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    const params = new URLSearchParams();
    const medicamentoId = document.getElementById("historico-filtro-medicamento").value;
    const tipo = document.getElementById("historico-filtro-tipo").value;
    const dataInicio = document.getElementById("historico-filtro-data-inicio").value;
    const dataFim = document.getElementById("historico-filtro-data-fim").value;

    if (medicamentoId) params.set("medicamento_id", medicamentoId);
    if (tipo) params.set("tipo", tipo);
    if (dataInicio) params.set("data_inicio", dataInicio);
    if (dataFim) params.set("data_fim", dataFim);

    try {
        const resposta = await fetch(`${FARMACIA_URLS.movimentos}?${params.toString()}`);
        const dados = await resposta.json();

        if (!dados.ok || dados.movimentos.length === 0) {
            corpo.innerHTML = `<tr><td colspan="7" class="py-6 px-4 text-center text-gray-400">Nenhum movimento encontrado.</td></tr>`;
            return;
        }

        const badges = {
            ENTRADA: "bg-teal-50 text-teal-600",
            SAIDA: "bg-red-50 text-red-600",
            AJUSTE: "bg-amber-50 text-amber-600",
        };

        corpo.innerHTML = dados.movimentos.map((m) => `
            <tr class="hover:bg-gray-50/50 transition">
                <td class="py-3 px-4 text-gray-500 whitespace-nowrap">${farmaciaFormatarDataHora(m.criado_em)}</td>
                <td class="py-3 px-4 font-medium">${m.medicamento}</td>
                <td class="py-3 px-4 text-gray-500">${m.numero_lote}</td>
                <td class="py-3 px-4"><span class="${badges[m.tipo] || "bg-gray-100 text-gray-500"} text-xs font-medium px-3 py-1 rounded-full">${m.tipo_display}</span></td>
                <td class="py-3 px-4 text-gray-500">${m.quantidade}</td>
                <td class="py-3 px-4 text-gray-500">${m.utilizador}</td>
                <td class="py-3 px-4 text-gray-500">${m.referencia || "—"}</td>
            </tr>
        `).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="7" class="py-6 px-4 text-center text-gray-400">Erro ao carregar o histórico.</td></tr>`;
    }
}

function farmaciaFormatarDataHora(isoString) {
    const data = new Date(isoString);
    return data.toLocaleString("pt-PT", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

// -------------------------------------------------------------------------
// Receitas (Farmácia processa prescrições digitais)
// -------------------------------------------------------------------------

let receitaAtualId = null;

async function atualizarBadgeReceitas() {
    try {
        const resposta = await fetch(FARMACIA_URLS.prescricoes);
        const dados = await resposta.json();
        const badge = document.getElementById("receitas-badge");
        if (!badge) return;

        const total = dados.ok ? dados.prescricoes.length : 0;
        badge.textContent = total;
        badge.classList.toggle("hidden", total === 0);
    } catch (erro) {
        // silencioso — o badge simplesmente não actualiza
    }
}

function openReceitasModal() {
    document.getElementById("modal-receitas").classList.remove("hidden");
    document.getElementById("input-search-receitas").value = "";
    carregarReceitas();
}

function closeReceitasModal() {
    document.getElementById("modal-receitas").classList.add("hidden");
}

async function carregarReceitas() {
    const corpo = document.getElementById("receitas-body");
    corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(FARMACIA_URLS.prescricoes);
        const dados = await resposta.json();

        if (!dados.ok || dados.prescricoes.length === 0) {
            corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Nenhuma receita por processar.</td></tr>`;
            return;
        }

        corpo.innerHTML = dados.prescricoes.map((p) => `
            <tr class="hover:bg-gray-50/50 transition" data-search="${p.paciente.toLowerCase()} ${p.paciente_codigo.toLowerCase()} ${(p.bi || "").toLowerCase()}">
                <td class="py-4 px-4 font-medium">${p.paciente}</td>
                <td class="py-4 px-4 text-gray-500">${p.bi || "—"}</td>
                <td class="py-4 px-4 text-gray-500">${p.medico}</td>
                <td class="py-4 px-4 text-gray-500">${p.total_itens}</td>
                <td class="py-4 px-4 text-gray-500 whitespace-nowrap">${farmaciaFormatarDataHora(p.criado_em)}</td>
                <td class="py-4 px-4 text-right">
                    <button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="abrirDetalheReceita(${p.id})">Ver</button>
                </td>
            </tr>
        `).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Erro ao carregar receitas.</td></tr>`;
    }
}

function filterReceitas(termo) {
    const alvo = termo.trim().toLowerCase();
    document.querySelectorAll("#receitas-body tr[data-search]").forEach((linha) => {
        linha.style.display = linha.dataset.search.includes(alvo) ? "" : "none";
    });
}

async function abrirDetalheReceita(id) {
    receitaAtualId = id;
    document.getElementById("modalErroReceita").classList.add("hidden");
    fecharPendenciaReceita();
    document.getElementById("modal-detalhe-receita").classList.remove("hidden");

    const corpo = document.getElementById("receita-itens-body");
    corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(FARMACIA_URLS.prescricaoDetalhe(id));
        const dados = await resposta.json();

        if (!dados.ok) {
            corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">Erro ao carregar a receita.</td></tr>`;
            return;
        }

        const p = dados.prescricao;
        document.getElementById("receita-paciente-nome").textContent = p.paciente;
        document.getElementById("receita-info-paciente").textContent = `${p.paciente} (${p.paciente_codigo})`;
        document.getElementById("receita-info-medico").textContent = p.medico;
        document.getElementById("receita-info-estado").textContent = p.status_display;

        corpo.innerHTML = p.itens.map((item) => {
            const badge = item.stock_suficiente
                ? `<span class="bg-teal-50 text-teal-600 text-xs font-medium px-3 py-1 rounded-full">Disponível (${item.stock_disponivel})</span>`
                : `<span class="bg-red-50 text-red-600 text-xs font-medium px-3 py-1 rounded-full">Insuficiente (${item.stock_disponivel})</span>`;

            return `
                <tr>
                    <td class="py-3 px-4 font-medium">${item.medicamento}${item.dosagem ? ` <span class="text-gray-400 font-normal">(${item.dosagem})</span>` : ""}</td>
                    <td class="py-3 px-4 text-gray-500">${item.via_administracao}${item.frequencia ? " — " + item.frequencia : ""}${item.duracao_dias ? ` — ${item.duracao_dias}d` : ""}</td>
                    <td class="py-3 px-4 text-gray-500">${item.quantidade}</td>
                    <td class="py-3 px-4">${badge}</td>
                </tr>`;
        }).join("");

        const btnDispensar = document.getElementById("btnDispensarReceita");
        btnDispensar.disabled = !p.pode_dispensar;
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="4" class="py-6 px-4 text-center text-gray-400">Erro ao carregar a receita.</td></tr>`;
    }
}

function closeDetalheReceitaModal() {
    document.getElementById("modal-detalhe-receita").classList.add("hidden");
    receitaAtualId = null;
}

async function dispensarReceita() {
    if (!receitaAtualId) return;
    const erroEl = document.getElementById("modalErroReceita");
    erroEl.classList.add("hidden");

    const dados = await farmaciaEnviar(FARMACIA_URLS.prescricaoDispensar(receitaAtualId), new FormData());

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeDetalheReceitaModal();
    carregarReceitas();
    atualizarBadgeReceitas();
    farmaciaRecarregarPainel();
}

function abrirPendenciaReceita() {
    document.getElementById("painel-pendencia-receita").classList.remove("hidden");
}

function fecharPendenciaReceita() {
    document.getElementById("painel-pendencia-receita").classList.add("hidden");
    document.getElementById("pendencia-motivo").value = "";
}

async function confirmarPendenciaReceita() {
    if (!receitaAtualId) return;
    const erroEl = document.getElementById("modalErroReceita");
    erroEl.classList.add("hidden");

    const formData = new FormData();
    formData.append("motivo", document.getElementById("pendencia-motivo").value);

    const dados = await farmaciaEnviar(FARMACIA_URLS.prescricaoPendencia(receitaAtualId), formData);

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeDetalheReceitaModal();
    carregarReceitas();
    atualizarBadgeReceitas();
}

// -------------------------------------------------------------------------
// Requisições Internas (sector → Farmácia)
// -------------------------------------------------------------------------

let requisicaoAtualId = null;

async function atualizarBadgeRequisicoes() {
    try {
        const resposta = await fetch(FARMACIA_URLS.requisicoes);
        const dados = await resposta.json();
        const badge = document.getElementById("requisicoes-badge");
        if (!badge) return;

        const total = dados.ok ? dados.requisicoes.length : 0;
        badge.textContent = total;
        badge.classList.toggle("hidden", total === 0);
    } catch (erro) {
        // silencioso
    }
}

function openRequisicoesModal() {
    document.getElementById("modal-requisicoes").classList.remove("hidden");
    carregarRequisicoes();
}

function closeRequisicoesModal() {
    document.getElementById("modal-requisicoes").classList.add("hidden");
}

async function carregarRequisicoes() {
    const corpo = document.getElementById("requisicoes-body");
    corpo.innerHTML = `<tr><td colspan="5" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(FARMACIA_URLS.requisicoes);
        const dados = await resposta.json();

        if (!dados.ok || dados.requisicoes.length === 0) {
            corpo.innerHTML = `<tr><td colspan="5" class="py-6 px-4 text-center text-gray-400">Nenhuma requisição pendente.</td></tr>`;
            return;
        }

        corpo.innerHTML = dados.requisicoes.map((r) => `
            <tr class="hover:bg-gray-50/50 transition">
                <td class="py-4 px-4 font-medium">${r.origem}</td>
                <td class="py-4 px-4 text-gray-500">${r.solicitante}</td>
                <td class="py-4 px-4 text-gray-500">${r.total_itens}</td>
                <td class="py-4 px-4 text-gray-500 whitespace-nowrap">${farmaciaFormatarDataHora(r.criado_em)}</td>
                <td class="py-4 px-4 text-right">
                    <button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="abrirDetalheRequisicao(${r.id})">Ver</button>
                </td>
            </tr>
        `).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="5" class="py-6 px-4 text-center text-gray-400">Erro ao carregar requisições.</td></tr>`;
    }
}

async function abrirDetalheRequisicao(id) {
    requisicaoAtualId = id;
    document.getElementById("modalErroRequisicao").classList.add("hidden");
    document.getElementById("modal-detalhe-requisicao").classList.remove("hidden");

    const corpo = document.getElementById("requisicao-itens-body");
    corpo.innerHTML = `<tr><td colspan="3" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(FARMACIA_URLS.requisicaoDetalhe(id));
        const dados = await resposta.json();

        if (!dados.ok) {
            corpo.innerHTML = `<tr><td colspan="3" class="py-6 px-4 text-center text-gray-400">Erro ao carregar a requisição.</td></tr>`;
            return;
        }

        const r = dados.requisicao;
        document.getElementById("requisicao-origem-nome").textContent = r.origem;
        document.getElementById("requisicao-info-solicitante").textContent = r.solicitante;
        document.getElementById("requisicao-info-estado").textContent = r.status_display;

        corpo.innerHTML = r.itens.map((item) => {
            const badge = item.stock_suficiente
                ? `<span class="bg-teal-50 text-teal-600 text-xs font-medium px-3 py-1 rounded-full">Disponível (${item.stock_disponivel})</span>`
                : `<span class="bg-red-50 text-red-600 text-xs font-medium px-3 py-1 rounded-full">Insuficiente (${item.stock_disponivel})</span>`;

            return `
                <tr>
                    <td class="py-3 px-4 font-medium">${item.medicamento}</td>
                    <td class="py-3 px-4 text-gray-500">${item.quantidade_solicitada}</td>
                    <td class="py-3 px-4">${badge}</td>
                </tr>`;
        }).join("");

        document.getElementById("btnEntregarRequisicao").disabled = !r.pode_entregar;
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="3" class="py-6 px-4 text-center text-gray-400">Erro ao carregar a requisição.</td></tr>`;
    }
}

function closeDetalheRequisicaoModal() {
    document.getElementById("modal-detalhe-requisicao").classList.add("hidden");
    requisicaoAtualId = null;
}

async function entregarRequisicao() {
    if (!requisicaoAtualId) return;
    const erroEl = document.getElementById("modalErroRequisicao");
    erroEl.classList.add("hidden");

    const dados = await farmaciaEnviar(FARMACIA_URLS.requisicaoEntregar(requisicaoAtualId), new FormData());

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeDetalheRequisicaoModal();
    carregarRequisicoes();
    atualizarBadgeRequisicoes();
    farmaciaRecarregarPainel();
}

async function rejeitarRequisicao() {
    if (!requisicaoAtualId) return;
    if (!confirm("Rejeitar esta requisição?")) return;

    const erroEl = document.getElementById("modalErroRequisicao");
    erroEl.classList.add("hidden");

    const dados = await farmaciaEnviar(FARMACIA_URLS.requisicaoRejeitar(requisicaoAtualId), new FormData());

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeDetalheRequisicaoModal();
    carregarRequisicoes();
    atualizarBadgeRequisicoes();
}