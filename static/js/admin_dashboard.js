const table_body = document.getElementById("table_body");
const refresh_patients = document.getElementById("refresh_patients");
const table_status = document.getElementById("table_status");

load_patients();

refresh_patients.addEventListener("click",load_patients);

function load_patients() {
    table_status.textcontent = "Loading Patients"
    fetch("/admin/retrieve-patients")

.then(async response => {
    //checks if response is anything other than 2XX
        if(!response.ok) {
            const error_message = await response.json();
            throw new Error(error_message.message);
        }   
        return response.json();
    })
.then(data => {
    console.log(data);
})
.catch(error => {
    table_status.textcontent = error.message;
});
}