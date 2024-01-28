const socket = io();
if (window.location.href.includes("game")) {
    let room_number = window.location.pathname
    room_number = room_number.split('/')
    room_number = room_number[2]
}
const uuid = localStorage.getItem('uuid')
if (uuid) {
    const uuid_part = uuid.substring(0, 8)
}
const username = localStorage.getItem('username')
let room_locked = false
let is_current_player = false
const diceIds = ["dice1", "dice2", "dice3", "dice4", "dice5", "dice6"];

$(document).ready(function () {
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

    if (window.location.href.includes("game")) {
        // TODO  find a way for fixing reload site
        // triggering join_room at reload and joining
        /*socket.emit('join_room', {
            room_number: room_number,
            uuid: uuid
        });
        // for only get current dices at reload and joining
        socket.emit('dices', {
            room_number: room_number,
            uuid: uuid,
            dices: false,
            locked_dices: false
        });
        setTimeout(function () {
            // for showing the scores at reload and joining
            socket.emit('new_score', {
                room_number: room_number,
                uuid: uuid,
                score: false
            });
            // for showing the current player border at reload and joining
            socket.emit('next_player', {
                room_number: room_number,
                uuid: uuid,
            });
        }, 2000);*/

        // generate big table
        const tableHead = document.querySelector('#playerTable thead');
        if (tableHead) {
            let headHtml = '<th scope="col">Zahlen</th>';
            for (let col = 1; col <= 10; col++) {
                headHtml += '<th scope="col">' + col + '</th>';
            }
            headHtml += '<th scope="col">Zahlen</th>';

            tableHead.innerHTML = headHtml;

            const tableBody = document.querySelector('#playerTable tbody');

            for (let row = 1; row <= 12; row++) {
                let rowHtml = '<tr><th scope="row">' + row + '</th>';

                for (let col = 1; col <= 10; col++) {
                    rowHtml += '<td><input class="form-check-input" disabled type="checkbox" id="' + row + '-' + col + '" style="border-color: var(--bs-primary)"></td>';
                }

                rowHtml += '<th scope="row">' + row + '</th></tr>';
                tableBody.innerHTML += rowHtml;
            }
        }

        // generate other user tables
        socket.on('update_amount_tables', function (data) {
            let nameList = data.names;
            generatePlayerTables(nameList);
            let player = data.current_player;
            if (!(player === "nicht gefunden!")) { // if uuid was found
                if (player === uuid_part) {
                    is_current_player = true // set variable to allow next()
                    activate_buttons()
                    document.getElementById("border_player_table").classList.add("custom_border");
                }
            }
        });

        socket.on('new_next_player', function (data) {
            let userlist = data.userlist;
            let currentPlayer = data.current_player;
            diceIds.forEach(diceId => {
                const diceElement = document.getElementById(diceId);
                diceElement.classList.remove('locked');
            });
            for (let i = 1; i <= 6; i++) {
                const checkbox = document.getElementById(`lock${i}`);
                checkbox.checked = false;
                checkbox.parentElement.classList.remove('active');
            }
            if (currentPlayer === uuid_part) {
                is_current_player = true;
                activate_buttons()
            }
            // set custom_border
            change_custom_border(userlist, currentPlayer)
        });

        socket.on('new_dices', function (data) {
            const new_dices = data.new_dices;
            const locked_dices = data.locked_dices;

            diceIds.forEach(diceId => {
                const diceElement = document.getElementById(diceId);
                diceElement.classList.remove('locked');
                if (locked_dices && locked_dices.includes(diceId)) {
                    diceElement.classList.add('locked');
                }
                if (!diceElement.classList.contains('locked')) {
                    diceElement.classList.add('rolling');
                    setTimeout(() => {
                        diceElement.classList.remove('rolling');
                        diceElement.className = `bi bi-dice-${new_dices[diceId.charAt(4)]} dice`;
                    }, 500);// Wait in Millisec
                }
            });
        });

        socket.on('new_scores', function (data) {
            let new_scores = JSON.parse(data.new_scores);
            for (let uuid_part_ in new_scores) {
                for (let number in new_scores[uuid_part_]) {
                    // disable checkboxes and remove all success
                    for (let i = 1; i <= 10; i++) {
                        if (uuid_part_ === uuid_part) {
                            let checkbox = document.getElementById(`${number}-${i}`);
                            checkbox.checked = false;
                        } else {
                            let field = document.getElementById(`${uuid_part_}-${number}-${i}`);
                            if (field && field.classList.contains("table-success")) {
                                field.classList.remove("table-success");
                            }
                        }
                    }
                    // show new scores
                    for (let i = 1; i <= new_scores[uuid_part_][number]; i++) {
                        if (uuid_part_ === uuid_part) {
                            let checkbox = document.getElementById(`${number}-${i}`);
                            checkbox.checked = true;
                        } else {
                            let field = document.getElementById(`${uuid_part_}-${number}-${i}`);
                            field.classList.add("table-success");
                        }
                    }
                }
            }
        });
    }

    socket.on('room_locked', function (data) {
        if ('message' in data) {
            const locktext = document.getElementById('lockmsg-text');
            locktext.textContent = data['message'];
            const lockmsg = document.getElementById('lockmsg');
            lockmsg.style.display = 'block';
        }
        room_locked = true
    });


    socket.on('disconnect', function () {
        console.log("disconnected")
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

function rollDice() {
    let dices = {};
    let locked_dices = [];
    let completed = 0
    document.getElementById('würfel').disabled = true;
    if (is_current_player === true) {
        // need to lock the room?
        if (room_locked === false) {
            socket.emit('lock_room', {
                room_number: room_number
            });
        }
        let score = get_score()
        socket.emit('new_score', {
            room_number: room_number,
            uuid: uuid,
            score: score
        });

        setTimeout(function () {
            document.getElementById('würfel').disabled = false;
        }, 2000);

        diceIds.forEach(diceId => {
            const diceElement = document.getElementById(diceId);
            if (!diceElement.classList.contains('locked')) {
                diceElement.classList.add('rolling');
                setTimeout(() => {
                    if (diceElement.classList.contains('rolling')) {
                        const randomNumber = Math.floor(Math.random() * 6) + 1;
                        diceElement.classList.remove('rolling');
                        diceElement.className = `bi bi-dice-${randomNumber} dice`;
                        dices[diceId.charAt(4)] = randomNumber;

                        completed++

                        if (completed === diceIds.length) {
                            socket.emit('dices', {
                                room_number: room_number,
                                uuid: uuid,
                                dices: dices,
                                locked_dices: locked_dices
                            });
                        }
                    }
                }, 500);// Wait in Millisec
            } else {
                locked_dices.push(diceId);
                completed++

                if (completed === diceIds.length) {
                    socket.emit('dices', {
                        room_number: room_number,
                        uuid: uuid,
                        dices: dices,
                        locked_dices: locked_dices
                    });
                }
            }
        });
    }
}

function next() {
    deactivate_buttons()
    if (is_current_player === true) {
        socket.emit('next_player', {
            room_number: room_number,
            uuid: uuid,
        });
        let score = get_score()
        socket.emit('new_score', {
            room_number: room_number,
            uuid: uuid,
            score: score
        });
        is_current_player = false;
    }
}

function generatePlayerTables(nameList) {
    const ownuuid_part = uuid.substring(0, 8);
    let names = nameList.filter(user => user[1] !== ownuuid_part); // removing own username
    let numPlayers = names.length;

    for (let i = 1; i <= numPlayers; i++) {
        const tableBody = document.querySelector(`#Table${i} tbody`);

        if (tableBody.children.length === 0) {
            // switch id of table border to uuid_part
            const tableBorder = document.getElementById(`user_table${i}`);
            tableBorder.id = names[i - 1][1]; // array starts at 1, i at 1 / [[name, uuidpart],[name, uuidpart]]
            // set caption of table to name
            const tableCaption = document.querySelector(`#Table${i} caption`);
            tableCaption.innerHTML = names[i - 1][0]; // array starts at 1, i at 1 / [[name, uuidpart],[name, uuidpart]]

            for (let row = 1; row <= 12; row++) {
                let rowHtml = `<tr><th scope="row">${row}</th>`;

                for (let col = 1; col <= 10; col++) {
                    rowHtml += `<td id="${names[i - 1][1]}-${row}-${col}"></td>`;
                }

                rowHtml += `<th scope="row">${row}</th></tr>`;
                tableBody.innerHTML += rowHtml;
            }
        }
    }
}

function activate_buttons() {
    if (is_current_player === true) {
        document.getElementById('würfel').disabled = false;
        document.getElementById('next').disabled = false;
        for (let i = 1; i <= 6; i++) {
            document.getElementById(`lock${i}`).disabled = false;
        }
        for (let row = 1; row <= 12; row++) {
            for (let col = 1; col <= 10; col++) {
                document.getElementById(`${row}-${col}`).disabled = false;
                document.getElementById(`${row}-${col}`).parentElement.classList.add('active');
            }
        }
    }
}

function deactivate_buttons() {
    document.getElementById('next').disabled = true;
    document.getElementById('würfel').disabled = true;
    for (let i = 1; i <= 6; i++) {
        document.getElementById(`lock${i}`).disabled = true;
    }
    for (let row = 1; row <= 12; row++) {
        for (let col = 1; col <= 10; col++) {
            document.getElementById(`${row}-${col}`).disabled = true;
            document.getElementById(`${row}-${col}`).parentElement.classList.remove('active');
        }
    }
}

function get_score() {
    let score = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0, "11": 0, "12": 0}
    for (let number in score) {
        for (let i = 1; i <= 10; i++) {
            let checkbox = document.getElementById(`${number}-${i}`)
            if (checkbox.checked) {
                score[number] = score[number] + 1;
            }
        }
    }
    return score
}

function change_custom_border(userlist, current_player) {
    userlist.splice(userlist.indexOf(uuid_part), 1); // remove own uuid_part
    if (is_current_player === true) {
        document.getElementById("border_player_table").classList.add("custom_border");
    } else {
        if (document.getElementById("border_player_table").classList.contains("custom_border")) {
            document.getElementById("border_player_table").classList.remove("custom_border");
        }
    }
    for (let i = 0; i <= userlist.length - 1; i++) {
        if (document.getElementById(`${userlist[i]}`).classList.contains("custom_border")) {
            document.getElementById(`${userlist[i]}`).classList.remove("custom_border");
        }
        if (userlist[i] === current_player) {
            document.getElementById(`${userlist[i]}`).classList.add("custom_border");
        }
    }
}