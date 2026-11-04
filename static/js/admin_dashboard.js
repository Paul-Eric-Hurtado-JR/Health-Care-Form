const table_body = document.getElementById("table_body");
const refresh_patients = document.getElementById("refresh_patients");
const status_message = document.getElementById("status_message");
const logout = document.getElementById("logout");
const searchbar_form = document.getElementById("searchbar_form");
const searchbar = document.getElementById("searchbar");
load_patients();

refresh_patients.addEventListener("click",function() {
    searchbar.value = "";
    load_patients();
});

logout.addEventListener("click", function(){
    fetch("/admin/logout", {
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
searchbar_form.addEventListener("submit", function(){
        event.preventDefault();
        const search = searchbar.value.trim();
        load_patients(search);
})
function load_patients(search_value="") {
    status_message.textcontent = "Loading Patients";
    fetch(`/admin/retrieve-patients?search=${encodeURIComponent(search_value)}`)
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
            if (data.Patient.length === 0) {
                status_message.textContent = "No records were found";
                return;
            }

            data.Patient.forEach(Patient => {
                const row = document.createElement("tr");

                const patientID = document.createElement("td");
                patientID.textContent = Patient[0];

                const firstname = document.createElement("td");
                firstname.textContent = Patient[1];

                const lastname = document.createElement("td");
                lastname.textContent = Patient[2];

                const age = document.createElement("td");
                age.textContent = Patient[3];

                const update_col = document.createElement("td");
                const update_button = document.createElement("button");
                update_button.textContent = "Update";

                const delete_col = document.createElement("td");
                const delete_button = document.createElement("button");
                delete_button.textContent = "Delete";

                update_button.addEventListener("click", function () {
                    const confirm_update = confirm("Are you sure you want to update this person. You will be redirected to a differnt page.");

                    if(confirm_update){
                        update_patient(Patient[0]);
                    }
                })

                delete_button.addEventListener("click", function() {
                    const confirm_deletion = confirm("Are you sure you want to delete this person.");

                    if(confirm_deletion){
                        delete_patient(Patient[0]);
                    }
                })
                update_col.appendChild(update_button);
                delete_col.appendChild(delete_button);
                row.append(patientID,firstname,lastname,age,update_col,delete_col);
                table_body.appendChild(row);
                
            });
            status_message.textContent = `Loaded ${data.Patient.length} patient records`;
        })
        .catch(error => {
            status_message.textContent = error.message;
    });
}

function update_patient(patient_ID) {
    window.location.href = `/update-patient-page/${patient_ID}`;
}

function delete_patient(patient_ID){
    fetch(`/delete-patient-record/${patient_ID}`,{
        method: "DELETE"
    })
    .then(async response => {
        const data = await response.json();
        //checks if response is anything other than 2XX
            if(!response.ok) {
                throw new Error(data.message || "Couldn't delete patient");
            }   
            status_message.textContent = data.message;
            load_patients(searchbar.value.trim());
        })
    .catch(error => {
        status_message.textContent = error.message;
    });
}