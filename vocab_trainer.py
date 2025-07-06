import tkinter as tk
from tkinter import messagebox
import random

def load_dictionary(filename):
    dictionary = []
    with open(filename, encoding="utf-8") as f:
        for line in f:
            if '-' in line:
                eng, rus = line.strip().split(' - ', 1)
                dictionary.append((eng.strip(), rus.strip()))
    return dictionary

class VocabTrainer:
    def __init__(self, master, dictionary):
        self.master = master
        self.dictionary = dictionary
        self.mode = tk.StringVar(value="eng_to_rus")
        self.progress = {}  # (eng, rus, mode) -> count
        self.max_repeats = 2
        self.current_pair = None
        self.current_mode = None

        self.label = tk.Label(master, text="Нажмите 'Следующее слово'")
        self.label.pack(pady=10)

        self.entry = tk.Entry(master, width=40)
        self.entry.pack(pady=5)
        self.entry.bind("<Return>", self.check_answer)

        self.result_label = tk.Label(master, text="")
        self.result_label.pack(pady=5)

        self.next_button = tk.Button(master, text="Следующее слово", command=self.next_word)
        self.next_button.pack(pady=5)

        self.check_button = tk.Button(master, text="Проверить", command=self.check_answer)
        self.check_button.pack(pady=5)

        self.mode_frame = tk.Frame(master)
        self.mode_frame.pack(pady=5)
        tk.Radiobutton(self.mode_frame, text="Английский → Русский", variable=self.mode, value="eng_to_rus").pack(side=tk.LEFT)
        tk.Radiobutton(self.mode_frame, text="Русский → Английский", variable=self.mode, value="rus_to_eng").pack(side=tk.LEFT)

        self.reset_progress()
        self.next_word()

    def reset_progress(self):
        self.progress = {}
        for eng, rus in self.dictionary:
            self.progress[(eng, rus, "eng_to_rus")] = 0
            self.progress[(eng, rus, "rus_to_eng")] = 0

    def get_available_pairs(self):
        mode = self.mode.get()
        return [
            (eng, rus)
            for eng, rus in self.dictionary
            if self.progress[(eng, rus, mode)] < self.max_repeats
        ]

    def next_word(self):
        self.entry.delete(0, tk.END)
        self.result_label.config(text="")
        available = self.get_available_pairs()
        if not available:
            if messagebox.askyesno("Поздравляем!", "Вы правильно ответили на все слова по 2 раза!\nХотите начать заново?"):
                self.reset_progress()
                available = self.get_available_pairs()
            else:
                self.master.quit()
                return
        self.current_pair = random.choice(available)
        self.current_mode = self.mode.get()
        if self.current_mode == "eng_to_rus":
            self.label.config(text=f"Переведите: {self.current_pair[0]}")
        else:
            self.label.config(text=f"Переведите: {self.current_pair[1]}")

    def check_answer(self, event=None):
        user_input = self.entry.get().strip().lower()
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

if __name__ == "__main__":
    dictionary = load_dictionary("dictionary.txt")
    root = tk.Tk()
    root.title("Словарик-тренажёр")
    app = VocabTrainer(root, dictionary)
    root.mainloop()
