document.addEventListener("DOMContentLoaded", () => {
    const workspace = document.getElementById("workspace");
    const pageTitle = document.getElementById("pageTitle");

    const menuLinks = document.querySelectorAll(
        ".sidebar-menu a[data-module]"
    );

    // ============================================================
    // MAPA DOS MÓDULOS
    // ============================================================

    const moduleMap = {
        dashboard: "Visão Geral",
        atendimento: "Atendimentos",
        encaminhamento: "Encaminhamentos",
        convenios: "Convênios & Guias",
        colaboradores: "Colaboradores",
        pacientes: "Pacientes",
        agendamentos: "Agendamentos",
        laboratorio: "Laboratório",
        farmacia: "Farmácia",
        meus_atendimentos: "Meus Atendimentos",
        triagem: "Triagem",
        internamento: "Internamento",
        configuracoes: "Configurações",
        perfis: "Perfis",
        permissoes: "Permissões"
    };

    // ============================================================
    // SCRIPTS DOS MÓDULOS
    // ============================================================

    const moduleScripts = {
        dashboard: "/static/js/modules/dashboard.js",
        pacientes: "/static/js/modules/pacientes.js",
        atendimento: "/static/js/modules/atendimento.js",
        encaminhamento: "/static/js/modules/encaminhamento.js",
        convenios: "/static/js/modules/convenios.js",
        colaboradores: "/static/js/modules/colaboradores.js",
        agendamentos: "/static/js/modules/agendamentos.js",
        laboratorio: "/static/js/modules/laboratorio.js",
        farmacia: "/static/js/modules/farmacia.js",
        meus_atendimentos: "/static/js/modules/meus_atendimentos.js",
        triagem: "/static/js/modules/triagem.js",

        // ========================================================
        // INTERNAMENTO
        // ========================================================
        internamento: "/static/js/modules/internamento.js",

        configuracoes: "/static/js/modules/configuracoes.js",
        perfis: "/static/js/modules/perfis.js",
        permissoes: "/static/js/modules/permissoes.js"
    };

    // ============================================================
    // CONTROLO DO MENU ATIVO
    // ============================================================

    function setActive(module, submodule = null) {
        menuLinks.forEach(link => {
            const linkModule = link.dataset.module;
            const linkSubmodule = link.dataset.submodule || null;

            const isActive =
                linkModule === module &&
                linkSubmodule === submodule;

            link.closest("li")?.classList.toggle(
                "active",
                isActive
            );
        });

        // Fecha todos os submenus
        document
            .querySelectorAll(".sidebar-menu .has-submenu")
            .forEach(parentLi => {
                parentLi.classList.remove("open");
            });

        // Abre somente o submenu correspondente
        document
            .querySelectorAll(".sidebar-menu .has-submenu")
            .forEach(parentLi => {

                const activeChild = parentLi.querySelector(
                    `.submenu a[data-module="${module}"]`
                );

                if (activeChild) {
                    parentLi.classList.add("open");
                }
            });
    }

    // ============================================================
    // CARREGAMENTO DO JAVASCRIPT DO MÓDULO
    // ============================================================

    async function initModule(module, submodule = null) {

        const src = moduleScripts[module];

        if (src) {

            const existingScript = document.querySelector(
                `script[data-module-script="${module}"]`
            );

            if (!existingScript) {

                await new Promise((resolve, reject) => {

                    const script = document.createElement("script");

                    script.src = src;

                    script.dataset.moduleScript = module;

                    script.onload = () => {
                        console.log(
                            `Módulo "${module}" carregado com sucesso.`
                        );

                        resolve();
                    };

                    script.onerror = () => {
                        console.error(
                            `Erro ao carregar o script: ${src}`
                        );

                        reject(
                            new Error(
                                `Não foi possível carregar ${src}`
                            )
                        );
                    };

                    document.body.appendChild(script);
                });
            }
        }

        // Executa o inicializador do módulo
        const initializer =
            window.moduleInitializers?.[module];

        if (typeof initializer === "function") {

            try {

                await initializer(submodule);

            } catch (error) {

                console.error(
                    `Erro ao inicializar o módulo "${module}":`,
                    error
                );
            }
        }
    }

    // ============================================================
    // CARREGAMENTO DO MÓDULO
    // ============================================================

    async function loadModule(
        module,
        title = null,
        options = {}
    ) {

        if (!workspace || !module) {
            console.warn(
                "Workspace ou módulo não encontrado."
            );

            return;
        }

        const submodule =
            options.submodule || null;

        // Estado de carregamento
        workspace.classList.add(
            "workspace-loading"
        );

        // Menu ativo
        setActive(
            module,
            submodule
        );

        // Título da página
        if (pageTitle) {

            pageTitle.textContent =
                title ||
                moduleMap[module] ||
                "Painel";
        }

        try {

            // ====================================================
            // URL DO MÓDULO
            // ====================================================

            const base =
                options.url ||
                `/modulos/${module}/`;

            let endpoint = base;

            // ====================================================
            // SUBMÓDULO / TAB
            // ====================================================

            if (submodule) {

                endpoint =
                    `${base}${base.includes("?") ? "&" : "?"}tab=${encodeURIComponent(submodule)}`;
            }

            console.log(
                `Carregando módulo: ${module}`
            );

            console.log(
                `Endpoint: ${endpoint}`
            );

            // ====================================================
            // REQUEST DJANGO
            // ====================================================

            const response = await fetch(
                endpoint,
                {
                    method: "GET",

                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest",

                        "Accept":
                            "text/html"
                    },

                    credentials: "same-origin"
                }
            );

            // ====================================================
            // VERIFICA RESPOSTA
            // ====================================================

            if (!response.ok) {

                throw new Error(
                    `HTTP ${response.status}`
                );
            }

            const html =
                await response.text();

            // ====================================================
            // INSERE HTML NO WORKSPACE
            // ====================================================

            workspace.innerHTML = html;

            // ====================================================
            // INICIALIZA JAVASCRIPT DO MÓDULO
            // ====================================================

            await initModule(
                module,
                submodule
            );

            // ====================================================
            // ABRIR MODAL AUTOMATICAMENTE
            // ====================================================

            if (options.openModal) {

                const modal =
                    document.getElementById(
                        options.openModal
                    );

                if (modal) {

                    modal.classList.remove(
                        "hidden"
                    );
                }
            }

        } catch (error) {

            console.error(
                `Erro ao carregar módulo "${module}":`,
                error
            );

            // ====================================================
            // MENSAGEM DE ERRO
            // ====================================================

            workspace.innerHTML = `
                <div class="content-card">
                    <div class="content-card-body">

                        <h3>
                            Não foi possível carregar o módulo
                        </h3>

                        <p>
                            Ocorreu um erro ao carregar
                            <strong>${moduleMap[module] || module}</strong>.
                        </p>

                        <p>
                            Verifique a rota Django:
                        </p>

                        <code>
                            /modulos/${module}/
                        </code>

                    </div>
                </div>
            `;
        } finally {

            workspace.classList.remove(
                "workspace-loading"
            );
        }
    }

    // ============================================================
    // CLIQUES DOS ITENS DO MENU
    // ============================================================

    menuLinks.forEach(link => {

        link.addEventListener(
            "click",
            event => {

                event.preventDefault();

                const module =
                    link.dataset.module;

                const title =
                    link.dataset.title ||
                    moduleMap[module];

                const submodule =
                    link.dataset.submodule ||
                    null;

                loadModule(
                    module,
                    title,
                    {
                        submodule
                    }
                );
            }
        );
    });

    // ============================================================
    // SUBMENUS / ACCORDION
    // ============================================================

    document
        .querySelectorAll(
            ".sidebar-menu .submenu-toggle"
        )
        .forEach(toggle => {

            toggle.addEventListener(
                "click",
                event => {

                    event.preventDefault();

                    const parentLi =
                        toggle.closest(
                            ".has-submenu"
                        );

                    if (!parentLi) {
                        return;
                    }

                    const wasOpen =
                        parentLi.classList.contains(
                            "open"
                        );

                    // Fecha outros
                    document
                        .querySelectorAll(
                            ".sidebar-menu .has-submenu.open"
                        )
                        .forEach(li => {

                            if (li !== parentLi) {
                                li.classList.remove(
                                    "open"
                                );
                            }
                        });

                    // Alterna o atual
                    parentLi.classList.toggle(
                        "open",
                        !wasOpen
                    );
                }
            );
        });

    // ============================================================
    // BOTÃO DE CONFIGURAÇÕES
    // ============================================================

    document
        .getElementById("settingsBtn")
        ?.addEventListener(
            "click",
            event => {

                event.preventDefault();

                loadModule(
                    "configuracoes",
                    "Configurações"
                );
            }
        );

    // ============================================================
    // DROPDOWN
    // ============================================================

    document
        .querySelectorAll(
            ".dropdown-item[data-module]"
        )
        .forEach(link => {

            link.addEventListener(
                "click",
                event => {

                    event.preventDefault();

                    const module =
                        link.dataset.module;

                    const title =
                        link.dataset.title ||
                        moduleMap[module];

                    const submodule =
                        link.dataset.submodule ||
                        null;

                    loadModule(
                        module,
                        title,
                        {
                            submodule
                        }
                    );
                }
            );
        });

    // ============================================================
    // FUNÇÕES GLOBAIS
    // ============================================================

    window.loadModule =
        loadModule;

    window.loadModuleAndOpenModal =
        function (
            module,
            modalId,
            title = null
        ) {

            loadModule(
                module,
                title,
                {
                    openModal: modalId
                }
            );
        };

    // ============================================================
    // EVENTO GLOBAL PARA RECARREGAR UM MÓDULO
    // ============================================================

    window.reloadCurrentModule =
        function () {

            const activeLink =
                document.querySelector(
                    ".sidebar-menu a[data-module].active"
                );

            if (!activeLink) {
                loadModule(
                    "dashboard",
                    "Visão Geral"
                );

                return;
            }

            const module =
                activeLink.dataset.module;

            const title =
                activeLink.dataset.title ||
                moduleMap[module];

            const submodule =
                activeLink.dataset.submodule ||
                null;

            loadModule(
                module,
                title,
                {
                    submodule
                }
            );
        };

    // ============================================================
    // INICIALIZAÇÃO
    // ============================================================

    loadModule(
        "dashboard",
        "Visão Geral"
    );
});