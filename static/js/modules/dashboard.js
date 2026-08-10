window.moduleInitializers = window.moduleInitializers || {};
window.moduleInitializers.dashboard = function(){
    const reportBtn=document.getElementById("reportDropdownBtn"); const panel=document.getElementById("reportOptionsPanel");
    if(reportBtn && panel){ reportBtn.onclick=e=>{e.stopPropagation(); panel.classList.toggle("show");}; document.addEventListener("click",()=>panel.classList.remove("show"),{once:false}); }
    document.getElementById("btnNovoAtendimento")?.addEventListener("click",()=>window.loadModuleAndOpenModal("atendimento","modal-atendimento","Atendimentos"));
    document.getElementById("btnNovoPaciente")?.addEventListener("click",()=>window.loadModuleAndOpenModal("pacientes","modalPaciente","Pacientes"));
};
