const table_body = document.getElementById("table_body");
const refresh_patients = document.getElementById("refresh_patients");
const status_message = document.getElementById("status_message");
const logout = document.getElementById("logout");

load_patients();

refresh_patients.addEventListener("click",load_patients);

logout.addEventListener("click", function(){
    fetch("/admin/logout", {
        method: "POST"
    })
    .then(async response =>{
        const data = await response.json;
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
    status_message.textcontent = "Loading Patients";
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
            status_message.textcontent = error.message;
    });
}