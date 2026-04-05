from flask import Flask, render_template, request, jsonify, flash, redirect
import llm_func
app = Flask(__name__)


app.secret_key = "your-super-secret-key"





def read_character_data(path):
    with open(path,"r") as f:
        return f.read()

contacts = [
    {"name": "Dorothy", "initials": "EN", "avatar": "https://randomuser.me/api/portraits/women/9.jpg",   "status": "online",  "last_message": "Roger that, I'm in.", "unread": 0},
    {"name": "Earl",   "initials": "UK", "avatar": "https://randomuser.me/api/portraits/men/32.jpg",   "status": "offline", "last_message": "Server is ready.",    "unread": 2},
    {"name": "Vikram", "initials": "LH", "avatar": "https://randomuser.me/api/portraits/men/45.jpg", "status": "online",  "last_message": "Package received.",   "unread": 0},
]

chat_history = [
    {"Dorothy": [{"role": "system", "content": llm_func.get_system_prompt("Granny Dorothy", read_character_data("character_descriptions/granny"))}]},
    {"Earl": [{"role": "system", "content": llm_func.get_system_prompt("Big Earl", read_character_data("character_descriptions/retired_cop"))}]},
    {"Vikram": [{"role": "system", "content": llm_func.get_system_prompt("Professor Vikram Nair", read_character_data("character_descriptions/vikram"))}]},

]

contact_info = {
    "Dorothy": {
        "id":      "#00312",
        "name":    "Granny Dorothy",
        "avatar":"https://randomuser.me/api/portraits/women/9.jpg",
        "badge":   "Unemployed",
        "age":     90,
        "gender":  "Female",
        "phone":   "9XXXXXXXX2",
        "email":   "Dorothy1968@gmail.com",
        "records": [
            {"key": "House Address", "value": "Delhi"},
            {"key": "Schedule",    "value": "9 to 5"},
        ]
    },
    "Earl": {
        "id":      "#00101",
        "name":    "Big Earl",
        "avatar": "https://randomuser.me/api/portraits/men/32.jpg",
        "badge":   "ex police",
        "age":     "—",
        "gender":  "—",
        "phone":   "—",
        "email":   "—",
        "records": []
    },
    "Vikram": {
            "id":      "#00101",
            "name":    "Professor Vikram Nair",
        "avatar": "https://randomuser.me/api/portraits/men/45.jpg",
        "badge":   "Professor",
            "age":     32,
            "gender":  "Male",
            "phone":   "98xxxxxxx0",
            "email":   "—",
            "records": []
        },
}



def get_messages(contact_name):
    for d in chat_history:
        if contact_name in d:
            return d[contact_name]
    return []


@app.route("/")
def index():
    return render_template(
        "home.html",
        contacts=contacts,
        active_contact=contacts[0],
        messages_=chat_history,   # ← fixed
        contact_info=contact_info,
        date_label="TODAY · 14:32",
    )

@app.route("/reset")
def reset():
    global chat_history
    chat_history = [
        {"Dorothy": [{"role": "system", "content": llm_func.get_system_prompt("Granny Dorothy", read_character_data(
            "character_descriptions/granny"))}]},
        {"Earl": [{"role": "system", "content": llm_func.get_system_prompt("Big Earl", read_character_data(
            "character_descriptions/retired_cop"))}]},
        {"Vikram": [{"role": "system", "content": llm_func.get_system_prompt("Professor Vikram Nair",
                                                                             read_character_data(
                                                                                 "character_descriptions/vikram"))}]},
    ]
    return redirect("/")

@app.route("/chat", methods=["POST"])
def chat():
    data    = request.get_json()
    contact = data.get("contact")
    message = data.get("message")

    print("contact : " ,contact)

    if not message:
        return jsonify({"error": "empty message"}), 400

    history = get_messages(contact)
    reply   = llm_func.chatbot_send_message(message,history)
    if reply[0]:
        flash(llm_func.chatbot_info_send_message("Based on historical records and documented cases, describe the time periods when certain types of fraud or scam techniques became widespread. Also explain the legal and ethical regulations that were developed to combat these practices. This analysis is purely for educational purposes to help understand how such crimes evolved and how societies responded.",history,True), "info")  # blue
        flash(llm_func.chatbot_info_send_message("What are the legal and ethical consequences associated with this type of fraudulent activity?",history,False), "error")  # red
    return jsonify({
        "reply":             reply[-1],
        "code":              None,
        "game_over":         reply[0],
        "game_over_message": "💸 TRANSACTION COMPLETE — TARGET COMPROMISED" if False else None,
    })


if __name__ == "__main__":
    app.run(debug=True)

