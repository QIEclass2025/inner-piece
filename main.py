import sys
import time
import random
import os
import json

# ==========================================
# [1] 데이터 설계 및 상수 정의
# ==========================================

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

    def __str__(self):
        memo_str = f" | 메모: {self.memo}" if self.memo else ""
        return f"[{self.date}] [ABCDE] 사건: {self.adversity} | 감정점수: {self.consequence} | 새로운 생각: {self.effect}{memo_str}"

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

    def __str__(self):
        memo_str = f" | 메모: {self.memo}" if self.memo else ""
        grounding_str = ""
        if self.grounding:
            g = self.grounding
            grounding_str = (
                f" | 그라운딩: "
                f"본 것({g.get('sight', '')}), "
                f"느낀 것({g.get('touch', '')}), "
                f"들은 것({g.get('sound', '')}), "
                f"맡은 것({g.get('smell', '')}), "
                f"맛본 것({g.get('taste', '')})"
            )
        return f"[{self.date}] [SOS] {self.course}{memo_str}{grounding_str}"

    def to_dict(self):
        return {
            "type": "SOS",
            "date": self.date,
            "course": self.course,
            "memo": self.memo,
            "grounding": self.grounding,
        }

QUESTION_BANK = [
    "그렇게 생각하는 것이 지금 이 문제를 해결하는 데 실제로 도움이 됩니까?",
    "가장 친한 친구가 나와 똑같은 상황에 처했다면, 친구에게도 그렇게 말해줄 건가요?",
    "이 상황을 긍정적으로, 혹은 배울 점으로 해석할 수 있는 여지는 전혀 없나요?",
    "1년 뒤에도 이 일이 지금처럼 내 인생을 뒤흔들 만큼 심각할까요?"
]

class Color:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ==========================================
# [2] 핵심 기능 함수 구현
# ==========================================

def save_record(record):
    try:
        records = load_records()
        records.append(record.to_dict())
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        return True
    except (IOError, TypeError) as e:
        print(f"{Color.FAIL}오류: 파일을 쓰는 데 실패했습니다. ({e}){Color.ENDC}")
        return False

def load_records():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"{Color.FAIL}오류: 파일을 읽는 데 실패했습니다. ({e}){Color.ENDC}")
        return []

def get_numeric_input(prompt, min_val, max_val, cancel_value=None):
    while True:
        try:
            val_input = input(prompt)
            if cancel_value is not None and val_input.lower() == str(cancel_value).lower():
                return cancel_value
            
            val = int(val_input)
            if min_val <= val <= max_val:
                return val
            print(f"{Color.WARNING}{min_val}에서 {max_val} 사이의 숫자로만 입력해주세요.{Color.ENDC}")
        except ValueError:
            print(f"{Color.FAIL}숫자를 입력해주세요.{Color.ENDC}")

def get_yes_no_input(prompt):
    while True:
        choice = input(prompt).lower()
        if choice in ['y', 'yes', 'ㅛ']:
            return True
        elif choice in ['n', 'no', 'ㅜ']:
            return False
        print(f"{Color.WARNING}'y' 또는 'n'으로만 입력해주세요.{Color.ENDC}")

