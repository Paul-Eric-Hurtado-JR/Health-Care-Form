console.log("Patient registration JavaScript loaded");
const patient_registration_form = document.getElementById("patient_registration_form");
const status_message = document.getElementById("status_message");
const patient_username = document.getElementById("patient_username");
const patient_password = document.getElementById("patient_password");
const confirm_patient_password = document.getElementById("confirm_patient_password");
const patient_fname = document.getElementById("patient_fname");
const patient_lname = document.getElementById("patient_lname");
const patient_age = document.getElementById("patient_age");

patient_registration_form.addEventListener("submit", function(event) {
    console.log("Form submitted");
    event.preventDefault();

    function messageHandling(text){
        status_message.textContent = text;
        status_message.className = "error";
        setTimeout(() => {
            status_message.textContent = "";
            status_message.className = "";
        }, 5000);
    };

    const username = patient_username.value.trim();
    const password = patient_password.value;
    const confirm_password = confirm_patient_password.value;
    const firstname = patient_fname.value.trim();
    const lastname = patient_lname.value.trim();
    const Age = patient_age.value.trim();

    //checks to see if a value was entered
    if (username === ""){
        messageHandling("username is needed");
        return;
    }
    if (password === ""){
        messageHandling("password is needed");
        return;
    }
    if (password.length < 12) {
        messageHandling("Password must be at least 12 characters");
        return;
    }
    if (confirm_password === ""){
        messageHandling("password is needed");
        return;
    }
    if (firstname === ""){
        messageHandling("First name is needed");
        return;
    }
    if (lastname === ""){
        messageHandling("Last name is needed");
        return;
    }
    if (Age === ""){
        messageHandling("Age is needed");
        return;
    }

    const valide_age = Number(Age);

    if(!Number.isInteger(valide_age)){
        messageHandling("Age is not whole number");
        return;
    }
    if((valide_age < 0) || (valide_age > 105)){
        messageHandling("Age is not valid");
        return;
    }
    if(password !== confirm_password){
        messageHandling("Passwords do not match")
        return;
    }
    //formats the name to have a capital for the first letter in the name and the rest to be lower case
    const formatedfirstname = firstname.charAt(0).toUpperCase() + firstname.slice(1).toLowerCase();
    const fromatedlastname = lastname.charAt(0).toUpperCase() + lastname.slice(1).toLowerCase();

    const patient_info = {
        username: username,
        password: password,
        fname: formatedfirstname,
        lname: fromatedlastname,
        age: valide_age
    };
    //sends the information to backend
    fetch("/patients-info", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(patient_info)
    })
    //verifys everything is good
    .then(async response => {
    //checks if response is anything other than 2XX
    if(!response.ok) {
        const error_message = await response.json();
        throw new Error(error_message.message);
    }   
        return response.json();
    })
    //if everything is succesful then provide message and reset page
    .then(data => {
        status_message.textContent = data.message;
        status_message.className = "success";
        patient_registration_form.reset();
        setTimeout(() => {
            window.location.href = "/"
        }, 2000);
    })
    //if anything went wrong provides the error
    .catch(error =>{
        status_message.textContent = error.message;
        status_message.className = "error";
        setTimeout(() => {
            status_message.textContent = "";
            status_message.className = "";
        }, 2000);
    });
});