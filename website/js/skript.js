/*function safe_input() {
    const input = document.getElementById(inputid).value;
    localStorage.setItem(inputid, input);
}

function get_input(inputid) {
    return localStorage.getItem(inputid)
}
*/

//Check for secure environment because uuid etc. needs this
if(window.isSecureContext) {
    console.log("Ist sicher")
} else{
        console.log("Nix sicher")
}

function io() {
    return undefined;
}

const socket = io(); //socketio connection to server//


//handle name
function safe_name() {
    const name = document.getElementById("username-input").value
    localStorage.setItem("username", name)
    //create uuid
    const uuid = self.crypto.randomUUID()
    localStorage.setItem("uuid", uuid)
    socket.emit("safe_name", { username: name, uuid: uuid })

}

function get_name() {
    const pElement = document.getElementById(`username`);
    if (localStorage.getItem("username")) {
        pElement.textContent = localStorage.getItem("username");
    } else {
        pElement.textContent = "Spielername fehlt!";
    }
}


//create room
function create_room() {

}

//join existing room


function check_room() {
    const room = document.getElementById("room_id").value;

    fetch('/check_room', {
        method: 'POST',
        body: new URLSearchParams({'room': room}),
        headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (data.error) {
                //TODO change to Text on page
                alert("Ungültige Raum-ID. Bitte gib eine gültige ein.");
            } else {
                // forwarding
                window.location.href = "game.html?room=" + room;
            }
        })
        .catch(error => {
            //TODO change to Text on page
            alert("Ungültige Raum-ID oder Verbindungsproblem.");
        });
    // safe room-ID
    localStorage.setItem("room", room);
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