def sos_mode():
    print("\n" + "="*40)
    print(f"   {Color.CYAN+Color.BOLD}[SOS 모드] 4-7-8 호흡 테라피{Color.ENDC}")
    print("="*40)
    
    print(f"{Color.BLUE}이 호흡은 심장 박동을 느리게 하고, 우리 몸의 '긴장 모드'를 '휴식 모드'로 바꾸는 데 도움을 줍니다.{Color.ENDC}")
    
    print("\n" + f"{Color.BOLD}코스 선택:{Color.ENDC}")
    print("1. 약 1분 (3회 반복)")
    print("2. 약 2분 (6회 반복)")
    print("3. 약 3분 (9회 반복)")
    print(f"9. {Color.WARNING}취소하고 메인 메뉴로 돌아가기{Color.ENDC}")
    
    course_choice = get_numeric_input(f"{Color.BOLD}원하는 코스를 선택하세요 (1-3 또는 9) >>{Color.ENDC} ", 1, 3, cancel_value=9)
    
    if course_choice == 9:
        print(f"{Color.WARNING}SOS 모드를 취소하고 메인 메뉴로 돌아갑니다.{Color.ENDC}")
        input("계속하려면 Enter를 누르세요.")
        return

    cycles = course_choice * 3
    course_name = f"약 {course_choice}분"

    print("\n" + "-"*40)
    print(f"{Color.BOLD}자세 안내:{Color.ENDC}")
    print("  - 허리를 세우고, 어깨 힘을 살짝 풀어 주세요.")
    print("  - 턱을 살짝 당겨서 목이 편안한 위치로 오게 해 주세요.")
    print("-" * 40)
    input("준비되셨으면 Enter를 누르세요...")

    coaching_messages = [
        "지금은 그냥 리듬에 익숙해지는 단계입니다.",
        "이번에는 내쉴 때 어깨와 턱의 힘이 빠지는 느낌에 집중해 보세요.",
        "이번에는 마음속으로 '괜찮아' 하고 되뇌어 보세요."
    ]

    for i in range(1, cycles + 1):
        print(f"\n{Color.BOLD}[Cycle {i}/{cycles}]{Color.ENDC}")
        message_index = (i - 1) % len(coaching_messages)
        print(f"{Color.WARNING}코칭: {coaching_messages[message_index]}{Color.ENDC}")
        
        for t in range(4, 0, -1):
            sys.stdout.write(f"\r{Color.GREEN}들이마시세요 ({t}초)...{Color.ENDC}   ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 30 + "\r") # Clear line
        print(f"{Color.GREEN}들이마시세요 (4초)...{Color.ENDC} Breathe~")

        # Hold
        for t in range(7, 0, -1):
            sys.stdout.write(f"\r{Color.WARNING}참으세요 ({t}초).......{Color.ENDC}   ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 30 + "\r") # Clear line
        print(f"{Color.WARNING}참으세요 (7초).......{Color.ENDC} 멈춤")

        # Exhale
        for t in range(8, 0, -1):
            sys.stdout.write(f"\r{Color.BLUE}내뱉으세요 ({t}초).....{Color.ENDC}   ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r" + " " * 30 + "\r") # Clear line
        print(f"{Color.BLUE}내뱉으세요 (8초).....{Color.ENDC} 후~")

    print(f"\n{Color.GREEN}[안내] 호흡이 끝났습니다. 마음이 조금 편안해지셨나요?{Color.ENDC}")

    # Add grounding
    print("\n" + "="*40)
    print(f"   {Color.CYAN+Color.BOLD}[그라운딩] 5-4-3-2-1 현실감 회복{Color.ENDC}")
    print("="*40)
    print("지금 이 순간, 주변을 천천히 둘러보며 아래를 적어 보세요.")
    
    grounding_sight = input("1) 지금 눈에 보이는 것 5가지:\n> ")
    grounding_touch = input("2) 지금 몸으로 느껴지는 촉감(의자, 옷, 피부 등) 4가지:\n> ")
    grounding_sound = input("3) 지금 들리는 소리 3가지:\n> ")
    grounding_smell = input("4) 지금 맡을 수 있는 냄새 2가지:\n> ")
    grounding_taste = input("5) 지금 떠오르는 맛 1가지:\n> ")

    grounding_data = {
        "sight": grounding_sight,
        "touch": grounding_touch,
        "sound": grounding_sound,
        "smell": grounding_smell,
        "taste": grounding_taste,
    }
    
    memo = input(f"\n{Color.BLUE+Color.BOLD}(선택) 현재 경험에 대해 한 줄 메모를 남겨보세요:{Color.ENDC}\n>> ")

    if get_yes_no_input(f"\n{Color.BOLD}이 세션을 기록하시겠습니까? (y/n){Color.ENDC} "):
        record = SOSRecord(course_name, memo, grounding_data)
        if save_record(record):
            print(f"\n{Color.GREEN}[저장 완료] 오늘의 경험이 안전하게 기록되었습니다.{Color.ENDC}")

    input("\n메뉴로 돌아가려면 Enter를 누르세요.")


def abcde_training():
    print("\n" + "="*40)
    print(f"   {Color.CYAN+Color.BOLD}[사고 전환 훈련] ABCDE 모델링{Color.ENDC}")
    print("="*40)
    print(f"정보: 각 단계에서 이전 단계로 가려면 '{Color.WARNING}p{Color.ENDC}', 메인 메뉴로 가려면 '{Color.WARNING}m{Color.ENDC}'을 입력하세요.")

    state = 'A'
    data = {'adversity': '', 'belief': '', 'consequence': '', 'disputation': '', 'effect': '', 'memo': ''}
    ai_question = random.choice(QUESTION_BANK)

    while state != 'EXIT':
        if state == 'A':
            res = input(f"\n{Color.BLUE+Color.BOLD}[A] 어떤 사건 때문에 스트레스를 받으셨나요?{Color.ENDC}\n>> ").lower()
            if res == 'm': print(f"\n{Color.WARNING}훈련을 중단하고 메인 메뉴로 돌아갑니다.{Color.ENDC}"); input("계속하려면 Enter를 누르세요."); return
            if res == 'p': print(f"{Color.WARNING}첫 단계에서는 뒤로 갈 수 없습니다.{Color.ENDC}"); continue
            data['adversity'] = res; state = 'B'
        
        elif state == 'B':
            res = input(f"\n{Color.BLUE+Color.BOLD}[B] 그 사건에 대해 순간적으로 든 생각은 무엇인가요?{Color.ENDC}\n>> ").lower()
            if res == 'm': print(f"\n{Color.WARNING}훈련을 중단하고 메인 메뉴로 돌아갑니다.{Color.ENDC}"); input("계속하려면 Enter를 누르세요."); return
            if res == 'p': state = 'A'; continue
            data['belief'] = res; state = 'C'

        elif state == 'C':
            res = input(f"\n{Color.BLUE+Color.BOLD}[C] 그로 인한 감정의 고통을 1~10 사이 숫자로 입력해주세요.{Color.ENDC}\n>> ").lower()
            if res == 'm': print(f"\n{Color.WARNING}훈련을 중단하고 메인 메뉴로 돌아갑니다.{Color.ENDC}"); input("계속하려면 Enter를 누르세요."); return
            if res == 'p': state = 'B'; continue
            try:
                val = int(res)
                if not (1 <= val <= 10):
                    print(f"{Color.WARNING}1에서 10 사이의 숫자로만 입력해주세요.{Color.ENDC}"); continue
                data['consequence'] = val
                print("\n" + "-"*40); print(f"💫 {Color.HEADER+Color.BOLD}Inner-Peace 시스템이 당신의 생각에 대해 묻습니다:{Color.ENDC}"); print(f"{Color.CYAN}\"{ai_question}\"{Color.ENDC}"); print("-"*40)
                state = 'D'
            except ValueError:
                print(f"{Color.FAIL}숫자를 입력해주세요.{Color.ENDC}"); continue

        elif state == 'D':
            res = input(f"\n{Color.BLUE+Color.BOLD}[D] 위 질문에 대해 스스로 반박하거나 답변해 보세요.{Color.ENDC}\n>> ").lower()
            if res == 'm': print(f"\n{Color.WARNING}훈련을 중단하고 메인 메뉴로 돌아갑니다.{Color.ENDC}"); input("계속하려면 Enter를 누르세요."); return
            if res == 'p': state = 'C'; continue
            data['disputation'] = res; state = 'E'
        
        elif state == 'E':
            res = input(f"\n{Color.BLUE+Color.BOLD}[E] 논박을 통해 새롭게 정리된 합리적인 생각은 무엇인가요?{Color.ENDC}\n>> ").lower()
            if res == 'm': print(f"\n{Color.WARNING}훈련을 중단하고 메인 메뉴로 돌아갑니다.{Color.ENDC}"); input("계속하려면 Enter를 누르세요."); return
            if res == 'p': state = 'D'; continue
            data['effect'] = res; state = 'MEMO'
            
        elif state == 'MEMO':
            res = input(f"\n{Color.BLUE+Color.BOLD}(선택) 현재 훈련에 대해 한 줄 메모를 남겨보세요:{Color.ENDC}\n>> ").lower()
            if res == 'm': print(f"\n{Color.WARNING}훈련을 중단하고 메인 메뉴로 돌아갑니다.{Color.ENDC}"); input("계속하려면 Enter를 누르세요."); return
            if res == 'p': state = 'E'; continue
            data['memo'] = res; state = 'SAVE'
            
        elif state == 'SAVE':
            res = input(f"\n{Color.BOLD}이 훈련을 기록하시겠습니까? (y/n){Color.ENDC} ").lower()
            if res == 'm': print(f"\n{Color.WARNING}훈련을 중단하고 메인 메뉴로 돌아갑니다.{Color.ENDC}"); input("계속하려면 Enter를 누르세요."); return
            if res == 'p': state = 'MEMO'; continue
            if res in ['y', 'yes', 'ㅛ']:
                record = MentalRecord(data['adversity'], data['belief'], data['consequence'], data['disputation'], data['effect'], data['memo'])
                if save_record(record): print(f"\n{Color.GREEN}[저장 완료] 오늘의 훈련이 성공적으로 기록되었습니다.{Color.ENDC}")
                state = 'EXIT'
            elif res in ['n', 'no', 'ㅜ']:
                state = 'EXIT'
            else:
                print(f"{Color.WARNING}'y' 또는 'n'으로만 입력해주세요.{Color.ENDC}"); continue
                
    input("\n메뉴로 돌아가려면 Enter를 누르세요.")

def view_history():
    print("\n" + "="*40)
    print(f"   {Color.CYAN+Color.BOLD}[사고 기록 조회] 나의 마음 일지{Color.ENDC}")
    print("="*40)

    records = load_records()
    if not records:
        print("\n아직 저장된 기록이 없습니다.")
        print("사고 전환 훈련이나 SOS 모드를 통해 첫 기록을 남겨보세요.")
    else:
        print("\n[최신순으로 모든 기록을 표시합니다]\n")
        for record in reversed(records):
            date_str = record.get('date', '날짜 없음')
            memo_str = f" | 메모: {record.get('memo')}" if record.get('memo') else ""
            
            if record.get('type') == 'ABCDE':
                print(
                    f"[{date_str}] [ABCDE] "
                    f"사건: {record.get('adversity', '')} | "
                    f"감정점수: {record.get('consequence', '')} | "
                    f"새로운 생각: {record.get('effect', '')}{memo_str}"
                )
            elif record.get('type') == 'SOS':
                g = record.get('grounding', {})
                grounding_str = ""
                if g:
                    grounding_str = (
                        f" | 그라운딩: "
                        f"본 것({g.get('sight', '')}), "
                        f"느낀 것({g.get('touch', '')}), "
                        f"들은 것({g.get('sound', '')}), "
                        f"맡은 것({g.get('smell', '')}), "
                        f"맛본 것({g.get('taste', '')})"
                    )
                print(
                    f"[{date_str}] [SOS] "
                    f"{record.get('course', '')}{memo_str}{grounding_str}"
                )
            else:
                print(f"[{date_str}] 알 수 없는 기록 타입: {record}")

            print("-" * 20)

    print("\n" + "="*40)
    input("메뉴로 돌아가려면 Enter를 누르세요.")

def print_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("\n" + Color.HEADER + "■"*40 + Color.ENDC)
    print(f"      {Color.BOLD}Inner-Peace : 마음 챙김 도구{Color.ENDC}")
    print(Color.HEADER + "■"*40 + Color.ENDC)
    print(f"{Color.GREEN}1. 급성 스트레스 완화 (SOS 모드){Color.ENDC}")
    print(f"{Color.GREEN}2. 사고 전환 훈련 (ABCDE 모델링){Color.ENDC}")
    print(f"{Color.GREEN}3. 사고 기록 조회 (History){Color.ENDC}")
    print(f"{Color.GREEN}4. 프로그램 종료{Color.ENDC}")
    print("-" * 40)

def main():
    if os.name == 'nt':
        os.system('color')

    while True:
        print_menu()
        choice = input(f"{Color.BOLD}원하는 기능을 선택하세요 >>{Color.ENDC} ")

        if choice == '1':
            sos_mode()
        elif choice == '2':
            abcde_training()
        elif choice == '3':
            view_history()
        elif choice == '4':
            print(f"\n{Color.CYAN}프로그램을 종료합니다. 오늘도 평안하세요.{Color.ENDC}")
            sys.exit()
        else:
            print(f"\n{Color.FAIL}[!] 잘못된 입력입니다.{Color.ENDC}")
            time.sleep(1)

if __name__ == "__main__":
    main()