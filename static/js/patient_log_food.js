const log_food_form = document.getElementById("log_food_form");
const meal_name = document.getElementById("meal_name");
const meal_type = document.getElementById("meal_type");
const serving_size = document.getElementById("serving_size");
const meal_note = document.getElementById("meal_note");
const meal_date = document.getElementById("meal_date");
const status_message = document.getElementById("status_message");
const submit_button = document.getElementById("submit_button");
const back_to_dashboard = document.getElementById("back_to_dashboard");
const csrf_token = document.querySelector('meta[name="csrf-token"]').getAttribute("content");

log_food_form.addEventListener("submit", function(event){
    event.preventDefault();
    submit_button.disabled = true;

    const food_name = meal_name.value.trim();
    const food_type = meal_type.value;
    const food_size = serving_size.value.trim();
    const food_note = meal_note.value.trim();
    const food_date = meal_date.value;

    const food_info = {
        foodName: food_name,
        mealType: food_type,
        portionSize: food_size,
        notes: food_note,
        logDate: food_date
    }

    fetch("/patient/food-log",{
        method: "POST",
        headers: {
            "content-type": "application/JSON",
            "X-CSRFToken": csrf_token
        },
        body: JSON.stringify(food_info)
    })
    .then(async response => {
        const data = await response.json()
        //checks if response is anything other than 2XX
        if(!response.ok) {
            throw new Error(data.message || "Failed to log food");
        }   
        return data;
    })
    .then(data => {
        status_message.textContent = data.message;
        log_food_form.reset();
    })
    .catch(error => {
        status_message.textContent = error.message;
    })
    .finally(() => {
    submit_button.disabled = false;
    });
})

back_to_dashboard.addEventListener("click", function(){
    window.location.href = "/patient/dashboard";
})