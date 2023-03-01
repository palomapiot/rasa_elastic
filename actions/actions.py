# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests, json

class ActionTrivia(Action):

    def name(self) -> Text:
        return "action_trivia"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        query = tracker.latest_message['text']
        answer = elasticsearch(query)

        dispatcher.utter_message(response="utter_trivia", answer=answer)

        return []

def elasticsearch(query):
    #url = '127.0.0.1:5000/trivia'
    url = "https://071b-213-164-3-50.ngrok.io/trivia"

    payload = json.dumps({"query": query})
    headers = {
    'Content-Type': 'application/json'
    }
    print('starting request')
    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.text)
    return response.text
