console.log("RoomBrowser.js chargé avec succès");

// Récupérer et afficher le nom d'utilisateur
document.addEventListener("DOMContentLoaded", () => {
    const username = localStorage.getItem("username"); // Récupérer depuis localStorage
    if (username) {
        updateUsername(username); // Appeler la fonction pour mettre à jour
    } else {
        console.warn("Nom d'utilisateur introuvable !");
    }

    fetchUserStats(); // Appeler la récupération des stats
});

function updateUsername(username) {
    console.log("Mise à jour du nom d'utilisateur : ", username); // Debug
    document.querySelector(".greetings span").textContent = username; // Modifier le DOM
}



document.getElementById("background-vid").playbackRate = 0.2;

const serverBrowsers = document.getElementsByClassName("server-browser")


Array.from(serverBrowsers).forEach((serverBrowser) => {
    const data = serverBrowser.getElementsByClassName("data")[0]
    const joinButton = serverBrowser.parentNode.getElementsByClassName("join")[0]
    console.log("ici")
    console.log(joinButton)
    
    document.addEventListener("click", e => {
        if(e.target == joinButton)
            return
        
        if(serverBrowser.contains(e.target) && e.target.parentNode.classList.contains("room"))
            return
        
        if(selected == "")
            return
        
        joinButton.classList.add("hidden")
        selected.classList.remove("selected")
        selected = "";
    })
    
    let selected = ""

    const rooms = data.getElementsByClassName("room")

    Array.from(rooms).forEach((room) => {
        room.addEventListener("click", e => {
            const realTarget = e.target.parentNode

            if(realTarget.classList.contains("selected"))
                return

            realTarget.classList.add("selected")
            if(selected != "")
                selected.classList.remove("selected")

            selected = realTarget
            
            joinButton.classList.remove("hidden")
        })
    })
})

const createRoom = document.getElementById("create-room")
const modalCreateRoom = document.getElementById("modal-create-room")

createRoom.addEventListener("click", e => {
    modalCreateRoom.classList.remove("hidden")
})

/* MODAL */

const playercountInputWrapper = document.getElementById("player-count-wrapper");
const gamemodeInput = document.forms["create-room"]["gamemode"];

function checkGameMode() {
    if (gamemodeInput.value == "multiplayer") {
        if (!playercountInputWrapper.classList.contains("hidden")) return;
        playercountInputWrapper.classList.remove("hidden");
    } else {
        if (playercountInputWrapper.classList.contains("hidden")) return;
        playercountInputWrapper.classList.add("hidden");
    }
}

Array.from(gamemodeInput).forEach((input) => {
    input.addEventListener("change", (e) => {
        checkGameMode();
    });
});

const rangePickers = document.forms["create-room"].querySelectorAll('input[type="range"]')

Array.from(rangePickers).forEach((rangePicker) => {
    const parentElement = rangePicker.parentNode
    
    rangePicker.addEventListener("input", e => {
        parentElement.getElementsByTagName("span")[0].innerHTML = e.target.value;
    })
})

const modalWrappers = document.getElementsByClassName("modal-wrapper")

Array.from(modalWrappers).forEach((modalWrapper) => {
    modalWrapper.addEventListener("click", e => {
        if(modalWrapper.contains(e.target) && e.target != modalWrapper)
            return
        modalWrapper.classList.add("hidden")
    })
})

const radioButtons = document.forms["create-room"].querySelectorAll('input[type="radio"]')

Array.from(radioButtons).forEach((radioButton) => {
    const radioName = radioButton.getAttribute("name")
    const linkedLabel = radioButton.parentNode.querySelector('label[for="' + radioName + '"]')
    
    linkedLabel.addEventListener("click", e => {
        radioButton.click()
    })
})

// Fonction pour mettre à jour les statistiques utilisateur
function updateUserStats(stats) {
    //console.log("Mise à jour des statistiques avec : ", stats);
    document.querySelector(".multiplayer_games_played").textContent = stats.multiplayer_games_played;
    document.querySelector(".multiplayer_wins").textContent = stats.multiplayer_wins;
    document.querySelector(".solo_games_played").textContent = stats.solo_games_played;
    document.querySelector(".solo_wins").textContent = stats.solo_wins;
}

// Appel de la fonction exposée par Python pour récupérer les stats
function fetchUserStats() {
    console.log("called");
    eel.get_user_stats_ui()().then((response) => {
        console.log("Réponse reçue depuis Python : ", response); // Debug
        if (response.response === "success") {
            updateUserStats(response.stats);
        } else {
            alert("Erreur lors de la récupération des statistiques : " + response.message);
        }
    }).catch((err) => {
        console.error("Erreur lors de l'appel à get_user_stats_ui : ", err);
    });
}
