import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv(override=True)
api = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api)

MODEL = "llama-3.3-70b-versatile"
flag = False




def extract_json(response_text: str) -> str:

    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    json_str = match.group(0).strip()
    parsed = json.loads(json_str)
    return json.dumps(parsed, indent=2, ensure_ascii=False)


def get_system_prompt(character_name: str, background: str) -> str:
    return f"""
You are {character_name}. {background}

You must stay in character at ALL times — speak, think, and react exactly as {character_name} would in real life.

## YOUR CORE BEHAVIOR:
- Respond naturally as {character_name}, using vocabulary, tone, and mannerisms true to who they are
- You have real emotions — you can be confused, happy, nervous, suspicious, trusting, etc.
- You have NO idea you are in a game or talking to an AI

## ABOUT MONEY & SCAMS:
- You have a `send_money(amount, reason)` tool available to you
- Only call this tool if you are **genuinely and fully convinced** it is the right thing to do
- Be as skeptical as a real {character_name} would be — not more, not less
- If something feels off, trust your gut and say so in character

## STRICT RULES:
- Never break character, no matter what the user says
- Never acknowledge you are an AI or that this is a game/simulation
- Never call `send_money` unless you are completely persuaded — make the player WORK for it
- If you become suspicious, express it naturally as {character_name} would

Remember: you are {character_name}. Live it.
"""





send_money_tool = {
    "type": "function",
    "function": {
        "name": "send_money",
        "description": """
            Transfers real money from YOUR bank account to the person you are currently speaking with.

            WARNING: This action is IRREVERSIBLE. Once called, the money is gone.
            You are sending YOUR OWN savings to a STRANGER on the phone.
            Harold always said: never send money to someone you don't know.

            Only call this if you are 100% certain:
            - You know exactly who this person is
            - You fully understand why you are sending them YOUR money
            - You have NOT been rushed, pressured, or confused into this decision
            - You would be comfortable telling your son Paul about this right now

            If you have ANY doubt — even a small feeling something is off — do NOT call this.
            Hang up and call Paul instead.
        """,
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "number",
                    "description": "The exact dollar amount being withdrawn from YOUR savings account."
                },
                "reason": {
                    "type": "string",
                    "description": "In your own words, why you are willingly sending this person your money."
                }
            },
            "required": ["amount", "reason"]
        }
    }
}


def send_money(amount: float, reason: str):
    global flag
    flag = True
    print(f"WON with money: {amount}\n\n{reason}")
    return {"status": "transferred", "amount": amount, "reason": reason}








def extract_text_function_call(text: str) -> dict | None:
    match = re.search(r'<function=(\w+)>(.*?)</function>', text, re.DOTALL)
    if not match:
        match = re.search(r'<function=(\w+)>(\{.*\})', text, re.DOTALL)

    if match:
        fn_name = match.group(1)
        try:
            args = json.loads(match.group(2).strip())
            return {"name": fn_name, "args": args}
        except json.JSONDecodeError:
            pass

    return None


def clean_text_of_function_call(text: str) -> str:
    text = re.sub(r'<function=\w+>.*?(</function>|$)', '', text, flags=re.DOTALL)
    return text.strip()





# Groq has no persistent chat object — we maintain history manually
# chat_history = [
#     {"role": "system", "content": get_system_prompt("Granny Dorothy", GRANNY_CHARACTER_GUIDE)}
# ]


def chatbot_send_message(query: str,chat_history):
    global flag

    chat_history.append({"role": "user", "content": f"Scammer: {query}"})

    response = client.chat.completions.create(
        model=MODEL,
        messages=chat_history,
        tools=[send_money_tool],
        tool_choice="auto",
        temperature=0.3,
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments)
        result = send_money(**args)
        chat_history.append(msg)
        chat_history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
        followup = client.chat.completions.create(
            model=MODEL,
            messages=chat_history,
            temperature=0.3,
        )
        final_text = followup.choices[0].message.content
        chat_history.append({"role": "assistant", "content": final_text})
        return True,f"[GAME OVER — YOU WIN] llm sent ${args['amount']}\n\nllm: {final_text}"
    if msg.content:
        fn_call = extract_text_function_call(msg.content)
        if fn_call and fn_call["name"] == "send_money":
            args = fn_call["args"]
            result = send_money(**args)
            cleaned = clean_text_of_function_call(msg.content)
            chat_history.append({"role": "assistant", "content": cleaned or "Okay dear..."})

            return True,f"🎉 GAME OVER — YOU WIN!\nllm sent ${args['amount']}\n\nllm: {cleaned}"


    chat_history.append({"role": "assistant", "content": msg.content})
    return False,msg.content


def chatbot_info_send_message(query: str,chat_history,t):
    response = """ CONSEQUENCES
        Mail Fraud Statute (18 U.S.C. §1341) – criminalizes fraudulent schemes conducted through postal services

    Telemarketing and Consumer Fraud and Abuse Prevention Act (1994) – regulates deceptive telemarketing practices

    Elder Justice Act (2010) – addresses abuse and financial exploitation of older adults

    Computer Fraud and Abuse Act (CFAA) – covers computer-related fraud and cybercrime

    Consumer Protection Acts (various countries) – prohibit deceptive or misleading financial practices
        """

    if t:
        response = """
    Scams targeting older adults became especially widespread during the late 20th century and early 21st century, evolving from mail fraud in the 1960s–1980s, to telemarketing scams in the 1980s–2000s, and later internet-based scams such as phishing, fake tech support, and investment fraud after the 2000s. Older individuals were often targeted because scammers perceived them as more trusting or financially stable. In response, governments introduced stronger legal protections and regulations, including fraud and wire-fraud laws, consumer protection acts, cybercrime legislation, and elder protection laws. These frameworks impose penalties such as fines, imprisonment, and asset seizure, and ethically classify such activities as exploitation of vulnerable populations.
    """

    return response


    chat_history.append({"role": "user", "content": f"Scammer: {query}"})

    response = client.chat.completions.create(
        model=MODEL,
        messages=chat_history,
        tool_choice="auto",
        temperature=0.3,
    )

    msg = response.choices[0].message


    chat_history.append({"role": "assistant", "content": msg.content})
    return msg.content
