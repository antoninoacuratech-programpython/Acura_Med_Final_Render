// static/js/modules/laboratorio.js

const LABORATORIO_URLS = {
    exameCadastrar: "/modulos/laboratorio/exames/cadastrar/",
    exameDetalhe: (id) => `/modulos/laboratorio/exames/${id}/`,
    exameAtualizar: (id) => `/modulos/laboratorio/exames/${id}/atualizar/`,
    exameEliminar: (id) => `/modulos/laboratorio/exames/${id}/eliminar/`,
    modulo: "/modulos/laboratorio/",
};

window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.laboratorio = function () {
    const busca = document.getElementById("input-search-exame");
    if (busca) busca.value = "";
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