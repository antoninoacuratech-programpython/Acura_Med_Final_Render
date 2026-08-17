// static/js/modules/laboratorio.js

const LABORATORIO_URLS = {
    exameCadastrar: "/modulos/laboratorio/exames/cadastrar/",
    exameDetalhe: (id) => `/modulos/laboratorio/exames/${id}/`,
    exameAtualizar: (id) => `/modulos/laboratorio/exames/${id}/atualizar/`,
    exameEliminar: (id) => `/modulos/laboratorio/exames/${id}/eliminar/`,
    solicitacoes: "/modulos/laboratorio/solicitacoes/",
    solicitacaoDetalhe: (id) => `/modulos/laboratorio/solicitacoes/${id}/`,
    solicitacaoColher: (id) => `/modulos/laboratorio/solicitacoes/${id}/colher/`,
    solicitacaoConcluir: (id) => `/modulos/laboratorio/solicitacoes/${id}/concluir/`,
    modulo: "/modulos/laboratorio/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.laboratorio = function () {
    const busca = document.getElementById("input-search-exame");
    if (busca) busca.value = "";
    atualizarBadgeSolicitacoes();
};

function laboratorioCsrfToken() {
    const nome = "csrftoken=";
    const partes = document.cookie.split(";");
    for (let parte of partes) {
        parte = parte.trim();
        if (parte.startsWith(nome)) return decodeURIComponent(parte.substring(nome.length));
    }
    return "";
}

async function laboratorioEnviar(url, formData) {
    const resposta = await fetch(url, {
        method: "POST",
        headers: { "X-CSRFToken": laboratorioCsrfToken() },
        body: formData,
    });
    return resposta.json();
}

async function laboratorioRecarregarPainel() {
    try {
        const resposta = await fetch(LABORATORIO_URLS.modulo);
        const html = await resposta.text();
        const workspace = document.getElementById("workspace");
        if (workspace) {
            workspace.innerHTML = html;
            if (window.moduleInitializers && window.moduleInitializers.laboratorio) {
                window.moduleInitializers.laboratorio();
            }
        }
    } catch (erro) {
        console.error("Erro ao recarregar painel de laboratório:", erro);
    }
}

function openExameModal(id) {
    const modal = document.getElementById("modal-exame");
    const form = document.getElementById("form-exame");
    const titulo = document.getElementById("titulo-modal-exame");
    const wrapperAtivo = document.getElementById("exame-ativo-wrapper");

    form.reset();
    document.getElementById("exame-id-input").value = "";
    wrapperAtivo.classList.add("hidden");
    wrapperAtivo.classList.remove("flex");

    if (id) {
        titulo.textContent = "Editar Exame";
        document.getElementById("exame-id-input").value = id;
        wrapperAtivo.classList.remove("hidden");
        wrapperAtivo.classList.add("flex");

        fetch(LABORATORIO_URLS.exameDetalhe(id))
            .then((r) => r.json())
            .then((dados) => {
                if (!dados.ok) {
                    window.showToast(dados.erro, "erro");
                    return;
                }
                const e = dados.exame;
                document.getElementById("exame-codigo").value = e.codigo;
                document.getElementById("exame-nome").value = e.nome;
                document.getElementById("exame-categoria").value = e.categoria;
                document.getElementById("exame-tipo-amostra").value = e.tipo_amostra;
                document.getElementById("exame-valor-referencia").value = e.valor_referencia;
                document.getElementById("exame-unidade-medida").value = e.unidade_medida;
                document.getElementById("exame-tempo-estimado").value = e.tempo_estimado_horas ?? "";
                document.getElementById("exame-ativo").checked = e.ativo;
            })
            .catch(() => window.showToast("Erro ao carregar dados do exame.", "erro"));
    } else {
        titulo.textContent = "Novo Exame";
    }

    modal.classList.remove("hidden");
}

function closeExameModal() {
    document.getElementById("modal-exame").classList.add("hidden");
    document.getElementById("form-exame").reset();
}

function editarExame(id) {
    openExameModal(id);
}

