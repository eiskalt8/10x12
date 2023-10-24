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