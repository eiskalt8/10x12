$(document).ready(function () {
    const socket = io();
    socket.on("connect", function () {
        console.log("connected");
    });

    $('form#user').submit(function (event) {
        event.preventDefault();
        save_name();
        socket.emit("save_name", {
            username: localStorage.getItem("username"),
            uuid: localStorage.getItem("uuid")
        });
        window.location.href = "mode.html";
    });
    initPage();
    // forwarding to game.html/room_number
    socket.on("to_room", function (data) {
        const room_number = data.room_number;
        window.location.href = `/game/${room_number}`;
    });

    socket.on("error_message", function (data) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = data.message;
        errorDiv.style.display = 'block';
    });

    $('#new_room').submit(function (event) {
        event.preventDefault();

        // sends create_room event with uuid
        socket.emit("create_room", {
            uuid: localStorage.getItem('uuid')
        });
    });

    $('#join_room').submit(function (event) {
        event.preventDefault();
        document.getElementById('join-button').disabled = true;
        setTimeout(function () {
            document.getElementById('join-button').disabled = false;
        }, 2000);

        //sends join_room event room_id and uuid
        socket.emit("join_room", {
            room_number: document.getElementById('room_id').value,
            uuid: localStorage.getItem('uuid')
        });
    });
});

function initPage() {
    get_color();
    document.getElementById("darkModeButton").addEventListener("click", function () {
        switch_color();
    });
}

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
        } else {
            localStorage.setItem("darkMode", "true");
            get_color();
        }
    } else {
        localStorage.setItem("darkMode", "true");
        get_color();
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