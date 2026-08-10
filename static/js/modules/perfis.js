window.moduleInitializers = window.moduleInitializers || {};

function getCookiePerfis(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function urlAtualizarPerfilPara(id) {
    const form = document.getElementById("formPerfil");
    const template = form?.dataset.urlAtualizarTemplate || "";
    return template.replace("999999999", encodeURIComponent(id));
}

/* -------------------------------------------------------------------- */
/* Carregar a lista de permissões (para o checklist) — usa o endpoint    */
/* de listagem de permissões já existente, filtrando só as ativas.       */
/* -------------------------------------------------------------------- */

async function carregarChecklistPermissoes(idsSelecionados = []) {
    const container = document.getElementById("listaPermissoesPerfil");
    if (!container) return;

    container.innerHTML = `<p class="p-4 text-sm text-gray-400">A carregar permissões…</p>`;

    try {
        const resposta = await fetch("/permissoes/listar/", {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            container.innerHTML = `<p class="p-4 text-sm text-red-500">Não foi possível carregar as permissões.</p>`;
            return;
        }

        const permissoes = resultado.permissoes.filter((p) => p.ativo);

        if (!permissoes.length) {
            container.innerHTML = `<p class="p-4 text-sm text-gray-400">Nenhuma permissão ativa cadastrada ainda.</p>`;
            return;
        }

        container.innerHTML = permissoes.map((p) => `
            <label class="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50 cursor-pointer">
                <input type="checkbox" name="permissoes" value="${p.id}"
                       ${idsSelecionados.includes(p.id) ? "checked" : ""}
                       class="w-4 h-4 rounded border-gray-300 text-orange-500 focus:ring-orange-400">
                <span class="text-sm text-gray-700">${p.nome}</span>
                <span class="text-xs text-gray-400 ml-auto">${p.codigo}</span>
            </label>
        `).join("");
    } catch (e) {
        container.innerHTML = `<p class="p-4 text-sm text-red-500">Falha de conexão ao carregar permissões.</p>`;
    }
}

/* -------------------------------------------------------------------- */
/* MODAL: abrir / fechar                                                 */
/* -------------------------------------------------------------------- */

window.abrirModalPerfil = () => {
    const form = document.getElementById("formPerfil");
    form.reset();
    document.getElementById("perfil_id").value = "";
    document.getElementById("perfil_ativo").checked = true;
    form.action = form.dataset.urlCriar;

    document.getElementById("modalPerfilTitulo").textContent = "Novo Perfil";
    document.getElementById("btnSalvarPerfilTexto").textContent = "Criar Perfil";
    document.getElementById("modalPerfilErro")?.classList.add("hidden");

    carregarChecklistPermissoes([]);

    document.getElementById("modalPerfil")?.classList.remove("hidden");
};

window.fecharModalPerfil = () => {
    document.getElementById("modalPerfil")?.classList.add("hidden");
    document.getElementById("modalPerfilErro")?.classList.add("hidden");
};

if (!window.__perfilModalListenersRegistados) {
    document.addEventListener("click", (event) => {
        const modal = document.getElementById("modalPerfil");
        if (modal && event.target === modal) window.fecharModalPerfil();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") window.fecharModalPerfil();
    });
    window.__perfilModalListenersRegistados = true;
}

/* -------------------------------------------------------------------- */
/* SUBMIT (criar OU atualizar)                                           */
/* -------------------------------------------------------------------- */

window.submitPerfil = async function (event) {
    event.preventDefault();

    const form = document.getElementById("formPerfil");
    const erroEl = document.getElementById("modalPerfilErro");
    const btn = document.getElementById("btnSalvarPerfil");
    erroEl?.classList.add("hidden");

    const dados = new FormData(form);

    if (btn) {
        btn.disabled = true;
        btn.classList.add("opacity-60", "cursor-not-allowed");
    }

    try {
        const resposta = await fetch(form.action, {
            method: "POST",
            headers: { "X-CSRFToken": getCookiePerfis("csrftoken") },
            body: dados,
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            if (erroEl) {
                erroEl.textContent = resultado.erro || "Erro ao guardar perfil.";
                erroEl.classList.remove("hidden");
            }
            return;
        }

        fecharModalPerfil();
        window.showToast?.(resultado.mensagem || "Perfil guardado com sucesso.");

        if (typeof window.loadModule === "function") {
            window.loadModule("perfis", "Perfis");
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

window.editarPerfil = async (id) => {
    try {
        const resposta = await fetch(`/perfis/${id}/detalhe/`, {
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            window.showToast?.(resultado.erro || "Não foi possível carregar o perfil.", "error");
            return;
        }

        const p = resultado.perfil;
        const form = document.getElementById("formPerfil");
        form.reset();

        document.getElementById("perfil_id").value = p.id;
        document.getElementById("perfil_nome").value = p.nome || "";
        document.getElementById("perfil_descricao").value = p.descricao || "";
        document.getElementById("perfil_ativo").checked = !!p.ativo;
        form.action = urlAtualizarPerfilPara(p.id);

        document.getElementById("modalPerfilTitulo").textContent = "Editar Perfil";
        document.getElementById("btnSalvarPerfilTexto").textContent = "Guardar Alterações";
        document.getElementById("modalPerfilErro")?.classList.add("hidden");

        await carregarChecklistPermissoes(p.permissoes_ids || []);

        document.getElementById("modalPerfil")?.classList.remove("hidden");
    } catch (e) {
        window.showToast?.("Falha de conexão ao carregar perfil.", "error");
    }
};

window.eliminarPerfil = async (btn, id) => {
    const tr = btn.closest("tr");
    const nome = tr?.querySelector("span.font-medium")?.textContent.trim() || id;

    if (!confirm(`Tem a certeza que deseja eliminar o perfil "${nome}"?`)) return;

    try {
        const resposta = await fetch(`/perfis/${id}/eliminar/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookiePerfis("csrftoken") },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            window.showToast?.(resultado.erro || "Não foi possível eliminar o perfil.", "error");
            return;
        }

        tr?.remove();
        window.showToast?.(resultado.mensagem || "Perfil eliminado.");
    } catch (e) {
        window.showToast?.("Falha de conexão ao eliminar perfil.", "error");
    }
};

/* -------------------------------------------------------------------- */
/* INICIALIZADOR DO MÓDULO                                                */
/* -------------------------------------------------------------------- */

window.moduleInitializers.perfis = function () {
    const pesquisa = document.getElementById("pesquisaPerfil");
    if (pesquisa) {
        pesquisa.oninput = () => {
            const termo = pesquisa.value.toLowerCase().trim();
            document.querySelectorAll("#perfis-table-body .perfil-row").forEach((row) => {
                const alvo = (row.dataset.search || "").toLowerCase();
                row.style.display = alvo.includes(termo) ? "" : "none";
            });
        };
    }
};
