import json
import time
import os
import uuid

HISTORY_FILE = "inner_peace_history.json"

class MentalRecord:
    def __init__(self, adversity, belief, consequence, disputation, effect, memo=""):
        self.id = str(uuid.uuid4())
        self.adversity = adversity
        self.belief = belief
        self.consequence = consequence
        self.disputation = disputation
        self.effect = effect
        self.memo = memo
        self.date = time.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "id": self.id,
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
        self.id = str(uuid.uuid4())
        self.course = course
        self.memo = memo
        self.grounding = grounding if grounding is not None else {}
        self.date = time.strftime('%Y-%m-%d %H:%M:%S')

    def to_dict(self):
        return {
            "id": self.id,
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
            records = json.load(f)
            
        # Migration: Add ID to legacy records if missing
        migrated = False
        for record in records:
            if 'id' not in record:
                record['id'] = str(uuid.uuid4())
                migrated = True
        
        if migrated:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=4)
                
        return records
    except (IOError, json.JSONDecodeError) as e:
        print(f"Error reading file: {e}")
        return []

def delete_record(record_id):
    """
    Deletes a record by ID.
    """
    try:
        records = load_records()
        new_records = [r for r in records if r.get('id') != record_id]
        
        if len(records) == len(new_records):
            return False # ID not found
            
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(new_records, f, ensure_ascii=False, indent=4)
        return True
    except (IOError, TypeError) as e:
        print(f"Error deleting record: {e}")
        return False

QUESTION_BANK = [
    "그렇게 생각하는 것이 지금 이 문제를 해결하는 데 실제로 도움이 됩니까?",
    "가장 친한 친구가 나와 똑같은 상황에 처했다면, 친구에게도 그렇게 말해줄 건가요?",
    "이 상황을 긍정적으로, 혹은 배울 점으로 해석할 수 있는 여지는 전혀 없나요?",
    "1년 뒤에도 이 일이 지금처럼 내 인생을 뒤흔들 만큼 심각할까요?",
    "이 일이 내 인생 전체를 놓고 봤을 때 얼마나 중요한 부분인가요?",
    "지금 하는 걱정이 실제로 일어날 확률은 얼마나 되나요?",
    "스피노사우르스는 당신이 이러길 원하나요? 🦖",
    "이 신념이 사실임을 증명하는 객관적인 증거가 있나요?",
    "이 신념이 참이 아니라는 증거는 무엇인가요?",
    "과거에 비슷한 상황에서 이 신념이 틀렸던 적은 없었나요?",
    "다른 사람이 이 상황을 본다면, 똑같이 생각할까요?",
    "내 신념은 느낌인가요, 아니면 확인된 사실인가요?",
    "이 신념을 뒷받침하는 구체적인 데이터나 관찰 가능한 사건은 무엇인가요?",
    "내 신념이 지나치게 일반화되거나 과장된 부분은 없나요?",
    "내 신념이 100% 항상 진실이어야 하나요, 아니면 예외적인 경우는 없나요?",
    "이 신념을 계속 믿으면 나에게 어떤 긍정적인 결과가 있나요?",
    "이 신념이 내 목표 달성에 도움이 되나요, 방해가 되나요?",
    "이 신념을 믿을 때 나는 어떤 감정을 느끼나요? 그 감정이 나에게 도움이 되나요?",
    "이 신념 때문에 내가 피하게 되는 행동은 무엇인가요?",
    "이 신념을 유지하는 것이 장기적으로 나의 정신 건강이나 행복에 도움이 될까요?",
    "이 신념을 버린다면 내 삶은 어떻게 달라질까요?",
    "내가 반드시 (Must) ~~해야 한다는 법칙이나 규칙이 정말로 존재하나요?",
    "내가 원하는 (Prefer) 것과 반드시 필요한 (Must) 것을 혼동하고 있지는 않나요?",
    "내가 생각하는 **결과 (C)**가 정말로 내 신념 (B) 때문에 발생한 것인가요? 아니면 다른 요인이 있나요?",
    "내 신념이 논리적으로 타당하다면, 모든 상황에서 동일한 결론이 나와야 하지 않나요?",
    "내가 가장 두려워하는 일이 일어난다 해도, 그것이 정말로 감당할 수 없는 재앙일까요?",
    "만약 일이 잘못된다면, 나는 어떤 식으로 대처할 수 있을까요?",
    "이 상황을 다르게 해석할 수 있는 최소한 3가지 다른 방법은 무엇인가요?",
    "이 상황에 대해 더 합리적이고 건강한 신념을 갖는다면, 그것은 무엇일까요?",
    "완벽하지 않은 나 자신과 세상을 조건 없이 수용하는 것은 어떤 의미인가요?",
    "내가 상황을 통제할 수 없다면, 무엇에 집중해야 할까요?",
    "이 신념을 조금 더 덜 절대적이고, 유연하게 바꾼다면 어떤 문장이 될까요?",
    "단기적인 고통을 겪는 것이 장기적인 목표를 위해 더 나은 결과를 가져올 수도 있나요?",
    "이 신념이 무상(無常)의 관점에서 보면 영속적이라고 주장할 만한 객관적 근거가 있나요?",
    "이 신념이 ‘아(我)의 고정성’을 강화해 집착을 낳는 것은 아닌가요(집착이 고통을 키우지 않나요)?",
    "이 신념이 중용(中庸)의 정신에서 지나치게 한쪽으로 치우친 극단적 판단은 아닌가요?",
    "이 신념이 타인에 대한 인(仁)과 공감에 비추어볼 때 올바른 행동으로 이어지나요, 아니면 해를 주나요?",
    "이 신념을 고수함으로써 내 본분(예·의무)이나 자기 수양(修身)에 방해가 되지는 않나요"
]
