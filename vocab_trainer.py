import tkinter as tk
from tkinter import messagebox
import random
from pathlib import Path


def load_dictionary(filename):
    dictionary = []
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Не найден файл словаря: {filename}")
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if " - " in line:
                parts = line.split(" - ", 1)
                if len(parts) == 2:
                    eng, rus = parts
                    eng = eng.strip()
                    rus = rus.strip()
                    if eng and rus:
                        dictionary.append((eng, rus))
    return dictionary


def load_irregular_verbs(filename):
    verbs = []
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Не найден файл неправильных глаголов: {filename}")
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = [item.strip() for item in line.strip().split(",")]
            if len(parts) == 3 and all(parts):
                verbs.append(tuple(parts))
    return verbs


class VocabTrainer:
    def __init__(self, master, dictionary_file="dictionary.txt", verbs_file="irregular_verbs.txt"):
        self.master = master
        self.dictionary_file = dictionary_file
        self.verbs_file = verbs_file

        self.dictionary = []
        self.irregular_verbs = []

        self.mode = tk.StringVar(value="eng_to_rus")
        self.word_target_correct = 2
        self.verb_target_correct = 1

        self.training_mode = None  # "dictionary" или "irregular"
        self.progress = {}
        self.current_pair = None
        self.current_mode = None
        self.current_verb = None
        self.last_skipped = None

        master.geometry("800x600")

        self.large_font = ("Arial", 16)
        self.medium_font = ("Arial", 14)
        self.button_font = ("Arial", 12)

        self.selection_frame = tk.Frame(master)
        self.selection_frame.pack(expand=True)
        tk.Label(
            self.selection_frame,
            text="Выберите режим тренировки",
            font=self.large_font,
        ).pack(pady=20)
        tk.Button(
            self.selection_frame,
            text="Заучивание слов",
            font=self.button_font,
            width=25,
            height=2,
            command=self.start_dictionary_mode,
        ).pack(pady=10)
        tk.Button(
            self.selection_frame,
            text="Формы неправильных глаголов",
            font=self.button_font,
            width=25,
            height=2,
            command=self.start_irregular_mode,
        ).pack(pady=10)

        self.training_frame = tk.Frame(master)

        self.label = tk.Label(self.training_frame, text="", font=self.large_font)
        self.label.pack(pady=20)

        self.entry_single = tk.Entry(self.training_frame, width=50, font=self.large_font)
        self.entry_single.bind("<Return>", self.check_answer)

        self.verbs_entry_frame = tk.Frame(self.training_frame)
        self.verbs_base_label = tk.Label(self.verbs_entry_frame, text="", font=self.large_font)
        self.verbs_base_label.pack(side=tk.LEFT, padx=10)
        self.entry_second = tk.Entry(self.verbs_entry_frame, width=20, font=self.large_font)
        self.entry_second.pack(side=tk.LEFT, padx=10)
        self.entry_third = tk.Entry(self.verbs_entry_frame, width=20, font=self.large_font)
        self.entry_third.pack(side=tk.LEFT, padx=10)
        self.entry_second.bind("<Return>", self.check_answer)
        self.entry_third.bind("<Return>", self.check_answer)

        self.result_label = tk.Label(self.training_frame, text="", font=self.large_font)
        self.result_label.pack(pady=10)

        self.buttons_frame = tk.Frame(self.training_frame)
        self.buttons_frame.pack(pady=10)
        self.next_button = tk.Button(
            self.buttons_frame,
            text="Следующее слово",
            command=self.next_word,
            font=self.button_font,
            width=20,
            height=2,
        )
        self.next_button.pack(side=tk.LEFT, padx=5)
        self.check_button = tk.Button(
            self.buttons_frame,
            text="Проверить",
            command=self.check_answer,
            font=self.button_font,
            width=15,
            height=2,
        )
        self.check_button.pack(side=tk.LEFT, padx=5)
        self.skip_button = tk.Button(
            self.buttons_frame,
            text="Пропустить",
            command=self.skip_current,
            font=self.button_font,
            width=15,
            height=2,
        )
        self.skip_button.pack(side=tk.LEFT, padx=5)

        self.mode_frame = tk.Frame(self.training_frame)
        tk.Radiobutton(
            self.mode_frame,
            text="Английский → Русский",
            variable=self.mode,
            value="eng_to_rus",
            font=self.medium_font,
        ).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(
            self.mode_frame,
            text="Русский → Английский",
            variable=self.mode,
            value="rus_to_eng",
            font=self.medium_font,
        ).pack(side=tk.LEFT, padx=10)

    def start_dictionary_mode(self):
        try:
            self.dictionary = load_dictionary(self.dictionary_file)
        except FileNotFoundError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return
        if not self.dictionary:
            messagebox.showwarning("Предупреждение", "Файл словаря пуст.")
            return
        self.training_mode = "dictionary"
        self.selection_frame.pack_forget()
        self.training_frame.pack(expand=True, fill=tk.BOTH)
        self.entry_single.pack(pady=10)
        self.verbs_entry_frame.pack_forget()
        self.mode_frame.pack(pady=10)
        self.reset_dictionary_progress()
        self.next_word()

    def start_irregular_mode(self):
        try:
            self.irregular_verbs = load_irregular_verbs(self.verbs_file)
        except FileNotFoundError as exc:
            messagebox.showerror("Ошибка", str(exc))
            return
        if not self.irregular_verbs:
            messagebox.showwarning("Предупреждение", "Файл неправильных глаголов пуст.")
            return
        self.training_mode = "irregular"
        self.selection_frame.pack_forget()
        self.training_frame.pack(expand=True, fill=tk.BOTH)
        self.entry_single.pack_forget()
        self.mode_frame.pack_forget()
        self.verbs_entry_frame.pack(pady=10)
        self.reset_irregular_progress()
        self.next_word()

    def reset_dictionary_progress(self):
        self.progress = {}
        for eng, rus in self.dictionary:
            self.progress[(eng, rus, "eng_to_rus")] = 0
            self.progress[(eng, rus, "rus_to_eng")] = 0

    def reset_irregular_progress(self):
        self.progress = {}
        for verb in self.irregular_verbs:
            self.progress[verb] = 0

    def get_available_pairs(self):
        mode = self.mode.get()
        return [
            (eng, rus)
            for eng, rus in self.dictionary
            if self.progress[(eng, rus, mode)] < self.word_target_correct
        ]

    def get_available_verbs(self):
        return [verb for verb in self.irregular_verbs if self.progress[verb] < self.verb_target_correct]

    def next_word(self):
        if self.training_mode == "dictionary":
            self.entry_single.delete(0, tk.END)
            self.result_label.config(text="")
            available = self.get_available_pairs()
            if not available:
                self.handle_completion("dictionary")
                return
            filtered = available
            if (
                self.last_skipped
                and self.last_skipped["mode"] == "dictionary"
                and len(available) > 1
            ):
                filtered = [
                    pair
                    for pair in available
                    if not (pair == self.last_skipped["data"] and self.mode.get() == self.last_skipped["direction"])
                ] or available
            self.current_pair = random.choice(filtered)
            self.current_mode = self.mode.get()
            if self.current_mode == "eng_to_rus":
                self.label.config(text=f"Переведите: {self.current_pair[0]}")
            else:
                self.label.config(text=f"Переведите: {self.current_pair[1]}")
            self.entry_single.focus_set()
            self.last_skipped = None
        elif self.training_mode == "irregular":
            self.entry_second.delete(0, tk.END)
            self.entry_third.delete(0, tk.END)
            self.result_label.config(text="")
            available = self.get_available_verbs()
            if not available:
                self.handle_completion("irregular")
                return
            filtered = available
            if (
                self.last_skipped
                and self.last_skipped["mode"] == "irregular"
                and len(available) > 1
            ):
                filtered = [verb for verb in available if verb != self.last_skipped["data"]] or available
            self.current_verb = random.choice(filtered)
            self.label.config(text="Введите остальные формы глагола")
            self.verbs_base_label.config(text=self.current_verb[0])
            self.entry_second.focus_set()
            self.last_skipped = None

    def handle_completion(self, mode_name):
        if mode_name == "dictionary":
            message = (
                f"Вы правильно ответили на все слова по {self.word_target_correct} раза!\n"
                "Хотите начать заново?"
            )
        else:
            message = (
                f"Вы правильно ввели все формы по {self.verb_target_correct} раз!\n"
                "Хотите начать заново?"
            )
        if messagebox.askyesno("Поздравляем!", message):
            if mode_name == "dictionary":
                self.reset_dictionary_progress()
            else:
                self.reset_irregular_progress()
            self.next_word()
        else:
            self.master.quit()

    def check_answer(self, event=None):
        if self.training_mode == "dictionary":
            if not self.current_pair:
                return
            user_input = self.entry_single.get().strip().lower()
            eng, rus = self.current_pair
            if self.current_mode == "eng_to_rus":
                correct = rus.strip().lower()
            else:
                correct = eng.strip().lower()
            if user_input == correct:
                self.result_label.config(text="Верно!", fg="green")
                self.progress[(eng, rus, self.current_mode)] += 1
                self.master.after(800, self.next_word)
            else:
                self.result_label.config(text=f"Неверно! Правильно: {correct}", fg="red")
                self.last_skipped = {
                    "mode": "dictionary",
                    "data": self.current_pair,
                    "direction": self.current_mode,
                }
                self.master.after(1000, self.next_word)
        elif self.training_mode == "irregular":
            if not self.current_verb:
                return
            second_input = self.entry_second.get().strip().lower()
            third_input = self.entry_third.get().strip().lower()
            second_correct = self.current_verb[1].strip().lower()
            third_correct = self.current_verb[2].strip().lower()
            if second_input == second_correct and third_input == third_correct:
                self.result_label.config(text="Верно!", fg="green")
                self.progress[self.current_verb] += 1
                self.master.after(800, self.next_word)
            else:
                correct_text = f"{self.current_verb[0]} - {self.current_verb[1]} - {self.current_verb[2]}"
                self.result_label.config(text=f"Неверно! Правильно: {correct_text}", fg="red")
                self.last_skipped = {
                    "mode": "irregular",
                    "data": self.current_verb,
                }
                self.master.after(1000, self.next_word)

    def skip_current(self):
        if self.training_mode == "dictionary" and self.current_pair:
            eng, rus = self.current_pair
            correct = rus if self.current_mode == "eng_to_rus" else eng
            self.result_label.config(text=f"Пропущено. Засчитано как верно: {correct}", fg="green")
            # Увеличиваем счетчик прогресса, как при правильном ответе
            self.progress[(eng, rus, self.current_mode)] += 1
            self.master.after(800, self.next_word)
        elif self.training_mode == "irregular" and self.current_verb:
            correct_text = f"{self.current_verb[0]} - {self.current_verb[1]} - {self.current_verb[2]}"
            self.result_label.config(text=f"Пропущено. Засчитано как верно: {correct_text}", fg="green")
            # Увеличиваем счетчик прогресса, как при правильном ответе
            self.progress[self.current_verb] += 1
            self.master.after(800, self.next_word)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Словарик-тренажёр")
    app = VocabTrainer(root)
    root.mainloop()
