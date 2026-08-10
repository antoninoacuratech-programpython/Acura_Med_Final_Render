document.addEventListener("DOMContentLoaded", () => {
    const workspace = document.getElementById("workspace");
    const pageTitle = document.getElementById("pageTitle");
    const menuLinks = document.querySelectorAll(".sidebar-menu a[data-module]");
    const moduleMap = { dashboard: "Visão Geral", atendimento: "Atendimentos", encaminhamento: "Encaminhamentos", convenios: "Convênios & Guias", colaboradores: "Colaboradores", pacientes: "Pacientes", agendamentos: "Agendamentos", configuracoes: "Configurações", perfis: "Perfis", permissoes: "Permissões" };

    function setActive(module) {
        menuLinks.forEach(link => link.closest("li")?.classList.toggle("active", link.dataset.module === module));
    }

    const moduleScripts = { dashboard: "/static/js/modules/dashboard.js", pacientes: "/static/js/modules/pacientes.js", atendimento: "/static/js/modules/atendimento.js", encaminhamento: "/static/js/modules/encaminhamento.js", convenios: "/static/js/modules/convenios.js", colaboradores: "/static/js/modules/colaboradores.js", agendamentos: "/static/js/modules/agendamentos.js", configuracoes: "/static/js/modules/configuracoes.js", perfis: "/static/js/modules/perfis.js", permissoes: "/static/js/modules/permissoes.js" };
    async function initModule(module) {
        const src = moduleScripts[module];
        if (src && !document.querySelector(`script[data-module-script="${module}"]`)) {
            await new Promise((resolve, reject) => { const s = document.createElement("script"); s.src = src; s.dataset.moduleScript = module; s.onload = resolve; s.onerror = reject; document.body.appendChild(s); });
        }
        const fn = window.moduleInitializers?.[module]; if (typeof fn === "function") fn();
    }

    async function loadModule(module, title, options = {}) {
        if (!workspace || !module) return;
        workspace.classList.add("workspace-loading");
        setActive(module);
        if (pageTitle) pageTitle.textContent = title || moduleMap[module] || "Painel";
        try {
            const endpoint = options.url || `/modulos/${module}/`;
            const response = await fetch(endpoint, { headers: { "X-Requested-With": "XMLHttpRequest" } });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            workspace.innerHTML = await response.text();
            await initModule(module);
            if (options.openModal) {
                const modal = document.getElementById(options.openModal);
                modal?.classList.remove("hidden");
            }
        } catch (error) {
            console.error(error);
            workspace.innerHTML = `<div class="content-card"><h3>Não foi possível carregar o módulo</h3><p>Verifique a rota Django <strong>/modulos/${module}/</strong>.</p></div>`;
        } finally { workspace.classList.remove("workspace-loading"); }
    }

    menuLinks.forEach(link => link.addEventListener("click", e => { e.preventDefault(); loadModule(link.dataset.module, link.dataset.title); }));
    document.getElementById("settingsBtn")?.addEventListener("click", () => loadModule("configuracoes", "Configurações"));
    document.querySelectorAll(".dropdown-item[data-module]").forEach(link => link.addEventListener("click", e => { e.preventDefault(); loadModule(link.dataset.module, link.dataset.title); }));

    window.loadModule = loadModule;
    window.loadModuleAndOpenModal = (module, modalId, title) => loadModule(module, title, { openModal: modalId });
    loadModule("dashboard", "Visão Geral");
});
