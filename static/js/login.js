const login_form = document.getElementById("login_form");
const status_message = document.getElementById("status_message");

login_form.addEventListener("submit", function(event) {
    event.preventDefault();

    const username = document.querySelector('[name="username"]').value;
    const password = document.querySelector('[name="password"]').value;

    const Login = {
        uname: username,
        pw: password
    };

    fetch("/login", {
        method: "POST",
        headers: {"content-type": "application/json"
        },
        body: JSON.stringify(Login)
    })
    .then(async response => {            
        const data = await response.json();
    //checks if response is anything other than 2XX
        if(!response.ok) {
            throw new Error(data.message || "Couldn't login");
        }   
        return data;
    })
    .then(data => {
        status_message.textContent = data.message;
        window.location.href = data.redirect;
    })
    .catch(error => {
        status_message.textContent = error.message;
    })
});