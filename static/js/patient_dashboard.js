const table_body = document.getElementById("table_body");
const refresh_patients = document.getElementById("refresh_patients");
const status_message = document.getElementById("status_message");
const logout = document.getElementById("logout");

load_patients();

refresh_patients.addEventListener("click",function() {
    load_patients();
});

logout.addEventListener("click", function(){
    fetch("/patient/logout", {
        method: "POST"
    })
    .then(async response =>{
        const data = await response.json();
        //checks if response is anything other than 2XX
        if(!response.ok) {
            throw new Error(data.message || "Logout failed");
        }   
        window.location.href = "/";
    })
    .catch(error => {
        console.error("Logout error", error)
        status_message.textContent = "Logout Failed"
    });
})

function load_patients() {
    status_message.textcontent = "Loading your information";
    fetch("/patient/my-record")
        .then(async response => {
        //checks if response is anything other than 2XX
            if(!response.ok) {
                const error_message = await response.json();
                throw new Error(error_message.message);
            }   
            return response.json();
        })
        .then(data => {
            table_body.innerHTML = "";
            const patient = data.Patient;

            const row = document.createElement("tr");

            const firstname = document.createElement("td");
            firstname.textContent = patient.Firstname;

            const lastname = document.createElement("td");
            lastname.textContent = patient.Lastname;

            const age = document.createElement("td");
            age.textContent = patient.age;

            const update_col = document.createElement("td");
            const update_button = document.createElement("button");
            update_button.textContent = "Update";

            update_button.addEventListener("click", function () {
                const confirm_update = confirm("Are you sure you want to update this person. You will be redirected to a differnt page.");

                if(confirm_update){
                    update_patient(patient.PatientID);
                    }
                })

                update_col.appendChild(update_button);
                row.append(firstname,lastname,age,update_col);
                table_body.appendChild(row);
                
            
            status_message.textContent = "Your information was successfully loaded";
        })
        .catch(error => {
            status_message.textContent = error.message;
    });
}
function update_patient(patient_ID) {
    window.location.href = `/update-patient-page/${patient_ID}`;
}