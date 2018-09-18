import requests
import json
from flask import Flask, request

app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages' #URL for facebook API
VERIFY_TOKEN = 'Ba7QQUtvZALjNKhIqZTR0wPtxuk/Av4LeXYl6ALAGtM'# <paste your verify token here>
PAGE_ACCESS_TOKEN = "EAAkWmiNcJY0BAJaP6pDRaqc84LuipKWzfD5SbyGMoQ1FpZCMaj43xQ90sSrQo1PJ4wEoDhDW7JsPqFWPpeXcdON8GIfGsg79XzkZBveB3A1gIkXFnpydxb6WeAzoZCNTWNsbZCkE65ZB0MFReR6o4ZBAKTGjwIxAhxxCFrpaSXsgZDZD"# paste your page access token here>"

#verifies the token if valid to give access to the webhook to function
def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

#Check if the message is a message from the user
def is_user_message(message):
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))

#Formulate a response to the user and pass it on to a function that sends it.
def respond(sender, message):
    response = main(sender, message)
    send_message(sender, response)

#main functions that flask use to process message
@app.route("/webhook", methods=['GET','POST'])
def listen():
    if request.method == 'GET':
        return verify_webhook(request)


    if request.method == 'POST':
        payload = request.get_json()
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id,text)
                return "ok", 200

#send the message response to facebook
def send_message(recipient_id, text):
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        }
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }
    payload = json.dumps(payload)

    response = requests.post(
        FB_API_URL,
        headers=headers,
        params=auth,
        data=payload
    )

    return response

#function that searches with LUIS for the correct bot to answer
def choice(user, recipient):
    headers = {'Content-Type': 'application/json'}

    message = user
    minimumscore = .95
    payload = {
        "inputTranscript": message,
        "minScore": minimumscore
    }
    payload= json.dumps(payload)

    #---- Sending a request to the LUIS for best bot-------------
    response = requests.request("POST", "https://yly787ovr6.execute-api.us-east-1.amazonaws.com/test/", data=payload, headers=headers)
    resp = response.json()

    bestScore = resp["sessionAttributes"]["topScoringScoreofIntent"]
    supportedConvo = resp["sessionAttributes"]["supportedConversation"]
    bestStatusBot = resp["sessionAttributes"]["topScoringIntent"]
    #---- if in need of a new intent it will delete the old one for the user -------
    if bestStatusBot == "None" or bestScore < minimumscore and supportedConvo == False:
        requests.request("DELETE", "http://localhost:4000/user/{}".format(recipient), headers=headers)
        print("We deleted the intent from the list because we did not understand... start fresh: ", bestStatusBot)
        return "We didn't get that. Could you please try again?"

    #call to server (for now just a local api that stores in a dict)
    payload2Storage = {
        "currentBot": bestStatusBot
    }

    payload2Storage = json.dumps(payload2Storage)
    requests.request("PUT", "http://localhost:4000/user/{}".format(recipient), data=payload2Storage, headers=headers)

    return conversation(bestStatusBot, recipient, user)

#if found that the intent is still valid in the convo then calls this
def conversation(intent, recipient, message):
    headers = {"Content-Type": "application/json"}

    payload = {
        "DestinationBot": intent,
        "RecipientID": recipient,
        "text": message
    }
    #call to the lambda orchestrator to message the best bot and get a response back
    payload = json.dumps(payload)
    response = requests.request("POST","https://krrtxsq9dk.execute-api.us-east-1.amazonaws.com/test", data=payload, headers=headers)
    response = response.json()
    #logic to know whether the intent is no good and it needs to choose another bot
    if(response["dialogState"] == "ElicitIntent"):
        return choice(message, recipient)
    else:
        print("The intent now: ", intent)
        return response["message"]

#main function whether to choose to get a new bot to respond or to continue the conversation with context
def main(sender, message):
    headers = {"Content-Type": "application/json"}

    response = requests.request("GET", "http://localhost:4000/user/{}".format(sender), headers=headers)
    responseValues = response.json()

    #use case: the incoming message is from a new user
    if(response.status_code == 404):
        start = choice(message, sender)
        text = start

    #use case: the incoming message is from existing user
    else:
        bestBot = responseValues["currentBot"]
        print("The intent of the last message: ", bestBot)
        text = conversation(bestBot, sender, message)

    return text


if __name__ == "__main__":
    app.run(debug = True)