async function submitExame(event) {
    event.preventDefault();
    const form = event.target;
    const id = document.getElementById("exame-id-input").value;
    const url = id ? LABORATORIO_URLS.exameAtualizar(id) : LABORATORIO_URLS.exameCadastrar;

    const dados = await laboratorioEnviar(url, new FormData(form));

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeExameModal();
    laboratorioRecarregarPainel();
}

async function eliminarExame(id, nome) {
    if (!confirm(`Tem a certeza que deseja eliminar "${nome}"?`)) return;

    const dados = await laboratorioEnviar(LABORATORIO_URLS.exameEliminar(id), new FormData());

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    laboratorioRecarregarPainel();
}

function filterExames(query) {
    const termo = query.trim().toLowerCase();
    const linhas = document.querySelectorAll("#exame-table-body tr[data-id]");

    linhas.forEach((linha) => {
        const alvo = [linha.dataset.nome || "", linha.dataset.codigo || ""].join(" ");
        linha.style.display = alvo.includes(termo) ? "" : "none";
    });
}

// -------------------------------------------------------------------------
// Solicitações de Exame (Recepção + Colheita + Resultado)
// -------------------------------------------------------------------------

let solicitacaoAtualId = null;

function laboratorioFormatarDataHora(isoString) {
    if (!isoString) return "—";
    const data = new Date(isoString);
    return data.toLocaleString("pt-PT", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

async function atualizarBadgeSolicitacoes() {
    try {
        const resposta = await fetch(LABORATORIO_URLS.solicitacoes);
        const dados = await resposta.json();
        const badge = document.getElementById("solicitacoes-badge");
        if (!badge) return;

        const total = dados.ok ? dados.solicitacoes.length : 0;
        badge.textContent = total;
        badge.classList.toggle("hidden", total === 0);
    } catch (erro) {
        // silencioso
    }
}

function openSolicitacoesModal() {
    document.getElementById("modal-solicitacoes").classList.remove("hidden");
    document.getElementById("input-search-solicitacoes").value = "";
    carregarSolicitacoes();
}

function closeSolicitacoesModal() {
    document.getElementById("modal-solicitacoes").classList.add("hidden");
}

const SOLICITACAO_BADGES = {
    AGUARDANDO: "bg-amber-50 text-amber-600",
    COLETADO: "bg-blue-50 text-blue-600",
};

async function carregarSolicitacoes() {
    const corpo = document.getElementById("solicitacoes-body");
    corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(LABORATORIO_URLS.solicitacoes);
        const dados = await resposta.json();

        if (!dados.ok || dados.solicitacoes.length === 0) {
            corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Nenhuma solicitação pendente.</td></tr>`;
            return;
        }

        corpo.innerHTML = dados.solicitacoes.map((s) => {
            const badge = SOLICITACAO_BADGES[s.status] || "bg-gray-100 text-gray-500";
            return `
                <tr class="hover:bg-gray-50/50 transition" data-search="${s.paciente.toLowerCase()} ${s.paciente_codigo.toLowerCase()}">
                    <td class="py-4 px-4 font-medium">${s.paciente}</td>
                    <td class="py-4 px-4 text-gray-500">${s.medico}</td>
                    <td class="py-4 px-4 text-gray-500">${s.total_itens}</td>
                    <td class="py-4 px-4"><span class="${badge} text-xs font-medium px-3 py-1 rounded-full">${s.status_display}</span></td>
                    <td class="py-4 px-4 text-gray-500 whitespace-nowrap">${laboratorioFormatarDataHora(s.criado_em)}</td>
                    <td class="py-4 px-4 text-right">
                        <button class="bg-[#2D3250] hover:bg-slate-800 text-white text-xs px-4 py-2 rounded-full font-medium transition shadow-sm" onclick="abrirDetalheSolicitacao(${s.id})">Ver</button>
                    </td>
                </tr>`;
        }).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Erro ao carregar solicitações.</td></tr>`;
    }
}

function filterSolicitacoes(termo) {
    const alvo = termo.trim().toLowerCase();
    document.querySelectorAll("#solicitacoes-body tr[data-search]").forEach((linha) => {
        linha.style.display = linha.dataset.search.includes(alvo) ? "" : "none";
    });
}

async function abrirDetalheSolicitacao(id) {
    solicitacaoAtualId = id;
    document.getElementById("modalErroSolicitacao").classList.add("hidden");
    document.getElementById("modal-detalhe-solicitacao").classList.remove("hidden");

    const container = document.getElementById("solicitacao-itens-container");
    container.innerHTML = `<p class="text-center text-gray-400 py-6">A carregar...</p>`;

    try {
        const resposta = await fetch(LABORATORIO_URLS.solicitacaoDetalhe(id));
        const dados = await resposta.json();

        if (!dados.ok) {
            container.innerHTML = `<p class="text-center text-gray-400 py-6">Erro ao carregar a solicitação.</p>`;
            return;
        }

        const s = dados.solicitacao;
        document.getElementById("solicitacao-paciente-nome").textContent = s.paciente;
        document.getElementById("solicitacao-info-paciente").textContent = `${s.paciente} (${s.paciente_codigo})`;
        document.getElementById("solicitacao-info-medico").textContent = s.medico;
        document.getElementById("solicitacao-info-estado").textContent = s.status_display;

        container.innerHTML = s.itens.map((item) => `
            <div class="border border-gray-200 rounded-xl p-4">
                <div class="flex items-center justify-between mb-2">
                    <div>
                        <p class="font-semibold text-gray-800">${item.tipo_exame}</p>
                        <p class="text-xs text-gray-400">${item.categoria} — Amostra: ${item.tipo_amostra}${item.valor_referencia ? " — Ref.: " + item.valor_referencia : ""}${item.unidade_medida ? " " + item.unidade_medida : ""}</p>
                        ${item.observacoes ? `<p class="text-xs text-gray-400">Obs.: ${item.observacoes}</p>` : ""}
                    </div>
                    <span class="text-xs ${item.data_colheita ? "text-teal-600" : "text-gray-400"}">
                        <i class="fa-solid fa-vial mr-1"></i>${item.data_colheita ? "Colhido em " + laboratorioFormatarDataHora(item.data_colheita) : "Ainda não colhido"}
                    </span>
                </div>
                <input type="hidden" name="item_id[]" value="${item.id}"/>
                <textarea class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm" name="item_resultado[]" placeholder="Resultado do exame..." rows="2">${item.resultado || ""}</textarea>
            </div>
        `).join("");
    } catch (erro) {
        container.innerHTML = `<p class="text-center text-gray-400 py-6">Erro ao carregar a solicitação.</p>`;
    }
}

function closeDetalheSolicitacaoModal() {
    document.getElementById("modal-detalhe-solicitacao").classList.add("hidden");
    solicitacaoAtualId = null;
}

async function registarColheita() {
    if (!solicitacaoAtualId) return;
    const erroEl = document.getElementById("modalErroSolicitacao");
    erroEl.classList.add("hidden");

    const dados = await laboratorioEnviar(LABORATORIO_URLS.solicitacaoColher(solicitacaoAtualId), new FormData());

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    abrirDetalheSolicitacao(solicitacaoAtualId);
    carregarSolicitacoes();
    atualizarBadgeSolicitacoes();
}

async function concluirSolicitacao() {
    if (!solicitacaoAtualId) return;
    const erroEl = document.getElementById("modalErroSolicitacao");
    erroEl.classList.add("hidden");

    const formData = new FormData();
    document.querySelectorAll("#solicitacao-itens-container input[name='item_id[]']").forEach((el) => formData.append("item_id[]", el.value));
    document.querySelectorAll("#solicitacao-itens-container textarea[name='item_resultado[]']").forEach((el) => formData.append("item_resultado[]", el.value));

    const dados = await laboratorioEnviar(LABORATORIO_URLS.solicitacaoConcluir(solicitacaoAtualId), formData);

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeDetalheSolicitacaoModal();
    carregarSolicitacoes();
    atualizarBadgeSolicitacoes();
}