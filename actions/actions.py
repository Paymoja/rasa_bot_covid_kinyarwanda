from actions.kba import KBAbstractionLayer
from os import stat

import json

from requests.exceptions import HTTPError

from typing import Any, Text, Dict, List

from requests.models import Response
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, EventType, ActionExecuted, UserUtteranceReverted
from rasa_sdk.executor import CollectingDispatcher
from actions.helper import (
    get_entities,
    intent_to_message,
    lockdown_lookup,
    compare_locations,
    detect_entity,
    get_entity_details
)


class ActionKBALayer(Action):
    """Call the knowledge base abstraction layer"""

    def name(self) -> Text:
        return "action_kba_layer"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent, entities = get_entities(tracker)
        dispatcher.utter_message(
            KBAbstractionLayer(intent, entities).kba_response
        )

        return []


class ActionCheckStatistics(Action):
    """Check country covid statistics"""

    def name(self) -> Text:
        return "action_check_statistics"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent, entities = get_entities(tracker)
        dispatcher.utter_message(
            KBAbstractionLayer(intent, entities).kba_response
        )

        return []


class ActionShowTestingCenters(Action):
    """Display covid testing centers"""

    def name(self) -> Text:
        return "action_show_testing_centers"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent, entities = get_entities(tracker)
        dispatcher.utter_message(
            KBAbstractionLayer(intent, entities).kba_response
        )

        return []


class ActionCheckFinesPenalties(Action):
    """Display covid fines and penalties"""

    def name(self) -> Text:
        return "action_check_fines_penalties"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        intent, entities = get_entities(tracker)

        entity_types = [
            "offence-mask",
            "offence-distance",
            "offence-curfew",
            "offence-gathering",
            "offence-lockdown",
            "offence-bar",
        ]

        entity = detect_entity(tracker, entity_types)

        if entity:

            dispatcher.utter_message(
                KBAbstractionLayer(intent, entities).kba_response
            )
        else:
            dispatcher.utter_message(response="utter_choose_fines_penalties")

        return []


class ActionDefaultAskAffirmation(Action):
    """ Overwriting default implementation which asks the user to affirm his intent."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        location = get_entity_details(tracker, "location")
        if location:
            location = location.get("value").lower()

        """Runs action. Please see parent class for the full docstring."""
        intent_to_affirm = tracker.latest_message["intent"].get("name")

        intent_ranking = tracker.latest_message.get("intent_ranking", [])
        if intent_to_affirm == "nlu_fallback" and len(intent_ranking) > 1:
            intent_to_affirm = intent_ranking[1]["name"]

        affirmation_message = f"Did you mean {intent_to_message(intent_to_affirm)}?"
        affirmation_buttons = [
            {
                "title": "Yes",
                "payload": f'/{intent_to_affirm}{{"location":"{location}"}}',
            }
            if location
            else {"title": "Yes", "payload": f"/{intent_to_affirm}"},
            # {"title": "Yes", "payload": f"/{intent_to_affirm}"},
            {"title": "No", "payload": "/out_of_scope"},
        ]

        dispatcher.utter_message(
            text=affirmation_message, buttons=affirmation_buttons)

        return []


class ActionCheckLockdown(Action):
    """Display if a location is under lockown or not"""

    def name(self) -> Text:
        return "action_check_lockdown"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        intent, entities = get_entities(tracker)
        location = get_entity_details(tracker, "location")

        if location:
            location = location.get("value").capitalize()
            entities = json.dumps({"value": location, "entity":"location"})
            message = KBAbstractionLayer(
                "lockdown_areas", entities).kba_response
            buttons = [
                {
                    "title": "Yes",
                    "payload": "/lockdown_areas",
                },
                {"title": "No", "payload": "/affirm"},
            ]
            dispatcher.utter_message(text=message)
            dispatcher.utter_message(text='Do you want to find the lockdown of another area?', buttons=buttons)
        else:
            dispatcher.utter_message(response="utter_ask_location")

        return []


class ActionCheckCurfewTime(Action):
    def name(self) -> Text:
        return "action_check_curfew_time"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        intent, entities = get_entities(tracker)

        location = get_entity_details(tracker, "location")

        if location:
            location = location.get("value").capitalize()
            entities = json.dumps({"location": location})
            dispatcher.utter_message(
                KBAbstractionLayer('curfew_time', entities).kba_response
            )
        else:
            dispatcher.utter_message(response="utter_ask_location")

        return []
