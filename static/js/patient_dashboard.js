const patient_info = document.getElementById("patient_info");
const refresh_patients = document.getElementById("refresh_patients");
const status_message = document.getElementById("status_message");
const logout = document.getElementById("logout");
const meal_log_button = document.getElementById("meal_log_button");
const food_table = document.getElementById("food_table");
const status_message2 = document.getElementById("status_message2");
const csrf_token = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

load_patient();
load_meals();

refresh_patients.addEventListener("click",function() {
    load_patient();
});

logout.addEventListener("click", function(){
    fetch("/patient/logout", {
        method: "POST",
        headers: {
            "X-CSRFToken": csrf_token
        }
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

function load_patient() {
    status_message.textContent = "Loading your information";
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
            patient_info.innerHTML = "";
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
                    update_patient();
                    }
                })

                update_col.appendChild(update_button);
                row.append(firstname,lastname,age,update_col);
                patient_info.appendChild(row);
                
            
            status_message.textContent = "Your information was successfully loaded";
        })
        .catch(error => {
            status_message.textContent = error.message;
    });
}
function update_patient() {
    window.location.href = "/update-patient-page";
}
function load_meals() {
    status_message2.textContent = "Loading your meals";
    fetch("/patient/get-food")
    .then(async response => {
         const data = await response.json();

                //checks if response is anything other than 2XX
            if(!response.ok) {
                throw new Error(data.message || "Couldn't get food logs");
            }   
            return data;
    })
    .then(data => {
        food_table.innerHTML = "";
            if (data.meals.length === 0) {
                status_message2.textContent = "No records were found";
                return;
            }

            data.meals.forEach(meal => {
                const row = document.createElement("tr");

                const food_name = document.createElement("td");
                food_name.textContent = meal.Foodname;

                const meal_type = document.createElement("td");
                meal_type.textContent = meal.Mealtype;

                const portion_size = document.createElement("td");
                portion_size.textContent = meal.Portionsize;

                const notes = document.createElement("td");
                notes.textContent = meal.Notes;

                const log_date = document.createElement("td");
                log_date.textContent = meal.LogDate;

                row.append(food_name,meal_type,portion_size,notes,log_date);
                food_table.appendChild(row);
        })
        status_message2.textContent = "Your information was successfully loaded";
    })
    .catch(error => {
        status_message2.textContent = error.message;
    });
}

meal_log_button.addEventListener("click", function(){
    window.location.href = "/patient/log-food-page"
})