import requests
import sys
from datetime import date

MODEL_ID = "8w6yyp2q"
BASETEN_API_KEY = "YMKFudUr.FcjOTi13DlaR3ZtCbBIumoXeqFJy25yx" # Gotten from Discord
     

def IsAppropriate(email, emailer):
    #check if emailer is institution or meeting scheduling service
    if "noreply" or "no-reply" in emailer:
        return(False)

    quickCheck = [
        {"role": "system", "content": f"If the email is coherent, appropriate, and scheduling related, output just the word 'yes'. DO NOT OUTPUT YES IF THE EMAIL DOES NOT RELATE DIRECTLY TO SCHEDULING AND REQUIRE A RESPONSE. The email is {email}"},
    ]

    payload = {
        "messages": quickCheck,
        "stream": True,
        "max_tokens": 4098,
        "temperature": 0.9
    }

    res = requests.post(
        f"https://model-{MODEL_ID}.api.baseten.co/production/predict",
        headers={"Authorization": f"Api-Key {BASETEN_API_KEY}"},
        json=payload,
        stream=False
    )

    # Create a string for the tokens being generated checking the email
    a = ""
    for content in res.iter_content():
        a += (content.decode("utf-8"))

    if a == "yes":
        return True

    else:
        return False
