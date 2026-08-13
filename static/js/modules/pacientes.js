window.moduleInitializers = window.moduleInitializers || {};

const TAB_ACTIVE = "text-base sm:text-xl font-semibold text-orange-500 transition-colors cursor-pointer pb-3 whitespace-nowrap";
const TAB_INACTIVE = "text-base sm:text-xl font-medium text-gray-400 transition-colors cursor-pointer pb-3 whitespace-nowrap";

/* -------------------------------------------------------------------- */
/* UTIL: CSRF                                                            */
/* -------------------------------------------------------------------- */

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function urlAtualizarPara(codigo) {
    const form = document.getElementById("formCadastroPaciente");
    const template = form?.dataset.urlAtualizarTemplate || "";
    return template.replace("CODIGOPLACEHOLDER", encodeURIComponent(codigo));
}

function definirValor(id, valor) {
    const el = document.getElementById(id);
    if (el) el.value = valor ?? "";
}

/* Activa/desactiva todos os campos dos dois formulários do modal — usado
   para alternar entre modo edição (campos editáveis) e modo visualização
   (campos só-leitura, sem se poder submeter por engano). */
function definirCamposEditaveis(editavel) {
    const seletor = "#formPaciente input, #formPaciente select, #formResponsavel input, #formResponsavel select";
    document.querySelectorAll(seletor).forEach((campo) => {
        if (campo.id === "paciente_codigo") return; // este é sempre readonly
        campo.disabled = !editavel;
    });

    const btnSalvar = document.getElementById("btnSalvarPaciente");
    if (btnSalvar) btnSalvar.classList.toggle("hidden", !editavel);
}

/* -------------------------------------------------------------------- */
/* MODAL: abrir / fechar / trocar aba                                    */
/* -------------------------------------------------------------------- */

function resetParaCriacao() {
    const form = document.getElementById("formCadastroPaciente");
    if (!form) return;

    form.reset();
    document.getElementById("paciente_codigo").value = "";
    document.getElementById("paciente_nacionalidade").value = "Angolana";
    form.action = form.dataset.urlCriar;
    definirCamposEditaveis(true);

    const fotoAtual = document.getElementById("paciente_fotografia_atual");
    fotoAtual?.classList.add("hidden");
    if (fotoAtual) fotoAtual.textContent = "";

    document.getElementById("modalPacienteTitulo").textContent = "Novo Paciente";
    document.getElementById("modalPacienteSubtitulo").textContent = "Registe os dados do paciente no sistema.";
    document.getElementById("btnSalvarPacienteTexto").textContent = "Cadastrar Paciente";
}

window.abrirModal = () => {
    resetParaCriacao();
    document.getElementById("modalPaciente")?.classList.remove("hidden");
    mudarAba("paciente");
};

window.fecharModal = () => {
    document.getElementById("modalPaciente")?.classList.add("hidden");
    document.getElementById("modalErro")?.classList.add("hidden");
};

window.mudarAba = (aba) => {
    const isPaciente = aba === "paciente";

    document.getElementById("formPaciente")?.classList.toggle("hidden", !isPaciente);
    document.getElementById("formResponsavel")?.classList.toggle("hidden", isPaciente);

    const btnPaciente = document.getElementById("btnTabPaciente");
    const btnResponsavel = document.getElementById("btnTabResponsavel");
    if (btnPaciente) btnPaciente.className = isPaciente ? TAB_ACTIVE : TAB_INACTIVE;
    if (btnResponsavel) btnResponsavel.className = isPaciente ? TAB_INACTIVE : TAB_ACTIVE;

    const indicator = document.getElementById("tabIndicator");
    if (indicator) {
        indicator.style.width = isPaciente ? "70px" : "100px";
        indicator.style.left = isPaciente ? "0px" : "94px";
    }
};

/* Fechar ao clicar fora / Esc — registado uma única vez por load do script */
if (!window.__pacientesModalListenersRegistados) {
    document.addEventListener("click", (event) => {
        const modal = document.getElementById("modalPaciente");
        if (modal && event.target === modal) window.fecharModal();
    });
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") window.fecharModal();
    });
    window.__pacientesModalListenersRegistados = true;
}

/* -------------------------------------------------------------------- */
/* SUBMIT: cadastro OU atualização, consoante o modo do formulário       */
/* -------------------------------------------------------------------- */

