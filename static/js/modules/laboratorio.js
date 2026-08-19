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
    parametrosExame: (tipoExameId) => `/modulos/laboratorio/exames/${tipoExameId}/parametros/`,
    parametroDetalhe: (ligacaoId) => `/modulos/laboratorio/parametros/${ligacaoId}/`,
    parametroSalvar: (tipoExameId) => `/modulos/laboratorio/exames/${tipoExameId}/parametros/salvar/`,
    parametroEliminar: (ligacaoId) => `/modulos/laboratorio/parametros/${ligacaoId}/eliminar/`,
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
                document.getElementById("exame-codigo-padronizado").value = e.codigo_padronizado;
                document.getElementById("exame-departamento").value = e.departamento;
                document.getElementById("exame-nome").value = e.nome;
                document.getElementById("exame-nome-tecnico").value = e.nome_tecnico;
                document.getElementById("exame-metodo").value = e.metodo;
                document.getElementById("exame-tipo-amostra").value = e.tipo_amostra;
                document.getElementById("exame-tipo-resultado").value = e.tipo_resultado;
                document.getElementById("exame-tempo-estimado").value = e.tempo_estimado;
                document.getElementById("exame-instrucoes-preparacao").value = e.instrucoes_preparacao;
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

function renderizarParametrosItem(item) {
    const grupos = {};
    item.parametros.forEach((p) => {
        const chave = p.subgrupo || "GERAL";
        if (!grupos[chave]) grupos[chave] = [];
        grupos[chave].push(p);
    });

    const total = item.parametros.length;
    const preenchidos = item.parametros.filter((p) => p.valor).length;
    const percentagem = total ? Math.round((preenchidos / total) * 100) : 0;

    let html = `
        <div class="px-4 pb-2 bg-white">
            <div class="flex items-center gap-3">
                <div class="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div class="h-full bg-[#F36A2D]" style="width:${percentagem}%"></div>
                </div>
                <span class="text-xs text-gray-400 whitespace-nowrap">${preenchidos}/${total} · ${percentagem}%</span>
            </div>
        </div>`;

    Object.keys(grupos).forEach((subgrupo) => {
        const linhas = grupos[subgrupo];
        const feitos = linhas.filter((p) => p.valor).length;

        html += `
            <div class="bg-[#2D3250] text-white px-4 py-2 flex items-center justify-between text-xs font-bold uppercase tracking-wider">
                <span>${subgrupo}</span>
                <span>${feitos}/${linhas.length}</span>
            </div>
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="border-b border-gray-100 bg-gray-50">
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Parâmetro</th>
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Lançamento</th>
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Unidade</th>
                        <th class="py-2 px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Referência</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-50 text-sm">
                    ${linhas.map((p) => `
                        <tr>
                            <td class="py-2.5 px-4 font-medium text-gray-800">${p.nome}</td>
                            <td class="py-2.5 px-4">
                                <input type="hidden" name="resultado_parametro_item_id[]" value="${item.id}"/>
                                <input type="hidden" name="resultado_parametro_parametro_id[]" value="${p.parametro_id}"/>
                                <input class="w-full px-2.5 py-1.5 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-[#F36A2D]" name="resultado_parametro_valor[]" oninput="atualizarProgressoParametros(this)" placeholder="Resultado..." value="${p.valor || ""}"/>
                            </td>
                            <td class="py-2.5 px-4 text-gray-500">${p.unidade || "—"}</td>
                            <td class="py-2.5 px-4 text-gray-500">${p.referencia || "—"}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>`;
    });

    return html;
}

function atualizarProgressoParametros() {
    // Recalcula a barra de progresso de cada item Multiparâmetro sempre
    // que um campo é preenchido — feedback visual imediato, sem esperar
    // por um novo pedido ao servidor.
    document.querySelectorAll("#solicitacao-itens-container > div").forEach((bloco) => {
        const campos = bloco.querySelectorAll("input[name='resultado_parametro_valor[]']");
        if (!campos.length) return;

        const total = campos.length;
        const preenchidos = Array.from(campos).filter((c) => c.value.trim()).length;
        const percentagem = Math.round((preenchidos / total) * 100);

        const barra = bloco.querySelector(".bg-\\[\\#F36A2D\\]");
        const texto = barra?.closest(".flex")?.querySelector("span");
        if (barra) barra.style.width = `${percentagem}%`;
        if (texto) texto.textContent = `${preenchidos}/${total} · ${percentagem}%`;
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

        container.innerHTML = s.itens.map((item) => {
            const cabecalho = `
                <div class="flex items-center justify-between mb-2">
                    <div>
                        <p class="font-semibold text-gray-800">${item.tipo_exame}</p>
                        <p class="text-xs text-gray-400">${item.departamento} — Amostra: ${item.tipo_amostra}</p>
                        ${item.observacoes ? `<p class="text-xs text-gray-400">Obs.: ${item.observacoes}</p>` : ""}
                    </div>
                    <span class="text-xs ${item.data_colheita ? "text-teal-600" : "text-gray-400"}">
                        <i class="fa-solid fa-vial mr-1"></i>${item.data_colheita ? "Colhido em " + laboratorioFormatarDataHora(item.data_colheita) : "Ainda não colhido"}
                    </span>
                </div>`;

            if (item.tipo_resultado_exame === "MULTIPARAMETRO") {
                return `<div class="border border-gray-200 rounded-xl overflow-hidden mb-2">
                    <div class="p-4 bg-white">${cabecalho}</div>
                    ${renderizarParametrosItem(item)}
                </div>`;
            }

            return `
                <div class="border border-gray-200 rounded-xl p-4">
                    ${cabecalho}
                    <input type="hidden" name="item_id[]" value="${item.id}"/>
                    <textarea class="w-full px-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm" name="item_resultado[]" placeholder="Resultado do exame..." rows="2">${item.resultado || ""}</textarea>
                </div>`;
        }).join("");
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
    document.querySelectorAll("#solicitacao-itens-container input[name='resultado_parametro_item_id[]']").forEach((el) => formData.append("resultado_parametro_item_id[]", el.value));
    document.querySelectorAll("#solicitacao-itens-container input[name='resultado_parametro_parametro_id[]']").forEach((el) => formData.append("resultado_parametro_parametro_id[]", el.value));
    document.querySelectorAll("#solicitacao-itens-container input[name='resultado_parametro_valor[]']").forEach((el) => formData.append("resultado_parametro_valor[]", el.value));

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

// -------------------------------------------------------------------------
// Parâmetros de um Exame (Multiparâmetro)
// -------------------------------------------------------------------------

let parametrosExameAtualId = null;

function gerirParametros(tipoExameId, nomeExame) {
    parametrosExameAtualId = tipoExameId;
    document.getElementById("parametros-exame-nome").textContent = nomeExame;
    document.getElementById("modal-parametros-exame").classList.remove("hidden");
    carregarParametrosExame();
}

function closeParametrosExameModal() {
    document.getElementById("modal-parametros-exame").classList.add("hidden");
    parametrosExameAtualId = null;
}

async function carregarParametrosExame() {
    const corpo = document.getElementById("parametros-exame-body");
    corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">A carregar...</td></tr>`;

    try {
        const resposta = await fetch(LABORATORIO_URLS.parametrosExame(parametrosExameAtualId));
        const dados = await resposta.json();

        if (!dados.ok || dados.parametros.length === 0) {
            corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Nenhum parâmetro associado a este exame ainda.</td></tr>`;
            return;
        }

        corpo.innerHTML = dados.parametros.map((p) => `
            <tr class="hover:bg-gray-50/50 transition">
                <td class="py-3 px-4 text-gray-500">${p.ordem}</td>
                <td class="py-3 px-4 font-medium">${p.nome}${p.unidade ? ` <span class="text-gray-400 font-normal">(${p.unidade})</span>` : ""}</td>
                <td class="py-3 px-4 text-gray-500">${p.subgrupo || "—"}</td>
                <td class="py-3 px-4 text-gray-500">${p.tipo_resultado_display}</td>
                <td class="py-3 px-4 text-gray-500">${p.total_referencias} grupo(s)</td>
                <td class="py-3 px-4 text-right whitespace-nowrap">
                    <button class="w-8 h-8 rounded-full inline-flex items-center justify-center text-gray-400 hover:text-blue-600 hover:bg-gray-100 transition" onclick="editarParametro(${p.id})" title="Editar">
                        <i class="fa-solid fa-pen text-xs"></i>
                    </button>
                    <button class="w-8 h-8 rounded-full inline-flex items-center justify-center text-gray-400 hover:text-red-600 hover:bg-gray-100 transition" onclick="eliminarParametroExame(${p.id}, '${p.nome.replace(/'/g, "\\'")}')" title="Remover">
                        <i class="fa-solid fa-trash-can text-xs"></i>
                    </button>
                </td>
            </tr>
        `).join("");
    } catch (erro) {
        corpo.innerHTML = `<tr><td colspan="6" class="py-6 px-4 text-center text-gray-400">Erro ao carregar parâmetros.</td></tr>`;
    }
}

function limparFormularioNovoParametro() {
    document.getElementById("form-novo-parametro").reset();
    document.getElementById("np-ligacao-id").value = "";
    document.getElementById("grupos-referencia-container").innerHTML = "";
    document.getElementById("modalErroNovoParametro").classList.add("hidden");
}

function abrirNovoParametro() {
    limparFormularioNovoParametro();
    document.getElementById("titulo-novo-parametro").textContent = "Novo parâmetro";
    document.getElementById("np-tipo-exame-id").value = parametrosExameAtualId;
    adicionarGrupoReferencia();
    document.getElementById("modal-novo-parametro").classList.remove("hidden");
}

async function editarParametro(ligacaoId) {
    limparFormularioNovoParametro();
    document.getElementById("titulo-novo-parametro").textContent = "Editar parâmetro";
    document.getElementById("np-tipo-exame-id").value = parametrosExameAtualId;
    document.getElementById("np-ligacao-id").value = ligacaoId;
    document.getElementById("modal-novo-parametro").classList.remove("hidden");

    try {
        const resposta = await fetch(LABORATORIO_URLS.parametroDetalhe(ligacaoId));
        const dados = await resposta.json();
        if (!dados.ok) {
            window.showToast("Erro ao carregar parâmetro.", "erro");
            return;
        }

        document.getElementById("np-nome").value = dados.parametro.nome;
        document.getElementById("np-unidade").value = dados.parametro.unidade;
        document.getElementById("np-tipo-resultado").value = dados.parametro.tipo_resultado;
        document.getElementById("np-observacoes").value = dados.parametro.descricao;
        document.getElementById("np-subgrupo").value = dados.subgrupo;
        document.getElementById("np-ordem").value = dados.ordem;

        if (dados.grupos.length === 0) {
            adicionarGrupoReferencia();
        } else {
            dados.grupos.forEach((g) => adicionarGrupoReferencia(g));
        }
    } catch (erro) {
        window.showToast("Erro ao carregar parâmetro.", "erro");
    }
}

function closeNovoParametroModal() {
    document.getElementById("modal-novo-parametro").classList.add("hidden");
}

function adicionarGrupoReferencia(valores) {
    const template = document.getElementById("template-grupo-referencia");
    const clone = template.content.cloneNode(true);

    if (valores) {
        clone.querySelector('[name="grupo_nome[]"]').value = valores.grupo || "Adulto";
        clone.querySelector('[name="grupo_sexo[]"]').value = valores.sexo || "AMBOS";
        clone.querySelector('[name="grupo_idade_min[]"]').value = valores.idade_minima || "";
        clone.querySelector('[name="grupo_idade_max[]"]').value = valores.idade_maxima || "";
        clone.querySelector('[name="grupo_sinal_min[]"]').value = valores.sinal_minimo || "-";
        clone.querySelector('[name="grupo_ref_min[]"]').value = valores.valor_minimo || "";
        clone.querySelector('[name="grupo_sinal_max[]"]').value = valores.sinal_maximo || "-";
        clone.querySelector('[name="grupo_ref_max[]"]').value = valores.valor_maximo || "";
        clone.querySelector('[name="grupo_critico_min[]"]').value = valores.critico_minimo || "";
        clone.querySelector('[name="grupo_critico_max[]"]').value = valores.critico_maximo || "";
        clone.querySelector('[name="grupo_ref_textual[]"]').value = valores.valor_texto || "";
    }

    document.getElementById("grupos-referencia-container").appendChild(clone);
}

async function submitNovoParametro(event) {
    event.preventDefault();
    const erroEl = document.getElementById("modalErroNovoParametro");
    erroEl.classList.add("hidden");

    const tipoExameId = document.getElementById("np-tipo-exame-id").value;
    const dados = await laboratorioEnviar(LABORATORIO_URLS.parametroSalvar(tipoExameId), new FormData(event.target));

    if (!dados.ok) {
        erroEl.textContent = dados.erro;
        erroEl.classList.remove("hidden");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    closeNovoParametroModal();
    carregarParametrosExame();
}

async function eliminarParametroExame(ligacaoId, nome) {
    if (!confirm(`Remover "${nome}" deste exame?`)) return;

    const dados = await laboratorioEnviar(LABORATORIO_URLS.parametroEliminar(ligacaoId), new FormData());

    if (!dados.ok) {
        window.showToast(dados.erro, "erro");
        return;
    }

    window.showToast(dados.mensagem, "sucesso");
    carregarParametrosExame();
}