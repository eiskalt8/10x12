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


//Darkmode
if (localStorage.getItem("darkMode") === true) {
    document.documentElement.setAttribute('data-bs-theme', 'dark')
}

/*document.getElementById('btnSwitch').addEventListener('click', () => {
    if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
        document.documentElement.setAttribute('data-bs-theme', 'light')
        localStorage.setItem("darkMode", false)
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'dark')
        localStorage.setItem("darkMode", true)
    }
})*/