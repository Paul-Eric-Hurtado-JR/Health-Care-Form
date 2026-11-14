    const firstname = document.getElementById("patient_fname");
    const lastname = document.getElementById("patient_lname");
    const patient_age = document.getElementById("patient_age");
    const status_message = document.getElementById("status_message");
    const submit_button = document.getElementById("submit_button");
    const csrf_token = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

    load_update_patient();
    //loads current patient information into slots
    function load_update_patient() {
        fetch("/patient/my-record")
            .then(async response => {
                const data = await response.json();

                if(!response.ok){
                    throw new Error(data.message || "Failed to load patients info");
                }
                return data;
            })
            .then(data => {
                const patient = data.Patient;
                firstname.value = patient.Firstname;
                lastname.value = patient.Lastname;
                patient_age.value = patient.age;
            })
            .catch(error => {
                status_message.textContent = error.message;
            });
        }

    const form = document.getElementById("patient_form");
    //updates the patient information
    form.addEventListener("submit", function(event){
        event.preventDefault();

        submit_button.disabled = true;
        const patient = {
            fname: firstname.value.trim(),
            lname: lastname.value.trim(),
            age: Number(patient_age.value)
        }

        fetch("/patient/update-my-record",{
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrf_token
            },
            body: JSON.stringify(patient)
        })                
        
        .then(async response => {
        const data = await response.json();
        //checks if response is anything other than 2XX
            if(!response.ok) {

                throw new Error(data.message || "Couldn't update information");
            }   
            return data;
        })
        .then(data => {
            status_message.textContent = data.message;
        })
        .catch(error => {
            status_message.textContent = error.message;
        })
        .finally(() => {
            submit_button.disabled = false;
        });
    })

    const back_to_patient_dashboard = document.getElementById("back_to_patient_dashboard");
    //moves back to patient dashboard when button is clicked
    back_to_patient_dashboard.addEventListener("click", function(){
        window.location.href = "/patient/dashboard";
    })