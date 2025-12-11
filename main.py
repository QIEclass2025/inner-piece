import tkinter as tk
from tkinter import messagebox
import time
import random

# ==========================================
# [1] 데이터 및 로직 (기존과 동일)
# ==========================================

class MentalRecord:
    def __init__(self, adversity, belief, consequence, disputation, effect):
        self.adversity = adversity
        self.belief = belief
        self.consequence = consequence
        self.disputation = disputation
        self.effect = effect
        self.date = time.strftime('%Y-%m-%d %H:%M:%S')

QUESTION_BANK = [
    "그 생각이 100% 사실이라는 확실한 법적 증거가 있습니까?",
    "그렇게 생각하는 것이 지금 이 문제를 해결하는 데 실제로 도움이 됩니까?",
    "가장 친한 친구가 나와 똑같은 상황에 처했다면, 친구에게도 그렇게 말해줄 건가요?",
    "이 상황을 긍정적으로, 혹은 배울 점으로 해석할 수 있는 여지는 전혀 없나요?",
    "1년 뒤에도 이 일이 지금처럼 내 인생을 뒤흔들 만큼 심각할까요?"
]

# ==========================================
# [2] GUI 애플리케이션 클래스
# ==========================================

class InnerPeaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inner-Peace: 디지털 인지 치료")
        self.root.geometry("500x600") # 창 크기 설정
        
        # 현재 화면을 담을 프레임 (컨테이너)
        self.current_frame = None
        
        # 앱 시작 시 메인 메뉴 보여주기
        self.show_main_menu()

    # --- 화면 전환 유틸리티 ---
    def switch_frame(self, frame_class):
        """기존 화면을 지우고 새로운 화면을 띄우는 함수"""
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = frame_class(self.root, self)
        self.current_frame.pack(fill="both", expand=True)

    def show_main_menu(self):
        self.switch_frame(MainMenuFrame)

    def show_sos_mode(self):
        self.switch_frame(SOSModeFrame)

    def show_abcde_training(self):
        self.switch_frame(ABCDEFrame)

# ==========================================
# [3] 각 화면(Frame) 정의
# ==========================================

# 1. 메인 메뉴 화면
class MainMenuFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        
        # 제목
        tk.Label(self, text="Inner-Peace", font=("Helvetica", 24, "bold"), pady=40).pack()
        tk.Label(self, text="마음 챙김 도구", font=("Helvetica", 12)).pack()
        
        # 버튼들
        tk.Button(self, text="1. 급성 스트레스 완화 (SOS)", font=("Helvetica", 14), width=30, height=2,
                  command=self.app.show_sos_mode).pack(pady=10)
        
        tk.Button(self, text="2. 사고 전환 훈련 (ABCDE)", font=("Helvetica", 14), width=30, height=2,
                  command=self.app.show_abcde_training).pack(pady=10)
        
        tk.Button(self, text="3. 종료", font=("Helvetica", 14), width=30, height=2,
                  command=master.quit).pack(pady=10)

# 2. SOS 모드 화면
class SOSModeFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        self.step = 0 # 호흡 단계
        
        tk.Label(self, text="SOS: 4-7-8 호흡", font=("Helvetica", 18, "bold"), pady=20).pack()
        
        self.status_label = tk.Label(self, text="시작 버튼을 누르세요", font=("Helvetica", 20), fg="blue")
        self.status_label.pack(pady=50)
        
        self.btn_start = tk.Button(self, text="호흡 시작", command=self.start_breathing)
        self.btn_start.pack()
        
        tk.Button(self, text="메인으로 돌아가기", command=self.app.show_main_menu).pack(side="bottom", pady=20)

    def start_breathing(self):
        self.btn_start.config(state="disabled") # 중복 클릭 방지
        self.run_cycle(3) # 3세트 반복

    def run_cycle(self, remaining_cycles):
        if remaining_cycles <= 0:
            self.status_label.config(text="편안해지셨나요?", fg="green")
            self.btn_start.config(state="normal")
            return

        # GUI에서는 time.sleep을 쓰면 멈춥니다. after()를 써야 합니다.
        # 1. 들이마시기 (4초)
        self.status_label.config(text="들이마시세요 (4초)", fg="red")
        self.after(4000, lambda: self.hold_breath(remaining_cycles))

    def hold_breath(self, remaining_cycles):
        # 2. 참기 (7초)
        self.status_label.config(text="숨을 참으세요 (7초)", fg="orange")
        self.after(7000, lambda: self.exhale_breath(remaining_cycles))

    def exhale_breath(self, remaining_cycles):
        # 3. 내뱉기 (8초)
        self.status_label.config(text="내뱉으세요 (8초)", fg="blue")
        self.after(8000, lambda: self.run_cycle(remaining_cycles - 1))

# 3. ABCDE 훈련 화면
class ABCDEFrame(tk.Frame):
    def __init__(self, master, app):
        super().__init__(master)
        self.app = app
        
        tk.Label(self, text="ABCDE 사고 전환", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        # 입력 필드들을 담을 컨테이너
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)
        
        # A: 사건
        tk.Label(form_frame, text="[A] 어떤 사건이 있었나요?").grid(row=0, column=0, sticky="w")
        self.entry_a = tk.Entry(form_frame, width=40)
        self.entry_a.grid(row=1, column=0, pady=(0, 10))
        
        # B: 신념
        tk.Label(form_frame, text="[B] 그때 든 생각은?").grid(row=2, column=0, sticky="w")
        self.entry_b = tk.Entry(form_frame, width=40)
        self.entry_b.grid(row=3, column=0, pady=(0, 10))

        # D: 논박 (버튼을 누르면 질문이 나옴)
        self.btn_ask = tk.Button(self, text="AI 논박 질문 받기", command=self.generate_question, bg="lightgray")
        self.btn_ask.pack(pady=5)
        
        self.lbl_question = tk.Label(self, text="", fg="blue", wraplength=400)
        self.lbl_question.pack(pady=5)
        
        # D 답변
        tk.Label(self, text="[D] 반박해 보세요:").pack()
        self.entry_d = tk.Entry(self, width=40)
        self.entry_d.pack()
        
        # 저장 버튼
        tk.Button(self, text="기록 저장하기", command=self.save_record, bg="lightblue").pack(pady=20)
        
        tk.Button(self, text="메인으로 돌아가기", command=self.app.show_main_menu).pack(side="bottom", pady=10)

    def generate_question(self):
        q = random.choice(QUESTION_BANK)
        self.lbl_question.config(text=f"AI: {q}")

    def save_record(self):
        # 간단한 저장 확인 메시지
        if not self.entry_a.get() or not self.entry_d.get():
            messagebox.showwarning("경고", "내용을 입력해주세요.")
            return
        
        messagebox.showinfo("성공", "마음 속에 기록되었습니다.\n(파일 저장은 다음 단계 구현)")
        self.app.show_main_menu()

# ==========================================
# [4] 메인 실행
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    app = InnerPeaceApp(root)
    root.mainloop()