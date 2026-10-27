import requests

patient = {
    "fname": "Paul",
    "lname": "Hurtado",
    "age": 20
}

response = requests.get("http://127.0.0.1:5000/patient-display/1", 
                        json = patient
                        )

print(response.text)