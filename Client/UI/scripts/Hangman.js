const TIMER_DURATION = 40; // Durée en secondes
const timerText = document.getElementById("timer-text");
const progressCircle = document.querySelector(".progress");
const progressBG = document.querySelector(".bg");

// Calcul de la circonférence du cercle
const RADIUS = 45;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
progressCircle.style.strokeDasharray = CIRCUMFERENCE;

function startTimer(duration) {
    // Appliquer la durée de l'animation directement
    progressCircle.style.strokeDasharray = CIRCUMFERENCE;
    progressCircle.style.strokeDashoffset = CIRCUMFERENCE;
    progressCircle.style.animationDuration = `${duration}s`;
    
    // Démarrer l'animation
    progressCircle.style.animation = "none";
    if (progressBG.classList.contains("end-of-timer")){
        progressBG.classList.remove("end-of-timer");
        progressBG.offsetHeight
    }
    
    setTimeout(() => {
        progressCircle.style.animation = `progress-animation ${duration}s linear forwards`;
    }, 10);

    let timeLeft = duration;
    const m = Math.floor(timeLeft / 60);
    const s = timeLeft - m * 60;

    let timerStr = "";

    if (m > 0) timerStr += "" + m + "m";
    if (m > 0 && s < 10) timerStr += " 0" + s;
    else timerStr += s;

    timerText.textContent = timerStr;

    const interval = setInterval(() => {
        timeLeft--;

        const m = Math.floor(timeLeft / 60);
        const s = timeLeft - m * 60;

        let timerStr = "";

        if (m > 0) timerStr += "" + m + "m";
        if (m > 0 && s < 10) timerStr += " 0" + s;
        else timerStr += s;

        if (timeLeft <= 10) {
            if (!progressBG.classList.contains("end-of-timer"))
                progressBG.classList.add("end-of-timer");
            if (!timerText.classList.contains("tick"))
                timerText.classList.add("tick");
        }

        timerText.textContent = timerStr;

        if (timeLeft <= -1) {
            timerText.textContent = 0;
            clearInterval(interval);
            if (timerText.classList.contains("tick"))
                timerText.classList.remove("tick");
            progressCircle.classList.remove("progress-animate");
            progressCircle.offsetHeight;
        }
    }, 1000);
}

function startCooldownTimer(duration) {
    const cooldownTimer = document.getElementById("cooldown-timer")
    
    cooldownTimer.textContent = duration
    
    const interval = setInterval(() => {
        duration--;

        cooldownTimer.textContent = duration

        if (duration <= -1) {
            cooldownTimer.textContent = 0;
            clearInterval(interval);
        }
    }, 1000);
}

// Fonction pour mettre à jour la liste des joueurs
/*eel.expose(update_player_list);
function update_player_list(players) {
    const playerListContainer = document.getElementById("player-list");
    playerListContainer.innerHTML = ""; // Vider la liste existante
    players.forEach(player => {
        const playerItem = document.createElement("div");
        playerItem.textContent = player;
        playerListContainer.appendChild(playerItem);
    });
    console.log("Liste des joueurs mise à jour :", players);
}*/

// Gestion de l'envoi de messages dans le chat via la touche "Entrée"
sendMessage.addEventListener("keyup", (event) => {
    if (event.key === "Enter" && sendMessage.value.trim() !== "") {
        const message = sendMessage.value.trim();
        eel.send_chat_message(message); // Fonction exposée Python
        sendMessage.value = ""; // Réinitialise le champ de saisie
    }
});