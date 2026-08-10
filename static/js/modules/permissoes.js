window.moduleInitializers = window.moduleInitializers || {};

function getCookiePermissoes(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function urlAtualizarPermissaoPara(id) {
    const form = document.getElementById("formPermissao");
    const template = form?.dataset.urlAtualizarTemplate || "";
    return template.replace("999999999", encodeURIComponent(id));
}

window.abrirModalPermissao = () => {
    const form = document.getElementById("formPermissao");
    form.reset();
    document.getElementById("permissao_id").value = "";
    document.getElementById("permissao_ativo").checked = true;
    form.action = form.dataset.urlCriar;

    document.getElementById("modalPermissaoTitulo").textContent = "Nova Permissão";
    document.getElementById("btnSalvarPermissaoTexto").textContent = "Criar Permissão";
    document.getElementById("modalPermissaoErro")?.classList.add("hidden");

    document.getElementById("modalPermissao")?.classList.remove("hidden");
};

window.fecharModalPermissao = () => {
    document.getElementById("modalPermissao")?.classList.add("hidden");
    document.getElementById("modalPermissaoErro")?.classList.add("hidden");
};

if (!window.__permissaoModalListenersRegistados) {
    document.addEventListener("click", (event) => {
        const modal = document.getElementById("modalPermissao");
        if (modal && event.target === modal) window.fecharModalPermissao();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") window.fecharModalPermissao();
    });
    window.__permissaoModalListenersRegistados = true;
}

/* -------------------------------------------------------------------- */
/* SUBMIT (criar OU atualizar)                                           */
/* -------------------------------------------------------------------- */

window.submitPermissao = async function (event) {
    event.preventDefault();

    const form = document.getElementById("formPermissao");
    const erroEl = document.getElementById("modalPermissaoErro");
    const btn = document.getElementById("btnSalvarPermissao");
    erroEl?.classList.add("hidden");

    const dados = new FormData(form);

    if (btn) {
        btn.disabled = true;
        btn.classList.add("opacity-60", "cursor-not-allowed");
    }

    try {
        const resposta = await fetch(form.action, {
            method: "POST",
            headers: { "X-CSRFToken": getCookiePermissoes("csrftoken") },
            body: dados,
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            if (erroEl) {
                erroEl.textContent = resultado.erro || "Erro ao guardar permissão.";
                erroEl.classList.remove("hidden");
            }
            return;
        }

        fecharModalPermissao();
        window.showToast?.(resultado.mensagem || "Permissão guardada com sucesso.");

        if (typeof window.loadModule === "function") {
            window.loadModule("permissoes", "Permissões");
        }
    } catch (e) {
        if (erroEl) {
            erroEl.textContent = "Falha de conexão. Tente novamente.";
            erroEl.classList.remove("hidden");
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.classList.remove("opacity-60", "cursor-not-allowed");
        }
    }
};

/* -------------------------------------------------------------------- */
/* EDITAR / ELIMINAR                                                     */
/* -------------------------------------------------------------------- */

window.editarPermissao = async (id) => {
    try {
        const resposta = await fetch(`/permissoes/${id}/detalhe/`, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            window.showToast?.(resultado.erro || "Não foi possível carregar a permissão.", "error");
            return;
        }

        const p = resultado.permissao;
        const form = document.getElementById("formPermissao");
        form.reset();

        document.getElementById("permissao_id").value = p.id;
        document.getElementById("permissao_nome").value = p.nome || "";
        document.getElementById("permissao_codigo").value = p.codigo || "";
        document.getElementById("permissao_descricao").value = p.descricao || "";
        document.getElementById("permissao_ativo").checked = !!p.ativo;
        form.action = urlAtualizarPermissaoPara(p.id);

        document.getElementById("modalPermissaoTitulo").textContent = "Editar Permissão";
        document.getElementById("btnSalvarPermissaoTexto").textContent = "Guardar Alterações";
        document.getElementById("modalPermissaoErro")?.classList.add("hidden");

        document.getElementById("modalPermissao")?.classList.remove("hidden");
    } catch (e) {
        window.showToast?.("Falha de conexão ao carregar permissão.", "error");
    }
};

window.eliminarPermissao = async (btn, id) => {
    const tr = btn.closest("tr");
    const nome = tr?.querySelector("span.font-medium")?.textContent.trim() || id;

    if (!confirm(`Tem a certeza que deseja eliminar a permissão "${nome}"? Isto remove-a de todos os perfis que a têm atribuída.`)) return;

    try {
        const resposta = await fetch(`/permissoes/${id}/eliminar/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookiePermissoes("csrftoken") },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            window.showToast?.(resultado.erro || "Não foi possível eliminar a permissão.", "error");
            return;
        }

        tr?.remove();
        window.showToast?.(resultado.mensagem || "Permissão eliminada.");
    } catch (e) {
        window.showToast?.("Falha de conexão ao eliminar permissão.", "error");
    }
};


window.moduleInitializers.permissoes = function () {
    const pesquisa = document.getElementById("pesquisaPermissao");
    if (pesquisa) {
        pesquisa.oninput = () => {
            const termo = pesquisa.value.toLowerCase().trim();
            document.querySelectorAll("#permissoes-table-body .permissao-row").forEach((row) => {
                const alvo = (row.dataset.search || "").toLowerCase();
                row.style.display = alvo.includes(termo) ? "" : "none";
            });
        };
    }
};