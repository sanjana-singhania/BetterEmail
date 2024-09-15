import requests
from datetime import date

MODEL_ID = "8w6yyp2q"
BASETEN_API_KEY = "YMKFudUr.FcjOTi13DlaR3ZtCbBIumoXeqFJy25yx" # Gotten from Discord
     

def generateRescheduleEmail(email, name, unavailability, emailsentdate, recipientName):
    now = date.today()

    prompt = [
        {"role": "system", "content": f"""
        Today is {now}. 
        You are busy and unavailable during the times {unavailability}.
        You received this email related to scheduling on {emailsentdate}: {email} \n
        Your name is {name}.
        Send a brief and highly-professional email to {recipientName} to reschedule for another time when you aren't unavailable.
        """},
    ]

    payload = {
        "messages": prompt,
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
    response = ""
    for content in res.iter_content():
        a += (content.decode("utf-8"))    
    
    return(response)


def generateConfirmationEmail(email, name, unavailability, emailsentdate, recipientName):
    now = date.today()

    prompt = [
        {"role": "system", "content": f"""
        Today is {now}. 
        You are busy and unavailable during the times {unavailability}.
        You received this email related to scheduling on {emailsentdate}: {email} \n
        Your name is {name}.
        Send a brief and highly-professional email to {recipientName} to confirm that you are available to attend at the planned time.
        """},
    ]

    payload = {
        "messages": prompt,
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
    response = ""
    for content in res.iter_content():
        a += (content.decode("utf-8"))
    
    return(response)
