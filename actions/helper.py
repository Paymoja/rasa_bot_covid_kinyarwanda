from typing import Dict, Text, Any, Optional
from rasa_sdk import Tracker

from fuzzywuzzy import fuzz
import json


def get_entity_details(
    tracker: Tracker, entity_type: Text
) -> Optional[Dict[Text, Any]]:
    all_entities = tracker.latest_message.get("entities", [])
    entities = [e for e in all_entities if e.get("entity") == entity_type]
    if entities:
        return entities[0]


def get_entities(tracker: Tracker):
    all_entities = tracker.latest_message.get("entities", [])
    return tracker.get_intent_of_latest_message(), json.dumps(all_entities)


def detect_entity(tracker: Tracker, entity_types: Text) -> Optional[Dict[Text, Any]]:
    all_entities = tracker.latest_message.get("entities", [])
    print(all_entities)
    for e in all_entities:
        for e_type in entity_types:
            if e.get("entity") == e_type:
                return e_type


def intent_to_message(intent):
    filename = "actions/intent_description_mapping.json"
    with open(filename) as data:
        intent_mapping = json.load(data)

        for item, message in intent_mapping.items():
            if item == intent:
                return message

    return "intent not found"


def lockdown_lookup(location):
    filename = "actions/lockdown.json"
    with open(filename) as data:
        lockdown_status = json.load(data)

        for item, status in lockdown_status.items():
            if item == location:
                return status


def get_location_similarity(n1, n2):
    return fuzz.token_sort_ratio(n1, n2)


def compare_locations(location):
    filename = "actions/lockdown.json"

    max_similarity = float("-inf")
    with open(filename) as data:
        districts_lockdown_status = json.load(data)

        for district, _ in districts_lockdown_status.items():
            similarity = get_location_similarity(district, location)
            if similarity > max_similarity:
                max_similarity = similarity
                most_similar_location = district
                return most_similar_location
            else:
                return None
