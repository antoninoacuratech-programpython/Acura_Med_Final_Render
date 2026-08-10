document.addEventListener("DOMContentLoaded", () => {
    const splash = document.getElementById("splash");
    if (splash) {
        setTimeout(() => {
            splash.classList.add("hide");
            document.body.classList.remove("loading");
        }, 2500);
    }
    const loginBox = document.getElementById("loginBox");
    const cadastroBox = document.getElementById("cadastroBox");

    const goCadastro = document.getElementById("goCadastro");
    const goLogin = document.getElementById("goLogin");

    const mobileLogin = document.getElementById("mobileLogin");
    const mobileCadastro = document.getElementById("mobileCadastro");

    function mostrarLogin() {
        if (cadastroBox) cadastroBox.classList.remove("active");
        if (loginBox) loginBox.classList.add("active");
    }

    function mostrarCadastro() {
        if (loginBox) loginBox.classList.remove("active");
        if (cadastroBox) cadastroBox.classList.add("active");
    }

    if (mobileLogin) mobileLogin.addEventListener("click", mostrarLogin);
    if (mobileCadastro) mobileCadastro.addEventListener("click", mostrarCadastro);

    if (goCadastro) {
        goCadastro.addEventListener("click", (e) => {
            e.preventDefault();
            mostrarCadastro();
        });
    }

    if (goLogin) {
        goLogin.addEventListener("click", (e) => {
            e.preventDefault();
            mostrarLogin();
        });
    }

    // 3. MOSTRAR / OCULTAR SENHA
    const passwordIcons = document.querySelectorAll(".toggle-password");
    passwordIcons.forEach(icon => {
        icon.addEventListener("click", () => {
            const input = icon.previousElementSibling;
            if (input && input.type === "password") {
                input.type = "text";
                icon.classList.replace("fa-eye", "fa-eye-slash");
            } else if (input) {
                input.type = "password";
                icon.classList.replace("fa-eye-slash", "fa-eye");
            }
        });
    });


});