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
    modulo: "/modulos/farmacia/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.farmacia = function () {
    const busca = document.getElementById("input-search-medicamento");
    if (busca) busca.value = "";
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