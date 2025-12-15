import sys
import json
import time
import os
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTabWidget, 
                             QTextEdit, QLineEdit, QSpinBox, QMessageBox, 
                             QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
                             QStackedWidget, QGroupBox, QFormLayout, QScrollArea)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QColor, QPalette

# ==========================================
# [1] 데이터 설계 및 상수 정의 (Original Logic)
# ==========================================

HISTORY_FILE = "inner_peace_history.json"

QUESTION_BANK = [
    "그렇게 생각하는 것이 지금 이 문제를 해결하는 데 실제로 도움이 됩니까?",
    "가장 친한 친구가 나와 똑같은 상황에 처했다면, 친구에게도 그렇게 말해줄 건가요?",
    "이 상황을 긍정적으로, 혹은 배울 점으로 해석할 수 있는 여지는 전혀 없나요?",
    "1년 뒤에도 이 일이 지금처럼 내 인생을 뒤흔들 만큼 심각할까요?"
]

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

def save_record(record):
    try:
        records = load_records()
        records.append(record.to_dict())
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)
        return True
    except (IOError, TypeError) as e:
        print(f"오류: 파일을 쓰는 데 실패했습니다. ({e})")
        return False

def load_records():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        print(f"오류: 파일을 읽는 데 실패했습니다. ({e})")
        return []

# ==========================================
# [2] GUI Implementation
# ==========================================

class InnerPeaceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inner-Peace: 마음 챙김 도구")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fa; }
            QTabWidget::pane { border: 1px solid #e1e4e8; background: white; border-radius: 8px; }
            QTabBar::tab { background: #e1e4e8; padding: 10px 20px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; }
            QTabBar::tab:selected { background: white; font-weight: bold; border-bottom: 2px solid #3498db; }
            QLabel { color: #2c3e50; }
            QPushButton { background-color: #3498db; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:disabled { background-color: #bdc3c7; }
            QLineEdit, QTextEdit, QSpinBox { border: 1px solid #bdc3c7; border-radius: 4px; padding: 5px; background: white; }
            QGroupBox { font-weight: bold; border: 1px solid #bdc3c7; border-radius: 6px; margin-top: 10px; padding-top: 15px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.sos_tab = SOSTab()
        self.abcde_tab = ABCDETab()
        self.history_tab = HistoryTab()

        self.tabs.addTab(self.sos_tab, "🆘 SOS 모드")
        self.tabs.addTab(self.abcde_tab, "🧠 사고 전환 (ABCDE)")
        self.tabs.addTab(self.history_tab, "📜 기록 조회")

        self.tabs.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, index):
        if index == 2: # History tab
            self.history_tab.refresh_history()

class SOSTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 1. Course Selection
        self.selection_group = QGroupBox("코스 선택")
        sel_layout = QHBoxLayout()
        
        self.btn_1min = QPushButton("1분 (3회)")
        self.btn_2min = QPushButton("2분 (6회)")
        self.btn_3min = QPushButton("3분 (9회)")
        
        self.btn_1min.clicked.connect(lambda: self.start_session(1))
        self.btn_2min.clicked.connect(lambda: self.start_session(2))
        self.btn_3min.clicked.connect(lambda: self.start_session(3))
        
        sel_layout.addWidget(self.btn_1min)
        sel_layout.addWidget(self.btn_2min)
        sel_layout.addWidget(self.btn_3min)
        self.selection_group.setLayout(sel_layout)
        self.layout.addWidget(self.selection_group)

        # 2. Breathing Display (Initially Hidden or Idle)
        self.breathing_display = QGroupBox("4-7-8 호흡")
        disp_layout = QVBoxLayout()
        
        self.status_label = QLabel("준비")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #7f8c8d;")
        
        self.timer_label = QLabel("0초")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setFont(QFont("Arial", 18))
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #2ecc71; }")
        
        self.cancel_btn = QPushButton("중단하기")
        self.cancel_btn.setStyleSheet("background-color: #e74c3c;")
        self.cancel_btn.clicked.connect(self.stop_session)
        self.cancel_btn.hide()

        disp_layout.addWidget(self.status_label)
        disp_layout.addWidget(self.timer_label)
        disp_layout.addWidget(self.progress_bar)
        disp_layout.addWidget(self.cancel_btn)
        self.breathing_display.setLayout(disp_layout)
        self.layout.addWidget(self.breathing_display)

        # 3. Grounding (Initially Hidden)
        self.grounding_group = QGroupBox("그라운딩 (5-4-3-2-1)")
        ground_layout = QFormLayout()
        
        self.sight_input = QLineEdit()
        self.touch_input = QLineEdit()
        self.sound_input = QLineEdit()
        self.smell_input = QLineEdit()
        self.taste_input = QLineEdit()
        self.memo_input = QLineEdit()
        
        ground_layout.addRow("👁️ 본 것 (5가지):", self.sight_input)
        ground_layout.addRow("✋ 느낀 것 (4가지):", self.touch_input)
        ground_layout.addRow("👂 들은 것 (3가지):", self.sound_input)
        ground_layout.addRow("👃 맡은 것 (2가지):", self.smell_input)
        ground_layout.addRow("👅 맛본 것 (1가지):", self.taste_input)
        ground_layout.addRow("📝 메모:", self.memo_input)
        
        self.save_btn = QPushButton("저장하기")
        self.save_btn.clicked.connect(self.save_grounding)
        
        self.grounding_group.setLayout(ground_layout)
        self.layout.addWidget(self.grounding_group)
        self.layout.addWidget(self.save_btn)
        
        self.grounding_group.hide()
        self.save_btn.hide()

        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_breathing)
        self.current_cycle = 0
        self.total_cycles = 0
        self.phase = 0 # 0: Ready, 1: Inhale, 2: Hold, 3: Exhale
        self.time_left = 0
        self.selected_course_min = 0

    def start_session(self, minutes):
        self.selected_course_min = minutes
        self.total_cycles = minutes * 3
        self.current_cycle = 0
        self.phase = 0 # Will start with Inhale
        
        self.selection_group.setEnabled(False)
        self.grounding_group.hide()
        self.save_btn.hide()
        self.cancel_btn.show()
        
        # Start breathing sequence
        self.start_inhale()

    def stop_session(self):
        self.timer.stop()
        self.status_label.setText("중단됨")
        self.status_label.setStyleSheet("color: #7f8c8d;")
        self.timer_label.setText("0초")
        self.progress_bar.setValue(0)
        self.selection_group.setEnabled(True)
        self.cancel_btn.hide()

    def start_inhale(self):
        if self.current_cycle >= self.total_cycles:
            self.end_session()
            return
            
        self.current_cycle += 1
        self.phase = 1
        self.time_left = 40 # 4.0 seconds (using 100ms timer for smoothness)
        self.status_label.setText(f"들이마시세요 (Cycle {self.current_cycle}/{self.total_cycles})")
        self.status_label.setStyleSheet("color: #2ecc71;") # Green
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #2ecc71; }")
        self.progress_bar.setRange(0, 40)
        self.progress_bar.setValue(0)
        self.timer.start(100) # 0.1s update

    def start_hold(self):
        self.phase = 2
        self.time_left = 70
        self.status_label.setText("참으세요")
        self.status_label.setStyleSheet("color: #f1c40f;") # Yellow/Warning
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #f1c40f; }")
        self.progress_bar.setRange(0, 70)
        self.progress_bar.setValue(0)

    def start_exhale(self):
        self.phase = 3
        self.time_left = 80
        self.status_label.setText("내뱉으세요")
        self.status_label.setStyleSheet("color: #3498db;") # Blue
        self.progress_bar.setStyleSheet("QProgressBar::chunk { background-color: #3498db; }")
        self.progress_bar.setRange(0, 80)
        self.progress_bar.setValue(0)

    def update_breathing(self):
        self.time_left -= 1
        self.timer_label.setText(f"{self.time_left / 10:.1f}초")
        
        # Update progress bar (fill up or drain down? let's fill up)
        max_val = self.progress_bar.maximum()
        self.progress_bar.setValue(max_val - self.time_left)

        if self.time_left <= 0:
            if self.phase == 1: # After Inhale
                self.start_hold()
            elif self.phase == 2: # After Hold
                self.start_exhale()
            elif self.phase == 3: # After Exhale
                self.start_inhale() # Next cycle

    def end_session(self):
        self.timer.stop()
        self.status_label.setText("호흡 완료! 주변을 둘러보세요.")
        self.status_label.setStyleSheet("color: #2c3e50;")
        self.cancel_btn.hide()
        
        # Clear inputs
        self.sight_input.clear()
        self.touch_input.clear()
        self.sound_input.clear()
        self.smell_input.clear()
        self.taste_input.clear()
        self.memo_input.clear()
        
        self.grounding_group.show()
        self.save_btn.show()

    def save_grounding(self):
        grounding_data = {
            "sight": self.sight_input.text(),
            "touch": self.touch_input.text(),
            "sound": self.sound_input.text(),
            "smell": self.smell_input.text(),
            "taste": self.taste_input.text(),
        }
        record = SOSRecord(f"약 {self.selected_course_min}분", self.memo_input.text(), grounding_data)
        if save_record(record):
            QMessageBox.information(self, "저장 완료", "오늘의 경험이 안전하게 기록되었습니다.")
            self.selection_group.setEnabled(True)
            self.grounding_group.hide()
            self.save_btn.hide()
            self.status_label.setText("준비")
        else:
            QMessageBox.critical(self, "오류", "저장에 실패했습니다.")


class ABCDETab(QWidget):
    def __init__(self):
        super().__init__()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.layout = QVBoxLayout(content_widget)
        scroll.setWidget(content_widget)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        # A. Adversity
        self.layout.addWidget(QLabel("A. 사건 (Adversity): 어떤 사건 때문에 스트레스를 받으셨나요?"))
        self.input_a = QTextEdit()
        self.input_a.setMaximumHeight(80)
        self.layout.addWidget(self.input_a)

        # B. Belief
        self.layout.addWidget(QLabel("B. 신념 (Belief): 그 사건에 대해 순간적으로 든 생각은 무엇인가요?"))
        self.input_b = QTextEdit()
        self.input_b.setMaximumHeight(80)
        self.layout.addWidget(self.input_b)

        # C. Consequence
        self.layout.addWidget(QLabel("C. 결과 (Consequence): 그로 인한 감정의 고통 점수 (1-10)"))
        self.input_c = QSpinBox()
        self.input_c.setRange(1, 10)
        self.layout.addWidget(self.input_c)

        # AI Question Button
        self.ai_q_label = QLabel("🤖 생각 전환을 위한 질문이 여기에 나타납니다.")
        self.ai_q_label.setStyleSheet("color: #8e44ad; font-style: italic; margin: 10px 0;")
        self.ai_q_label.setWordWrap(True)
        self.layout.addWidget(self.ai_q_label)
        
        self.btn_get_q = QPushButton("질문 받기")
        self.btn_get_q.clicked.connect(self.show_question)
        self.layout.addWidget(self.btn_get_q)

        # D. Disputation
        self.layout.addWidget(QLabel("D. 반박 (Disputation): 위 질문에 대해 스스로 반박하거나 답변해 보세요."))
        self.input_d = QTextEdit()
        self.input_d.setMaximumHeight(80)
        self.layout.addWidget(self.input_d)

        # E. Effect
        self.layout.addWidget(QLabel("E. 효과 (Effect): 새롭게 정리된 합리적인 생각은 무엇인가요?"))
        self.input_e = QTextEdit()
        self.input_e.setMaximumHeight(80)
        self.layout.addWidget(self.input_e)
        
        # Memo
        self.layout.addWidget(QLabel("메모 (선택):"))
        self.input_memo = QLineEdit()
        self.layout.addWidget(self.input_memo)

        # Save Button
        self.btn_save = QPushButton("기록 저장하기")
        self.btn_save.setStyleSheet("background-color: #27ae60; height: 40px; font-size: 14px;")
        self.btn_save.clicked.connect(self.save_abcde)
        self.layout.addWidget(self.btn_save)

        self.layout.addStretch()

    def show_question(self):
        q = random.choice(QUESTION_BANK)
        self.ai_q_label.setText(f"🤖 Inner-Peace 질문: \"{q}\"")

    def save_abcde(self):
        if not self.input_a.toPlainText().strip() or not self.input_b.toPlainText().strip():
            QMessageBox.warning(self, "입력 부족", "사건(A)과 신념(B)은 반드시 입력해야 합니다.")
            return

        record = MentalRecord(
            self.input_a.toPlainText(),
            self.input_b.toPlainText(),
            self.input_c.value(),
            self.input_d.toPlainText(),
            self.input_e.toPlainText(),
            self.input_memo.text()
        )

        if save_record(record):
            QMessageBox.information(self, "성공", "사고 전환 훈련이 기록되었습니다.")
            # Reset
            self.input_a.clear()
            self.input_b.clear()
            self.input_c.setValue(1)
            self.input_d.clear()
            self.input_e.clear()
            self.input_memo.clear()
            self.ai_q_label.setText("🤖 생각 전환을 위한 질문이 여기에 나타납니다.")
        else:
            QMessageBox.critical(self, "오류", "저장에 실패했습니다.")

class HistoryTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["날짜", "유형", "내용 요약", "메모"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        
        self.btn_refresh = QPushButton("목록 새로고침")
        self.btn_refresh.clicked.connect(self.refresh_history)
        
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.btn_refresh)

    def refresh_history(self):
        records = load_records()
        self.table.setRowCount(len(records))
        
        for row, r in enumerate(reversed(records)): # Show newest first
            date_item = QTableWidgetItem(r.get('date', ''))
            type_item = QTableWidgetItem(r.get('type', ''))
            
            summary_text = ""
            if r.get('type') == 'ABCDE':
                summary_text = f"사건: {r.get('adversity', '')} -> 효과: {r.get('effect', '')}"
            elif r.get('type') == 'SOS':
                summary_text = f"코스: {r.get('course', '')}"
                
            summary_item = QTableWidgetItem(summary_text)
            memo_item = QTableWidgetItem(r.get('memo', ''))
            
            self.table.setItem(row, 0, date_item)
            self.table.setItem(row, 1, type_item)
            self.table.setItem(row, 2, summary_item)
            self.table.setItem(row, 3, memo_item)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set global font
    font = QFont("Malgun Gothic", 10) # Using Malgun Gothic for Korean support on Windows/General
    if sys.platform == "darwin":
        font = QFont("AppleGothic", 10)
    app.setFont(font)
    
    window = InnerPeaceApp()
    window.show()
    sys.exit(app.exec())
