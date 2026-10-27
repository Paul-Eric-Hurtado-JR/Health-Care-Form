const form = document.getElementById("admin_form");
const display_message = document.getElementById("display_message");

form.addEventListener("submit", function(event) {
    event.preventDefault();

    const username = document.querySelector('[name="username"]').value;
    const password = document.querySelector('[name="password"]').value;

    const Login = {
        uname: username,
        pw: password
    };

    fetch("/admin/login", {
        method: "POST",
        headers: {"content-type": "application/json"
        },
        body: JSON.stringify(Login)
    })
    .then(async response => {
    //checks if response is anything other than 2XX
        if(!response.ok) {
            const error_message = await response.json();
            throw new Error(error_message.message);
        }   
        return response.json();
    })
    .then(data => {
        display_message.textContent = data.message;
        window.location.href = data.redirect;
    })
    .catch(error => {
        display_message.textContent = error.message;
    })
});