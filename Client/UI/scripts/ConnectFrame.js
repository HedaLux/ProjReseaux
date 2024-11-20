const ipInputs = document.getElementsByClassName("ip-input")
const ipRegex = /^(25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])$/

Array.from(ipInputs).forEach((ipInput) => {
    inputs = ipInput.getElementsByTagName("input")
    
    Array.from(inputs).forEach((input, index) => {
        if(index == 0)
            return;
        
        let temp = ""
        
        input.addEventListener('focusin', e => {
            temp = e.target.value
            e.target.value = ""
        })
        
        input.addEventListener('focusout', e => {
            if(e.target.value == "" || !e.target.value.match(ipRegex))
                e.target.value = temp
            temp = ""
        })
        
        input.addEventListener("change", e => {
            if(e.target.value == "" || !e.target.value.match(ipRegex))
                return
            
            ip = inputs[0].value
            ipSplitted = ip.split('.')
            ipSplitted[index-1] = e.target.value
            inputs[0].value = ipSplitted.join('.')
        })
        
        
        input.addEventListener("input", e => {
            if(e.target.value.match(/^(1[0-9]{2}|2[0-4][0-9]|25[0-5])$/)) {
                if(index < (Array.from(inputs).length - 1)) {
                    const parent = e.target.parentNode
                    const siblingInputs = parent.getElementsByTagName('input')
                    const nextSibling = Array.from(siblingInputs)[index+1]
                    
                    nextSibling.focus()
                    console.log(nextSibling)
                } else {
                    //const portInput = input.parentElement.getElementBy
                    
                    e.target.blur()
                }
            } else {
                if(!e.target.value.match(ipRegex)){
                    e.target.blur()
                    e.target.focus()
                }
            }
        })
    })
})


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

document.getElementById("background-vid").playbackRate = 0.2;

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
