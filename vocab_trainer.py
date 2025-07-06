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

        # Устанавливаем размер окна в 2 раза больше стандартного
        master.geometry("800x600")  # Увеличиваем с примерно 400x300 до 800x600
        
        # Создаем шрифты большего размера
        large_font = ("Arial", 16)
        medium_font = ("Arial", 14)
        button_font = ("Arial", 12)

        self.label = tk.Label(master, text="Нажмите 'Следующее слово'", font=large_font)
        self.label.pack(pady=20)

        self.entry = tk.Entry(master, width=50, font=large_font)  # Увеличиваем ширину поля ввода
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", self.check_answer)

        self.result_label = tk.Label(master, text="", font=large_font)
        self.result_label.pack(pady=10)

        self.next_button = tk.Button(master, text="Следующее слово", command=self.next_word, font=button_font, width=20, height=2)
        self.next_button.pack(pady=10)

        self.check_button = tk.Button(master, text="Проверить", command=self.check_answer, font=button_font, width=15, height=2)
        self.check_button.pack(pady=10)

        self.mode_frame = tk.Frame(master)
        self.mode_frame.pack(pady=10)
        tk.Radiobutton(self.mode_frame, text="Английский → Русский", variable=self.mode, value="eng_to_rus", font=medium_font).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(self.mode_frame, text="Русский → Английский", variable=self.mode, value="rus_to_eng", font=medium_font).pack(side=tk.LEFT, padx=10)

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
            self.label.config(text=f"Переведите: {self.current_pair[0]}", font=("Arial", 16))
        else:
            self.label.config(text=f"Переведите: {self.current_pair[1]}", font=("Arial", 16))

    def check_answer(self, event=None):
        user_input = self.entry.get().strip().lower()
        eng, rus = self.current_pair
        if self.current_mode == "eng_to_rus":
            correct = rus.strip().lower()
        else:
            correct = eng.strip().lower()
        if user_input == correct:
            self.result_label.config(text="Верно!", fg="green", font=("Arial", 16))
            self.progress[(eng, rus, self.current_mode)] += 1
            self.master.after(800, self.next_word)
        else:
            self.result_label.config(text=f"Неверно! Правильно: {correct}", fg="red", font=("Arial", 16))

if __name__ == "__main__":
    dictionary = load_dictionary("dictionary.txt")
    root = tk.Tk()
    root.title("Словарик-тренажёр")
    app = VocabTrainer(root, dictionary)
    root.mainloop()
