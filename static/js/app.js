document.addEventListener("DOMContentLoaded", () => {
    const dropdowns = [
        [document.getElementById("userMenuBtn"), document.getElementById("userDropdownMenu")],
        [document.getElementById("notificationBtn"), document.getElementById("notificationDropdownMenu")]
    ];
    const hide = () => dropdowns.forEach(([,menu]) => menu?.classList.remove("show"));
    dropdowns.forEach(([btn,menu]) => btn && menu && btn.addEventListener("click", e => { e.stopPropagation(); const open=menu.classList.contains("show"); hide(); if(!open) menu.classList.add("show"); }));
    document.addEventListener("click", hide);
});

window.showToast = function(message, type="success") {
    const toast=document.getElementById("app-toast"); if(!toast) return;
    toast.textContent=message; toast.dataset.type=type; toast.classList.add("show");
    clearTimeout(window.__toastTimer); window.__toastTimer=setTimeout(()=>toast.classList.remove("show"),2600);
};
