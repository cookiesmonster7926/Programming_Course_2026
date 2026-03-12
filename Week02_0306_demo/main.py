import tkinter as tk
import tkinter.font as tkfont
import random
import time
import string

# Colors
BG_COLOR = "#2C3E50"
FG_COLOR = "#ECF0F1"
ACCENT_COLOR = "#E74C3C"
SUCCESS_COLOR = "#2ECC71"
BUTTON_COLOR = "#3498DB"

# Word Banks
WORD_BANKS = {
    "Normal": [  # 單字
        # fruits & food
        "apple", "banana", "cherry", "date", "elderberry", "fig", "grape", "honey",
        "kiwi", "lemon", "mango", "melon", "olive", "peach", "pear", "orange",
        "quince", "raisin", "berry", "fruit", "tomato", "potato", "onion", "carrot",
        "garlic", "pepper", "cheese", "butter", "bread", "cookie", "candy", "chocolate",
        # home & objects
        "house", "mouse", "table", "chair", "sofa", "window", "door", "floor",
        "ceiling", "kitchen", "bathroom", "bedroom", "pillow", "blanket", "closet", "mirror",
        "spoon", "fork", "knife", "plate", "glass", "cup", "bottle", "water",
        "phone", "laptop", "screen", "mousepad", "keyboard", "notebook", "pencil", "eraser",
        # feelings & adjectives
        "happy", "smile", "laugh", "dream", "sleep", "night", "light", "green",
        "blue", "white", "black", "yellow", "purple", "orange", "bright", "dark",
        "fast", "slow", "strong", "weak", "clean", "dirty", "quiet", "noisy",
        # verbs
        "run", "walk", "jump", "swim", "write", "read", "sing", "dance",
        "study", "learn", "think", "focus", "rest", "relax", "start", "finish"
    ],
    "Hard": [   # 兩個單字片語
        # CS / IT
        "binary search", "bubble sort", "linked list", "hash table", "stack overflow",
        "queue system", "database server", "cloud storage", "network socket", "virtual machine",
        "source code", "object oriented", "event loop", "error handler", "memory leak",
        "garbage collection", "version control", "merge conflict", "unit test", "debug mode",
        "command line", "terminal window", "cursor position", "input buffer", "output stream",
        "data structure", "algorithm design", "runtime error", "compile time", "infinite loop",
        "recursion depth", "binary tree", "dynamic array", "function call", "parameter list",
        "return value", "main thread", "worker thread", "user input",
        # 一般英文片語
        "high score", "game over", "final round", "time limit", "speed run",
        "focus mode", "brain training", "typing practice", "keyboard layout", "short cut",
        "daily challenge", "simple task", "hard mode", "random word", "secret level",
        "blue screen", "dark theme", "light mode", "save file", "load game",
        "sound effect", "background music", "window size", "screen resolution", "user interface",
        "mouse click", "double click", "drag drop", "hot key", "caps lock",
        "space bar", "enter key", "shift key", "control key", "escape key"
    ],
    "Nightmare": [  # 短句
        "Type this sentence as fast as you can.",
        "Small mistakes will cost you precious time.",
        "Stay calm, breathe, and keep on typing.",
        "Every round is another chance to improve.",
        "Accuracy is more important than raw speed.",
        "Do not panic when the timer goes down.",
        "Focus on each letter, one by one.",
        "Your fingers will learn the pattern slowly.",
        "A steady rhythm beats random bursts.",
        "Keep your eyes on the center of the screen.",
        "Typos are normal, corrections are progress.",
        "Practice daily and the keyboard becomes invisible.",
        "Short sentences train both speed and control.",
        "You can always try again next round.",
        "Treat each mistake as a friendly teacher.",
        "Good posture helps you type more comfortably.",
        "Relax your shoulders and wrists while typing.",
        "Look at the screen, not at the keyboard.",
        "Let your muscle memory guide your hands.",
        "Stay patient, improvement takes a little time.",
        "Do not rush the first few letters.",
        "Reading ahead can make you much faster.",
        "Your score today is not your limit.",
        "Speed grows naturally with consistent practice.",
        "Focus on clean and smooth keystrokes.",
        "A clear mind types with fewer errors.",
        "Trust your practice and keep going.",
        "You are training both mind and fingers.",
        "Small improvements add up over many games.",
        "Missing one round does not define you.",
        "Keep your typing steady, not chaotic.",
        "Every correct word is a tiny victory.",
        "Stay curious and enjoy the challenge.",
        "Measure progress, not perfection each time.",
        "Warm up your hands before a long session.",
        "Challenge yourself with harder sentences gradually.",
        "Learn from patterns in your common mistakes.",
        "Pause briefly if your mind feels overloaded.",
        "Consistency beats intensity in the long run.",
        "You can always redesign your own practice.",
        "Typing skills help with many other tasks.",
        "Games like this make training more fun.",
        "Even slow progress is still forward progress.",
        "Good habits today create strong skills tomorrow.",
        "Do your best, then take a short break.",
        "Keep the rhythm even when you feel nervous.",
        "Short breaks can refresh your concentration.",
        "Count your wins, not just your failures.",
        "Smile a little and keep typing on.",
        "Let the timer motivate, not scare you.",
        "Treat each mistake as helpful feedback.",
        "Accuracy first, then speed will follow.",
        "Stay focused, the round ends quickly.",
        "You are better than your last score.",
        "Focus on the current word, not the result.",
        "This sentence is here to train your patience.",
        "Trust that your hands remember the layout.",
        "A calm mind types with stable rhythm.",
        "Your future self will thank you for practicing.",
        "You can always restart and try a new pace.",
        "This challenge is training your concentration.",
        "Type smoothly, not violently on the keys.",
        "Your goal is progress, not perfection today.",
        "Take a deep breath before each new round.",
        "Notice how your typing slowly becomes automatic.",
        "You are building a long term skill here.",
        "Celebrate small milestones after every few games.",
        "Let this round be your cleanest yet.",
        "Your mistakes guide you to your weaknesses.",
        "A stable tempo often beats frantic typing.",
        "Use each sentence to learn something new.",
        "Your hands and eyes are learning to cooperate.",
        "Every session makes you slightly more confident.",
        "Stay curious, relaxed, and keep moving forward."
    ]
}


class RandomKeyboardGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Speed Typing Challenge")
        self.root.geometry("600x500")
        self.root.configure(bg=BG_COLOR)

        # Game State
        self.total_rounds = 0
        self.current_round = 0
        self.score = 0
        self.answer = ""
        self.start_time = 0
        self.timer_running = False
        self.remaining_time = 0
        self.total_chars_typed = 0
        self.game_start_time = 0
        
        # Difficulty Settings
        self.difficulty_var = tk.StringVar(value="Normal")
        self.current_time_limit = 10
        self.current_word_length = 5

        # ==== Setup UI ====
        self.setup_ui()

    def setup_ui(self):
        # Title
        tk.Label(self.root, text="Speed Typing Challenge", font=("Helvetica", 24, "bold"), 
                 bg=BG_COLOR, fg=FG_COLOR).pack(pady=20)

        # Settings Frame
        self.settings_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.settings_frame.pack(pady=10)

        # Rounds Input
        tk.Label(self.settings_frame, text="Rounds:", font=("Helvetica", 14), 
                 bg=BG_COLOR, fg=FG_COLOR).pack(side=tk.LEFT, padx=5)
        
        self.round_entry = tk.Entry(self.settings_frame, width=5, font=("Helvetica", 14), justify="center")
        self.round_entry.insert(0, "5")
        self.round_entry.pack(side=tk.LEFT, padx=5)
        self.round_entry.bind("<Return>", lambda event: self.start_game())

        # Difficulty Selection
        self.diff_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.diff_frame.pack(pady=5)
        
        self.diff_buttons = {}
        modes = ["Normal", "Hard", "Nightmare"]
        for mode in modes:
            btn = tk.Button(self.diff_frame, text=mode, command=lambda m=mode: self.set_difficulty(m),
                            font=("Helvetica", 12), width=10)
            btn.pack(side=tk.LEFT, padx=5)
            self.diff_buttons[mode] = btn
            
        # Set default difficulty
        self.set_difficulty("Normal")

        # Start Button (Removed custom bg/fg to fix Mac visibility issue)
        self.start_button = tk.Button(self.root, text="Start Game", command=self.start_game,
                                      font=("Helvetica", 14, "bold"), padx=20, pady=5)
        self.start_button.pack(pady=15)

        # Game Area (Initially Hidden or Empty)
        self.game_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.game_frame.pack(pady=10, fill="both", expand=True)

        # Word Display (Canvas for CAPTCHA style)
        self.word_canvas = tk.Canvas(self.game_frame, width=600, height=100, bg=BG_COLOR, highlightthickness=0)
        self.word_canvas.pack(pady=10)

        # Timer Bar
        self.timer_label = tk.Label(self.game_frame, text=f"Time: --", font=("Helvetica", 12),
                                    bg=BG_COLOR, fg=FG_COLOR)
        self.timer_label.pack()

        # Input
        self.input_entry = tk.Entry(self.game_frame, width=25, font=("Helvetica", 18), justify="center")
        self.input_entry.pack(pady=15)
        self.input_entry.bind("<Return>", self.check_answer)
        self.input_entry.bind("<KeyRelease>", self.check_input_progress)
        self.input_entry.config(state="disabled")

        # Status / Feedback
        self.feedback_label = tk.Label(self.game_frame, text="", font=("Helvetica", 14), bg=BG_COLOR, fg=FG_COLOR)
        self.feedback_label.pack(pady=5)

        self.stats_label = tk.Label(self.game_frame, text="Score: 0 | WPM: 0", font=("Helvetica", 12), 
                                    bg=BG_COLOR, fg=FG_COLOR)
        self.stats_label.pack(pady=10, side=tk.BOTTOM)

    def set_difficulty(self, mode):
        self.difficulty_var.set(mode)
        
        # Update button styles
        for m, btn in self.diff_buttons.items():
            if m == mode:
                # Active: Gold text, Bold font. Avoid setting bg on Mac to prevent issues.
                btn.config(fg="#D4AC0D", font=("Helvetica", 12, "bold"), relief="sunken")
            else:
                # Inactive: Default text, Normal font
                btn.config(fg="black", font=("Helvetica", 12), relief="raised")

    def get_difficulty_settings(self):
        mode = self.difficulty_var.get()
        if mode == "Normal":
            return 10, 5  # 10s, length 5
        elif mode == "Hard":
            return 10, 8  # 10s, length 8
        elif mode == "Nightmare":
            return 15, 8  # 10s, length 8, complex chars
        return 10, 5

    def start_game(self):
        try:
            rounds = int(self.round_entry.get())
            if rounds <= 0: raise ValueError
        except ValueError:
            self.feedback_label.config(text="Please enter a valid number of rounds!", fg=ACCENT_COLOR)
            return

        self.total_rounds = rounds
        self.current_round = 0
        self.score = 0
        self.total_chars_typed = 0
        self.game_start_time = time.time()
        
        # Apply Difficulty Settings
        self.current_time_limit, self.current_word_length = self.get_difficulty_settings()
        
        self.start_button.config(state="disabled")
        self.round_entry.config(state="disabled")
        for widget in self.diff_frame.winfo_children():
            widget.config(state="disabled")
            
        self.input_entry.config(state="normal")
        self.input_entry.focus()
        
        self.next_round()

    def next_round(self):
        self.current_round += 1
        
        if self.current_round > self.total_rounds:
            self.end_game()
            return

        self.answer = self.generate_random_word(self.current_word_length)
        self.draw_text_display(self.answer)
        
        self.input_entry.delete(0, tk.END)
        self.feedback_label.config(text="")
        
        # Reset Timer
        self.remaining_time = self.current_time_limit
        self.timer_running = True
        self.update_timer()
        
        self.update_status()

    def check_input_progress(self, event=None):
        if not self.timer_running: return
        user_input = self.input_entry.get()
        self.draw_text_display(self.answer, user_input)

    def draw_text_display(self, text, user_input=""):
        self.word_canvas.delete("all")
        
        # Dynamic font size based on length
        base_font_size = 32
        if len(text) > 15:
            base_font_size = 24
        if len(text) > 25:
            base_font_size = 16
        if len(text) > 40:
            base_font_size = 12
            
        # Create font object to measure size
        game_font = tkfont.Font(family="Courier New", size=base_font_size, weight="bold")
        
        # Calculate total width using the font metric
        # For monospaced font, we can measure one char and multiply, or measure the whole string
        # To ensure character-by-character coloring aligns perfectly, we should use fixed char width
        char_width = game_font.measure("A") 
        total_width = char_width * len(text)
        
        # Center the text block
        canvas_width = 600
        start_x = (canvas_width - total_width) / 2
        
        # Prevent left-side clipping
        if start_x < 10: start_x = 10
        
        for i, char in enumerate(text):
            # Calculate x position for this character
            # We use the left edge (start_x) + offset, then add half width for center anchor
            x = start_x + (i * char_width) + (char_width / 2)
            y = 50 # Vertical center
            
            # Determine color
            color = FG_COLOR
            if i < len(user_input):
                if user_input[i] == char:
                    color = SUCCESS_COLOR
                else:
                    color = ACCENT_COLOR
            
            self.word_canvas.create_text(x, y, text=char, font=game_font, 
                                         fill=color, tags="text", anchor="center")

    def update_timer(self):
        if not self.timer_running:
            return
            
        if self.remaining_time > 0:
            self.timer_label.config(text=f"Time: {self.remaining_time:.1f}s", fg=FG_COLOR)
            self.remaining_time -= 0.1
            self.root.after(100, self.update_timer)
        else:
            self.timer_label.config(text="Time's Up!", fg=ACCENT_COLOR)
            self.handle_timeout()

    def handle_timeout(self):
        self.timer_running = False
        self.feedback_label.config(text=f"Time's up! It was '{self.answer}'", fg=ACCENT_COLOR)
        self.draw_text_display(self.answer) # Reset color
        self.root.after(1500, self.next_round)

    def generate_random_word(self, length):
        # length param is now ignored as we use word banks
        mode = self.difficulty_var.get()
        bank = WORD_BANKS.get(mode, WORD_BANKS["Normal"])
        return random.choice(bank)

    def check_answer(self, event=None):
        if not self.timer_running: return

        user_input = self.input_entry.get().strip()
        
        if not user_input: return

        self.timer_running = False # Stop timer logic
        
        if user_input == self.answer:
            self.score += 1
            self.total_chars_typed += len(self.answer)
            self.draw_text_display(self.answer, self.answer) # All green
            self.feedback_label.config(text="Correct!", fg=SUCCESS_COLOR)
            delay = 500 # Fast transition for correct
        else:
            self.draw_text_display(self.answer) # Reset color
            self.feedback_label.config(text=f"Wrong! It was '{self.answer}'", fg=ACCENT_COLOR)
            delay = 1500 # Slower transition for error to see feedback

        self.update_status()
        self.root.after(delay, self.next_round)

    def calculate_wpm(self):
        elapsed_min = (time.time() - self.game_start_time) / 60
        if elapsed_min == 0: return 0
        wpm = (self.total_chars_typed / 5) / elapsed_min
        return int(wpm)

    def update_status(self):
        wpm = self.calculate_wpm()
        self.stats_label.config(
            text=f"Round: {self.current_round}/{self.total_rounds} | Score: {self.score} | WPM: {wpm}"
        )

    def end_game(self):
        self.timer_running = False
        self.word_canvas.delete("all")
        self.word_canvas.create_text(300, 50, text="Game Over", font=("Courier New", 32, "bold"), fill=FG_COLOR, anchor="center")
        
        self.input_entry.config(state="disabled")
        self.start_button.config(state="normal")
        self.round_entry.config(state="normal")
        for widget in self.diff_frame.winfo_children():
            widget.config(state="normal")
        
        wpm = self.calculate_wpm()
        accuracy = (self.score / self.total_rounds * 100) if self.total_rounds else 0
        
        self.feedback_label.config(
            text=f"Final Score: {self.score}/{self.total_rounds} ({accuracy:.0f}%)\nWPM: {wpm}", 
            fg=SUCCESS_COLOR
        )

if __name__ == "__main__":
    root = tk.Tk()
    game = RandomKeyboardGame(root)
    root.mainloop()
