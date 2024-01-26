/*function safe_input() {
    const input = document.getElementById(inputid).value;
    localStorage.setItem(inputid, input);
}

function get_input(inputid) {
    return localStorage.getItem(inputid)
}
*/

//handle name
function save_name() {
    const name = document.getElementById("username-input").value
    localStorage.setItem("username", name)
    //create + check uuid
    const existingUuid = localStorage.getItem("uuid");

    if (!existingUuid) {
        // UUID not in local storage
        const uuid = self.crypto.randomUUID();
        localStorage.setItem("uuid", uuid);
    }
}

function get_name() {
    const pElement = document.getElementById(`username`);
    if (localStorage.getItem("username")) {
        pElement.textContent = localStorage.getItem("username");
    } else {
        pElement.textContent = "Spielername fehlt!";
    }
}

function toggleLock(diceId) {
    const checkboxElement = document.getElementById(`lock${diceId.charAt(diceId.length - 1)}`);
    const diceElement = document.getElementById(diceId);

    if (checkboxElement.checked) {
        diceElement.classList.add("locked");
    } else {
        diceElement.classList.remove("locked");
    }
}

//Darkmode
function get_color() {
    if (localStorage.getItem("darkMode") === "true") {
        document.documentElement.setAttribute('data-bs-theme', 'dark')
        document.getElementById("darkModeButton").classList.add("bi-lightbulb");
        document.getElementById("darkModeButton").classList.remove("bi-lightbulb-fill");
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'light')
        document.getElementById("darkModeButton").classList.remove("bi-lightbulb");
        document.getElementById("darkModeButton").classList.add("bi-lightbulb-fill");
    }
}

function switch_color() {
    if (localStorage.getItem("darkMode")) {
        if (localStorage.getItem("darkMode") === "true") {
            localStorage.setItem("darkMode", "false");
            get_color();
        }else {
            localStorage.setItem("darkMode", "true");
            get_color();
        }
    } else {
        localStorage.setItem("darkMode", "true");
        get_color();
    }
}