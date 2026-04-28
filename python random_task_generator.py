import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Файл для сохранения истории
        self.history_file = "task_history.json"
        
        # Предопределённые задачи с категориями
        self.default_tasks = [
            {"text": "Прочитать статью по Python", "category": "учёба"},
            {"text": "Сделать зарядку 15 минут", "category": "спорт"},
            {"text": "Закончить отчёт", "category": "работа"},
            {"text": "Выучить 10 новых слов", "category": "учёба"},
            {"text": "Пробежка 3 км", "category": "спорт"},
            {"text": "Созвониться с клиентом", "category": "работа"},
            {"text": "Посмотреть вебинар", "category": "учёба"},
            {"text": "Отжимания 30 раз", "category": "спорт"},
            {"text": "Написать план на неделю", "category": "работа"}
        ]
        
        # Загружаем сохранённые задачи или используем стандартные
        self.tasks = []
        self.history = []
        self.load_data()
        
        # Текущая сгенерированная задача
        self.current_task = None
        
        self.setup_ui()
        self.update_task_list()
        self.update_history_display()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🎲 Random Task Generator", 
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # === Фрейм для генерации задачи ===
        generate_frame = ttk.LabelFrame(main_frame, text="Генерация задачи", padding="10")
        generate_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        self.generate_btn = ttk.Button(generate_frame, text="🎲 Сгенерировать задачу", 
                                      command=self.generate_task)
        self.generate_btn.grid(row=0, column=0, pady=5)
        
        self.current_task_label = ttk.Label(generate_frame, text="Нажмите кнопку, чтобы получить задачу", 
                                           font=("Arial", 11), wraplength=500)
        self.current_task_label.grid(row=1, column=0, pady=10)
        
        # === Фрейм для добавления новой задачи ===
        add_frame = ttk.LabelFrame(main_frame, text="Добавить новую задачу", padding="10")
        add_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(add_frame, text="Текст задачи:").grid(row=0, column=0, sticky=tk.W)
        self.task_entry = ttk.Entry(add_frame, width=40)
        self.task_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(add_frame, text="Категория:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_var = tk.StringVar(value="учёба")
        category_combo = ttk.Combobox(add_frame, textvariable=self.category_var, 
                                      values=["учёба", "спорт", "работа"], state="readonly")
        category_combo.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        add_btn = ttk.Button(add_frame, text="➕ Добавить задачу", command=self.add_task)
        add_btn.grid(row=2, column=0, columnspan=2, pady=5)
        
        # === Фрейм со списком доступных задач ===
        tasks_frame = ttk.LabelFrame(main_frame, text="📋 Список доступных задач", padding="10")
        tasks_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Создаём Treeview для списка задач
        columns = ("Текст задачи", "Категория")
        self.task_tree = ttk.Treeview(tasks_frame, columns=columns, show="headings", height=6)
        self.task_tree.heading("Текст задачи", text="Текст задачи")
        self.task_tree.heading("Категория", text="Категория")
        self.task_tree.column("Текст задачи", width=300)
        self.task_tree.column("Категория", width=100)
        self.task_tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(tasks_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        # === Фрейм истории ===
        history_frame = ttk.LabelFrame(main_frame, text="📜 История сгенерированных задач", padding="10")
        history_frame.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Фильтр по категориям
        filter_frame = ttk.Frame(history_frame)
        filter_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Label(filter_frame, text="Фильтр:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="все")
        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                   values=["все", "учёба", "спорт", "работа"], 
                                   state="readonly", width=10)
        filter_combo.pack(side=tk.LEFT, padx=5)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.update_history_display())
        
        self.clear_history_btn = ttk.Button(filter_frame, text="🗑 Очистить историю", 
                                           command=self.clear_history)
        self.clear_history_btn.pack(side=tk.LEFT, padx=10)
        
        # Список истории
        self.history_listbox = tk.Listbox(history_frame, height=10)
        self.history_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        history_scroll = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        history_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.history_listbox.configure(yscrollcommand=history_scroll.set)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        tasks_frame.columnconfigure(0, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(1, weight=1)
        
    def load_data(self):
        """Загрузка задач и истории из файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tasks = data.get("tasks", self.default_tasks.copy())
                    self.history = data.get("history", [])
            except (json.JSONDecodeError, IOError):
                self.tasks = self.default_tasks.copy()
                self.history = []
        else:
            self.tasks = self.default_tasks.copy()
            self.history = []
    
    def save_data(self):
        """Сохранение задач и истории в файл"""
        data = {
            "tasks": self.tasks,
            "history": self.history
        }
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def update_task_list(self):
        """Обновление отображения списка задач"""
        # Очищаем текущий список
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Добавляем задачи
        for task in self.tasks:
            self.task_tree.insert("", tk.END, values=(task["text"], task["category"]))
    
    def update_history_display(self):
        """Обновление отображения истории с учётом фильтра"""
        self.history_listbox.delete(0, tk.END)
        
        filter_value = self.filter_var.get()
        
        for entry in self.history:
            # Проверяем фильтр
            if filter_value != "все" and entry["category"] != filter_value:
                continue
            
            # Форматируем строку для отображения
            time_str = entry.get("timestamp", "")
            display_text = f"[{time_str}] {entry['category'].upper()}: {entry['text']}"
            self.history_listbox.insert(tk.END, display_text)
    
    def generate_task(self):
        """Генерация случайной задачи"""
        if not self.tasks:
            messagebox.showwarning("Нет задач", "Список задач пуст. Добавьте хотя бы одну задачу!")
            return
        
        # Выбираем случайную задачу
        self.current_task = random.choice(self.tasks)
        
        # Отображаем задачу
        self.current_task_label.config(
            text=f"✨ Ваша задача: {self.current_task['text']} (Категория: {self.current_task['category']}) ✨",
            foreground="green"
        )
        
        # Добавляем в историю с временной меткой
        history_entry = {
            "text": self.current_task["text"],
            "category": self.current_task["category"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(history_entry)
        
        # Сохраняем и обновляем отображение
        self.save_data()
        self.update_history_display()
    
    def add_task(self):
        """Добавление новой задачи"""
        task_text = self.task_entry.get().strip()
        category = self.category_var.get()
        
        # Проверка на пустую строку
        if not task_text:
            messagebox.showwarning("Ошибка", "Текст задачи не может быть пустым!")
            return
        
        # Добавляем задачу
        new_task = {"text": task_text, "category": category}
        self.tasks.append(new_task)
        
        # Очищаем поле ввода
        self.task_entry.delete(0, tk.END)
        
        # Сохраняем и обновляем отображение
        self.save_data()
        self.update_task_list()
        messagebox.showinfo("Успех", f"Задача '{task_text}' добавлена!")
    
    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.save_data()
            self.update_history_display()
            messagebox.showinfo("Очистка", "История успешно очищена!")

def main():
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()