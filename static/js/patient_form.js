const form = document.getElementById("patient_form");
const message = document.getElementById("message");

form.addEventListener("submit", function(event) {
    event.preventDefault();

    function messageHandling(text){
        message.textContent = text;
        message.className = "error";
        setTimeout(() => {
            message.textContent = "";
            message.className = "";
        }, 5000);
    };
    const firstname = document.querySelector('[name="fname"]').value;
    const lastname = document.querySelector('[name="lname"]').value;
    const age = document.querySelector('[name="age"]').value;

    //checks to see if a value was entered
    if (firstname.trim() === ""){
        messageHandling("First name is needed");
        return;
    }
    if (lastname.trim() === ""){
        messageHandling("Last name is needed");
        return;
    }
    if (age.trim() === ""){
        messageHandling("Age is needed");
        return;
    }

    const valide_age = Number(age);

    if(!Number.isInteger(valide_age)){
        messageHandling("Age is not whole number");
    }
    if((valide_age < 0) || (valide_age > 150)){
        messageHandling("Age is not valid");
    }
    //formats the name to have a capital for the first letter in the name and the rest to be lower case
    const formatedfirstname = firstname.charAt(0).toUpperCase() + firstname.slice(1).toLowerCase();
    const fromatedlastname = lastname.charAt(0).toUpperCase() + lastname.slice(1).toLowerCase();

    const patient_info = {
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
        message.textContent = data.message;
        message.className = "success";
        form.reset();
        setTimeout(() => {
            message.textContent = "";
            message.className = "";
        }, 5000);
    })
    //if anything went wrong provides the error
    .catch(error =>{
        message.textContent = error.message;
        message.className = "error";
        setTimeout(() => {
            message.textContent = "";
            message.className = "";
        }, 5000);
    });
});