window.submitPaciente = async function (event) {
    event.preventDefault();

    const form = document.getElementById("formCadastroPaciente");
    const erroEl = document.getElementById("modalErro");
    const btn = document.getElementById("btnSalvarPaciente");
    erroEl?.classList.add("hidden");

    const dados = new FormData(form);

    if (btn) {
        btn.disabled = true;
        btn.classList.add("opacity-60", "cursor-not-allowed");
    }

    try {
        const resposta = await fetch(form.action, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            body: dados,
        });

        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            if (erroEl) {
                erroEl.textContent = resultado.erro || "Erro ao guardar paciente.";
                erroEl.classList.remove("hidden");
            }
            return;
        }

        fecharModal();
        window.showToast?.(resultado.mensagem || "Paciente guardado com sucesso.");

        if (typeof window.loadModule === "function") {
            window.loadModule("pacientes", "Pacientes");
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
/* EDITAR: busca os dados reais do paciente e abre o modal pré-preenchido */
/* -------------------------------------------------------------------- */

async function carregarDadosPaciente(codigo) {
    const resposta = await fetch(`/pacientes/${encodeURIComponent(codigo)}/detalhe/`, {
        headers: { "X-Requested-With": "XMLHttpRequest" },
    });
    const resultado = await resposta.json();

    if (!resposta.ok || !resultado.ok) {
        window.showToast?.(resultado.erro || "Não foi possível carregar o paciente.", "error");
        return null;
    }

    const p = resultado.paciente;
    const form = document.getElementById("formCadastroPaciente");
    form.reset();
    document.getElementById("paciente_codigo").value = p.codigo;

    // Dados pessoais
    definirValor("paciente_primeiro_nome", p.primeiro_nome);
    definirValor("paciente_ultimo_nome", p.ultimo_nome);
    definirValor("paciente_data_nascimento", p.data_nascimento);
    definirValor("paciente_sexo", p.sexo);
    definirValor("paciente_estado_civil", p.estado_civil);
    definirValor("paciente_nacionalidade", p.nacionalidade || "Angolana");
    definirValor("paciente_profissao", p.profissao);
    definirValor("paciente_bi", p.bi);
    definirValor("paciente_contacto", p.contacto);

    // Fotografia: input file não pode ser pré-preenchido (limitação do
    // browser) — mostra-se um aviso com a foto já guardada.
    const fotoAtual = document.getElementById("paciente_fotografia_atual");
    if (fotoAtual) {
        if (p.fotografia_url) {
            fotoAtual.innerHTML = `Foto atual: <a href="${p.fotografia_url}" target="_blank" class="text-orange-600 underline">ver</a> — escolhe um novo ficheiro para substituir.`;
            fotoAtual.classList.remove("hidden");
        } else {
            fotoAtual.classList.add("hidden");
            fotoAtual.textContent = "";
        }
    }

    // Endereço
    definirValor("paciente_provincia", p.provincia);
    definirValor("paciente_municipio", p.municipio);
    definirValor("paciente_comuna", p.comuna);
    definirValor("paciente_bairro", p.bairro);
    definirValor("paciente_rua", p.rua);
    definirValor("paciente_numero_casa", p.numero_casa);
    definirValor("paciente_referencia", p.referencia);

    // Responsável
    definirValor("responsavel_nome", p.responsavel_nome);
    definirValor("responsavel_parentesco", p.responsavel_parentesco);
    definirValor("responsavel_contacto", p.responsavel_contacto);
    definirValor("responsavel_endereco", p.responsavel_endereco);

    return p;
}

window.editarPaciente = async (codigo) => {
    try {
        const p = await carregarDadosPaciente(codigo);
        if (!p) return;

        const form = document.getElementById("formCadastroPaciente");
        form.action = urlAtualizarPara(p.codigo);
        definirCamposEditaveis(true);

        document.getElementById("modalPacienteTitulo").textContent = "Editar Paciente";
        document.getElementById("modalPacienteSubtitulo").textContent = `A editar ${p.codigo}`;
        document.getElementById("btnSalvarPacienteTexto").textContent = "Guardar Alterações";

        document.getElementById("modalPaciente")?.classList.remove("hidden");
        mudarAba("paciente");
    } catch (e) {
        window.showToast?.("Falha de conexão ao carregar paciente.", "error");
    }
};

/* -------------------------------------------------------------------- */
/* ELIMINAR: chamada real ao backend, com confirmação                    */
/* -------------------------------------------------------------------- */

window.eliminarPaciente = async (btn, codigo) => {
    const tr = btn.closest("tr");
    const nome = tr?.querySelector("p.font-medium")?.textContent.trim() || codigo;

    if (!confirm(`Tem a certeza que deseja eliminar o paciente "${nome}" (${codigo})? Esta ação não pode ser desfeita.`)) {
        return;
    }

    try {
        const resposta = await fetch(`/pacientes/${encodeURIComponent(codigo)}/eliminar/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
        });
        const resultado = await resposta.json();

        if (!resposta.ok || !resultado.ok) {
            window.showToast?.(resultado.erro || "Não foi possível eliminar o paciente.", "error");
            return;
        }

        tr?.remove();
        window.showToast?.(resultado.mensagem || "Paciente eliminado.");
    } catch (e) {
        window.showToast?.("Falha de conexão ao eliminar paciente.", "error");
    }
};

/* -------------------------------------------------------------------- */
/* VISUALIZAR: mesmo modal, mesmos dados, mas em modo só-leitura         */
/* -------------------------------------------------------------------- */

window.visualizarPaciente = async (codigo) => {
    try {
        const p = await carregarDadosPaciente(codigo);
        if (!p) return;

        const form = document.getElementById("formCadastroPaciente");
        form.action = "#"; // não deve submeter nada em modo leitura
        definirCamposEditaveis(false);

        document.getElementById("modalPacienteTitulo").textContent = "Ver Paciente";
        document.getElementById("modalPacienteSubtitulo").textContent = `${p.codigo} — modo de visualização`;

        document.getElementById("modalPaciente")?.classList.remove("hidden");
        mudarAba("paciente");
    } catch (e) {
        window.showToast?.("Falha de conexão ao carregar paciente.", "error");
    }
};

/* -------------------------------------------------------------------- */
/* INICIALIZADOR DO MÓDULO "pacientes"                                    */
/* Chamado pelo navigation.js sempre que o painel é carregado no SPA.    */
/* -------------------------------------------------------------------- */

window.moduleInitializers.pacientes = function () {

    /* --- Autocomplete de entidade vinculada (mock local, sem backend) --- */
    const entidadesMock = [
        { id: 1, nome: "Clinica Multiperfil", tipo: "Empresa / Hospital" },
        { id: 2, nome: "Seguradora Allianz", tipo: "Seguradora" },
        { id: 3, nome: "Dr. Armando Santos", tipo: "Médico" },
        { id: 4, nome: "Colaborador João Baptista", tipo: "Colaborador" },
        { id: 5, nome: "Empresa Sonangol Saúde", tipo: "Empresa" },
    ];

    const input = document.getElementById("inputPesquisaEntidade");
    const drop = document.getElementById("dropdownEntidades");
    const hidden = document.getElementById("entidadeSelecionada");

    if (input && drop && hidden) {
        input.oninput = () => {
            const q = input.value.toLowerCase().trim();
            if (!q) {
                drop.classList.add("hidden");
                return;
            }
            const resultados = entidadesMock.filter(
                (x) => x.nome.toLowerCase().includes(q) || x.tipo.toLowerCase().includes(q)
            );
            drop.innerHTML = resultados.length
                ? resultados.map((x) => `
                    <div class="px-4 py-2.5 hover:bg-orange-50 cursor-pointer text-sm flex justify-between">
                        <span class="font-medium">${x.nome}</span>
                        <span class="text-xs text-orange-600">${x.tipo}</span>
                    </div>`).join("")
                : `<div class="px-4 py-3 text-sm text-gray-400">Nenhuma entidade encontrada</div>`;
            drop.classList.remove("hidden");

            [...drop.children].forEach((el, i) => {
                el.onclick = () => {
                    input.value = resultados[i].nome;
                    hidden.value = resultados[i].id;
                    drop.classList.add("hidden");
                };
            });
        };

        document.addEventListener("click", (e) => {
            if (!drop.contains(e.target) && e.target !== input) {
                drop.classList.add("hidden");
            }
        });
    }

    /* --- Pesquisa/filtro da tabela de pacientes --- */
    const pesquisa = document.getElementById("pesquisaPaciente");
    if (pesquisa) {
        pesquisa.oninput = () => {
            const termo = pesquisa.value.toLowerCase().trim();
            document.querySelectorAll("#pacientes-table-body .paciente-row").forEach((row) => {
                const alvo = (row.dataset.search || "").toLowerCase();
                row.style.display = alvo.includes(termo) ? "" : "none";
            });
        };
    }
};