document.addEventListener("DOMContentLoaded", () => {
    const workspace = document.getElementById("workspace");
    const pageTitle = document.getElementById("pageTitle");
    const menuLinks = document.querySelectorAll(".sidebar-menu a[data-module]");
    const moduleMap = { dashboard: "Visão Geral", atendimento: "Atendimentos", encaminhamento: "Encaminhamentos", convenios: "Convênios & Guias", colaboradores: "Colaboradores", pacientes: "Pacientes", agendamentos: "Agendamentos", laboratorio: "Laboratório", farmacia: "Farmácia", meus_atendimentos: "Meus Atendimentos", triagem: "Triagem", configuracoes: "Configurações", perfis: "Perfis", permissoes: "Permissões" };

    function setActive(module, submodule) {
        menuLinks.forEach(link => {
            const isActive = link.dataset.module === module && (link.dataset.submodule || null) === (submodule || null);
            link.closest("li")?.classList.toggle("active", isActive);
        });

        // abre o submenu-pai correspondente e fecha os outros
        document.querySelectorAll(".sidebar-menu .has-submenu").forEach(parentLi => {
            const hasActiveChild = parentLi.querySelector(`.submenu a[data-module="${module}"]`) !== null;
            parentLi.classList.toggle("open", hasActiveChild);
        });
    }

    const moduleScripts = { dashboard: "/static/js/modules/dashboard.js", pacientes: "/static/js/modules/pacientes.js", atendimento: "/static/js/modules/atendimento.js", encaminhamento: "/static/js/modules/encaminhamento.js", convenios: "/static/js/modules/convenios.js", colaboradores: "/static/js/modules/colaboradores.js", agendamentos: "/static/js/modules/agendamentos.js", laboratorio: "/static/js/modules/laboratorio.js", farmacia: "/static/js/modules/farmacia.js", meus_atendimentos: "/static/js/modules/meus_atendimentos.js", triagem: "/static/js/modules/triagem.js", configuracoes: "/static/js/modules/configuracoes.js", perfis: "/static/js/modules/perfis.js", permissoes: "/static/js/modules/permissoes.js" };
    async function initModule(module, submodule) {
        const src = moduleScripts[module];
        if (src && !document.querySelector(`script[data-module-script="${module}"]`)) {
            await new Promise((resolve, reject) => { const s = document.createElement("script"); s.src = src; s.dataset.moduleScript = module; s.onload = resolve; s.onerror = reject; document.body.appendChild(s); });
        }
        const fn = window.moduleInitializers?.[module];
        if (typeof fn === "function") fn(submodule);
    }

    async function loadModule(module, title, options = {}) {
        if (!workspace || !module) return;
        const submodule = options.submodule || null;
        workspace.classList.add("workspace-loading");
        setActive(module, submodule);
        if (pageTitle) pageTitle.textContent = title || moduleMap[module] || "Painel";
        try {
            const base = options.url || `/modulos/${module}/`;
            const endpoint = submodule ? `${base}${base.includes("?") ? "&" : "?"}tab=${submodule}` : base;
            const response = await fetch(endpoint, { headers: { "X-Requested-With": "XMLHttpRequest" } });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            workspace.innerHTML = await response.text();
            await initModule(module, submodule);
            if (options.openModal) {
                const modal = document.getElementById(options.openModal);
                modal?.classList.remove("hidden");
            }
        } catch (error) {
            console.error(error);
            workspace.innerHTML = `<div class="content-card"><h3>Não foi possível carregar o módulo</h3><p>Verifique a rota Django <strong>/modulos/${module}/</strong>.</p></div>`;
        } finally { workspace.classList.remove("workspace-loading"); }
    }

    // itens finais (com data-module): carregam o módulo/submódulo
    menuLinks.forEach(link => link.addEventListener("click", e => {
        e.preventDefault();
        loadModule(link.dataset.module, link.dataset.title, { submodule: link.dataset.submodule });
    }));

    // cabeçalhos de submenu (sem data-module): só fazem accordion, não navegam
    document.querySelectorAll(".sidebar-menu .submenu-toggle").forEach(toggle => {
        toggle.addEventListener("click", e => {
            e.preventDefault();
            const parentLi = toggle.closest(".has-submenu");
            const wasOpen = parentLi.classList.contains("open");
            document.querySelectorAll(".sidebar-menu .has-submenu.open").forEach(li => li.classList.remove("open"));
            if (!wasOpen) parentLi.classList.add("open");
        });
    });

    document.getElementById("settingsBtn")?.addEventListener("click", () => loadModule("configuracoes", "Configurações"));
    document.querySelectorAll(".dropdown-item[data-module]").forEach(link => link.addEventListener("click", e => {
        e.preventDefault();
        loadModule(link.dataset.module, link.dataset.title, { submodule: link.dataset.submodule });
    }));

    window.loadModule = loadModule;
    window.loadModuleAndOpenModal = (module, modalId, title) => loadModule(module, title, { openModal: modalId });
    loadModule("dashboard", "Visão Geral");
});