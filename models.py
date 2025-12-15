import json
import time
import os

HISTORY_FILE = "inner_peace_history.json"

class MentalRecord:
    def __init__(self, adversity, belief, consequence, disputation, effect, memo=""):
        self.adversity = adversity
        self.belief = belief
        self.consequence = consequence
        self.disputation = disputation
        self.effect = effect
        self.memo = memo
        self.date = time.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "type": "ABCDE",
            "date": self.date,
            "adversity": self.adversity,
            "belief": self.belief,
            "consequence": self.consequence,
            "disputation": self.disputation,
            "effect": self.effect,
            "memo": self.memo,
        }

class SOSRecord:
    def __init__(self, course, memo="", grounding=None):
        self.course = course
        self.memo = memo
        self.grounding = grounding if grounding is not None else {}
        self.date = time.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "type": "SOS",
            "date": self.date,
            "course": self.course,
            "memo": self.memo,
            "grounding": self.grounding,
        }

def save_record(record_dict):
    """
    Saves a record dictionary to the history file.
    Note: Pass the dictionary, not the object, to keep it simple for Flask.
    """
    try:
        records = load_records()
        records.append(record_dict)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        return True
    except (IOError, TypeError) as e:
        print(f"Error saving file: {e}")
        return False

def load_records():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading file: {e}")
        return []

QUESTION_BANK = [
    "그렇게 생각하는 것이 지금 이 문제를 해결하는 데 실제로 도움이 됩니까?",
    "가장 친한 친구가 나와 똑같은 상황에 처했다면, 친구에게도 그렇게 말해줄 건가요?",
    "이 상황을 긍정적으로, 혹은 배울 점으로 해석할 수 있는 여지는 전혀 없나요?",
    "1년 뒤에도 이 일이 지금처럼 내 인생을 뒤흔들 만큼 심각할까요?",
    "이 일이 내 인생 전체를 놓고 봤을 때 얼마나 중요한 부분인가요?",
    "지금 하는 걱정이 실제로 일어날 확률은 얼마나 되나요?",
    "스피노사우르스는 당신이 이러길 원하나요? 🦖"
]
