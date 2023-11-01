/*function safe_input() {
    const input = document.getElementById(inputid).value;
    localStorage.setItem(inputid, input);
}

function get_input(inputid) {
    return localStorage.getItem(inputid)
}
*/
//handle name
function safe_name() {
    const name = document.getElementById("username-input").value
    localStorage.setItem("username", name)

}

function get_name() {
    return localStorage.getItem("username")
}

//create room
function create_room() {

}

//join existing room
//create room
function join_room() {

}

//Darkmode
if (localStorage.getItem("darkMode") === true) {
            document.documentElement.setAttribute('data-bs-theme', 'dark')
    }

document.getElementById('btnSwitch').addEventListener('click', () => {
    if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
        document.documentElement.setAttribute('data-bs-theme', 'light')
        localStorage.setItem("darkMode", false)
    } else {
        document.documentElement.setAttribute('data-bs-theme', 'dark')
        localStorage.setItem("darkMode", true)
    }
})