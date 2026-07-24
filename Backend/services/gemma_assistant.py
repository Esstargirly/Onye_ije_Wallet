import os
from dotenv import load_dotenv
load_dotenv()

from google import genai
from google.genai import types
from services import wallet_service

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemma-4-26b-a4b-it"

_pending_actions = {}

# Tool definitions: what Gemma is allowed to call
check_balance_fn = {
    "name": "check_balance",
    "description": "Check the user's current wallet balance in Naira.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "The user's ID"}
        },
        "required": ["user_id"],
    },
}

top_up_wallet_fn = {
    "name": "top_up_wallet",
    "description": "Add money to the user's wallet.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "The user's ID"},
            "amount": {"type": "number", "description": "Amount in Naira to add"},
        },
        "required": ["user_id", "amount"],
    },
}

check_sufficient_fare_fn = {
    "name": "check_sufficient_fare",
    "description": "Check if the user has enough balance to cover a given fare.",
    "parameters": {
        "type": "object",
        "properties": {
            "user_id": {"type": "integer", "description": "The user's ID"},
            "fare_amount": {"type": "number", "description": "The fare amount to check against"},
        },
        "required": ["user_id", "fare_amount"],
    },
}

tools = types.Tool(function_declarations=[
    check_balance_fn,
    top_up_wallet_fn,
    check_sufficient_fare_fn,
])


# Executing whatever Gemma decides to call

def execute_function(name, args):
    try:
        if name == "check_balance":
            return {"balance": wallet_service.get_balance(args["user_id"])}

        elif name == "top_up_wallet":
            user_id, amount = args["user_id"], args["amount"]
            pending = _pending_actions.get(user_id)

            if pending and pending["type"] == "top_up" and pending["amount"] == amount:
                del _pending_actions[user_id]
                new_balance = wallet_service.top_up(user_id, amount)
                return {"success": True, "new_balance": new_balance}

            _pending_actions[user_id] = {"type": "top_up", "amount": amount}
            return {
                "requires_confirmation": True,
                "message": f"Please confirm: add \u20a6{amount:.2f} to your wallet?",
            }

        elif name == "check_sufficient_fare":
            return wallet_service.check_sufficient_fare(args["user_id"], args["fare_amount"])

        return {"error": "unknown function"}
    except ValueError as e:
        return {"error": str(e)}


SYSTEM_INSTRUCTION = (
    "You are the Onye Ije Wallet assistant. Users ask about their transit "
    "wallet balance, top-ups, and fares in plain language. When a function "
    "result includes requires_confirmation, relay the message to the user "
    "exactly and stop — do not call the function again until the user "
    "replies with a clear yes/confirm. Keep replies short and in plain "
    "English suited for a mobile chat screen."
)

def ask_gemma(user_message, user_id):
    context_note = ""
    pending = _pending_actions.get(user_id)
    if pending and pending["type"] == "top_up":
        context_note = (
            f" (Context: there is a pending top-up of \u20a6{pending['amount']:.2f} "
            f"awaiting the user's confirmation. If this message confirms it, "
            f"call top_up_wallet with amount={pending['amount']}.)"
        )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=f"(user_id={user_id}) {user_message}{context_note}")]
        )
    ]


    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            tools=[tools],
            system_instruction=SYSTEM_INSTRUCTION,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            ),
        ),
    )

    part = response.candidates[0].content.parts[0]

    if part.function_call:
        fn_name = part.function_call.name
        fn_args = dict(part.function_call.args)
        result = execute_function(fn_name, fn_args)

        contents.append(response.candidates[0].content)
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(
                    function_response=types.FunctionResponse(
                        name=fn_name,
                        response=result,
                    )
                )]
            )
        )

        final_response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                tools=[tools],
                system_instruction=SYSTEM_INSTRUCTION,
            ),
        )
        return final_response.text

    return response.text