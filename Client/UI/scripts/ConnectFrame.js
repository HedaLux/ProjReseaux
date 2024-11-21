const ipInputs = document.getElementsByClassName("ip-input");
const ipRegex = /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$/;

Array.from(ipInputs).forEach((ipInput) => {
    const inputs = ipInput.getElementsByTagName("input");
    const hiddenInput = ipInput.querySelector("input[name='server-ip']"); // Hidden input for server IP

    Array.from(inputs).forEach((input, index) => {
        if (index === 0) return;

        let temp = "";

        // Sauvegarde de l'ancienne valeur en cas d'entrée invalide
        input.addEventListener("focusin", (e) => {
            temp = e.target.value;
            e.target.value = "";
        });

        // Restaurer l'ancienne valeur si l'entrée est invalide
        input.addEventListener("focusout", (e) => {
            if (e.target.value === "" || !e.target.value.match(ipRegex)) {
                e.target.value = temp;
            }
            temp = "";

            // Mettre à jour le champ caché avec la nouvelle adresse IP
            updateHiddenInput();
        });

        // Mettre à jour le champ caché après une modification valide
        input.addEventListener("change", (e) => {
            if (e.target.value === "" || !e.target.value.match(ipRegex)) return;

            const ipSegments = Array.from(inputs).slice(1).map((input) => input.value || "0");
            hiddenInput.value = ipSegments.join(".");
            console.log("IP Updated: ", hiddenInput.value); // Debugging log
        });

         // Auto-focus sur le champ suivant si l'entrée est valide
        input.addEventListener("input", (e) => {
            if (e.target.value.match(/^(1[0-9]{2}|2[0-4][0-9]|25[0-5])$/)) {
                if (index < inputs.length - 1) {
                    inputs[index + 1].focus();
                } else {
                    e.target.blur(); // Si c'est le dernier champ, perdre le focus
                }
            }
        });
    });

    // Fonction pour mettre à jour le champ caché avec l'adresse IP complète
    function updateHiddenInput() {
        const ipSegments = Array.from(inputs).slice(1).map((input) => input.value || "0");
        hiddenInput.value = ipSegments.join(".");
        console.log("Hidden IP value updated to: ", hiddenInput.value); // Debug log
    }

    // Initialiser la valeur du champ caché au chargement de la page
    updateHiddenInput();
});



const connectBtn = document.getElementById("connect-btn")
const registerBtn = document.getElementById("register-btn")

const connectForm = document.getElementById("connect-form")
const registerForm = document.getElementById("register-form")

connectBtn.addEventListener('click', e => {
    if(connectBtn.classList.contains("checked"))
        return
    
    registerBtn.classList.remove("checked")
    registerForm.classList.add("hidden")
    
    
    connectBtn.classList.add("checked")
    connectForm.classList.remove("hidden")
})

registerBtn.addEventListener('click', e => {
    if(registerBtn.classList.contains("checked"))
        return
    
    connectBtn.classList.remove("checked")
    connectForm.classList.add("hidden")
    
    registerBtn.classList.add("checked")
    registerForm.classList.remove("hidden")
})

document.forms['connect-form'].addEventListener("submit", e => {
    e.preventDefault();
    
    const form = e.target.elements;
    const username = form['username'].value;
    const password = form['password'].value;
    const serverAddress = form['server-ip'].value;
    const serverPort = form['server-port'].value;

    eel.connect_to_server(username, password, serverAddress, serverPort)().then(res => {
        console.log(res);
        if (res["response"] === "error") {
            alert(res["message"]);
            return;
        }
        // Sauvegarder le nom d'utilisateur dans localStorage
        localStorage.setItem("username", username);
        window.location.href = "RoomBrowser.html";
    });
});

document.forms['register-form'].addEventListener("submit", e => {
    e.preventDefault();
    
    const form = e.target.elements;
    const username = form['username'].value;
    const password = form['password'].value;
    const passwordConfirm = form['password-confirm'].value;
    const serverAddress = form['server-ip'].value;
    const serverPort = form['server-port'].value;

    eel.connect_to_server(username, password, serverAddress, serverPort)().then(res => {
        console.log(res);
        if (res["response"] === "error") {
            alert(res["message"]);
            return;
        }
        // Sauvegarder le nom d'utilisateur dans localStorage
        localStorage.setItem("username", username);
        window.location.href = "RoomBrowser.html";
    });
});

