import requests
from datetime import date

MODEL_ID = "8w6yyp2q"
BASETEN_API_KEY = "YMKFudUr.FcjOTi13DlaR3ZtCbBIumoXeqFJy25yx" # Gotten from Discord
     

def checkFree(email, unavailability, emailsentdate):
    now = date.today()

    prompt = [
        {"role": "system", "content": f"""
        Today is {now}. 
        You are busy and unavailable during the times {unavailability}.
        You received this email related to scheduling on {emailsentdate}: {email} \n
        Respond with ONLY the word 'yes' if you are available at the time discussed in the email.
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
    a = ""
    for content in res.iter_content():
        a += (content.decode("utf-8"))

    if a == "yes":
        # find and store the time of the event mentioned in the email by asking the LLM to do it
        prompt1 = [
            {"role": "system", "content": f"""
            Today is {now}. 
            You are busy and unavailable during the times {unavailability}.
            You received this email related to scheduling on {emailsentdate}: {email} \n
            Respond with ONLY the time of the event mentioned in the email in the format [Hour:Minuteam to Hour:Minutepm].
            """},
        ]
        payload1 = {
        "messages": prompt1,
        "stream": True,
        "max_tokens": 4098,
        "temperature": 0.9
        }
        res1 = requests.post(
        f"https://model-{MODEL_ID}.api.baseten.co/production/predict",
        headers={"Authorization": f"Api-Key {BASETEN_API_KEY}"},
        json=payload1,
        stream=False
        )
        # make 2 string variables, the first one is the start time and the second one is the end time
        start_time, end_time = res1.text.split(" to ")
        
        return start_time, end_time

    else:
        #checkFree is False and your schedule is not open at that time
        return False