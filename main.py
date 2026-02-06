import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import hashlib
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import json
import tempfile
import shutil


class FileEncryptorApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("File Encryptor Pro v2.0 - Режим замены")
        self.window.geometry("700x700")
        self.window.configure(bg='#f0f0f0')

        # Настройка стилей
        self.setup_styles()

        # Переменные
        self.input_file = ""
        self.output_file = ""
        self.is_processing = False
        self.replace_mode = tk.BooleanVar(value=False)  # Режим замены файла

        # Создание интерфейса
        self.create_widgets()

    def setup_styles(self):
        """Настройка стилей элементов"""
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Title.TLabel', font=('Arial', 16, 'bold'),
                        background='#f0f0f0', foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'),
                        background='#f0f0f0', foreground='#34495e')
        style.configure('Action.TButton', font=('Arial', 11, 'bold'),
                        padding=10, background='#4CAF50', foreground='white')
        style.configure('Progress.Horizontal.TProgressbar', thickness=20)
        style.configure('Custom.TButton', font=('Arial', 10),
                        padding=5)

        style.map('Action.TButton',
                  background=[('active', '#45a049'), ('pressed', '#3d8b40')])

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Заголовок
        title_frame = ttk.Frame(self.window)
        title_frame.pack(fill='x', padx=20, pady=(20, 10))

        ttk.Label(title_frame, text="🔐 File Encryptor",
                  style='Title.TLabel').pack()
        ttk.Label(title_frame, text="Шифрование/дешифрование на месте",
                  font=('Arial', 10), foreground='#7f8c8d').pack()

        # Основной контейнер
        main_container = ttk.Frame(self.window)
        main_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Левая панель (настройки)
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        # Правая панель (лог)
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))

        # Создание виджетов
        self.create_file_section(left_panel)
        self.create_settings_section(left_panel)
        self.create_password_section(left_panel)
        self.create_action_button_section(left_panel)
        self.create_progress_section(left_panel)
        self.create_log_section(right_panel)
        self.create_bottom_buttons(right_panel)

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(self.window, textvariable=self.status_var,
                               relief='sunken', anchor='w', padding=(10, 5),
                               background='#e8f5e8', foreground='#2e7d32',
                               font=('Arial', 9))
        status_bar.pack(side='bottom', fill='x')

    def create_file_section(self, parent):
        """Создание секции выбора файлов"""
        frame = ttk.LabelFrame(parent, text="📁 Файл", padding=15)
        frame.pack(fill='x', pady=(0, 15))

        # Входной файл (он же выходной)
        ttk.Label(frame, text="Файл для обработки:", style='Header.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 5))

        input_frame = ttk.Frame(frame)
        input_frame.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 15))
        input_frame.columnconfigure(0, weight=1)

        self.input_entry = ttk.Entry(input_frame, font=('Arial', 10))
        self.input_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))

        ttk.Button(input_frame, text="Выбрать...",
                   command=self.select_input_file, width=12).grid(row=0, column=1)

        # Чекбокс режима замены
        self.replace_checkbox = ttk.Checkbutton(frame,
                                                text="Заменить исходный файл",
                                                variable=self.replace_mode,
                                                command=self.on_replace_mode_change)
        self.replace_checkbox.grid(row=2, column=0, sticky='w', pady=(10, 0))

    def create_settings_section(self, parent):
        """Создание секции настроек"""
        frame = ttk.LabelFrame(parent, text="⚙️ Настройки", padding=15)
        frame.pack(fill='x', pady=(0, 15))

        # Режим работы
        ttk.Label(frame, text="Режим:", style='Header.TLabel').grid(
            row=0, column=0, sticky='w', padx=(0, 20))

        self.mode_var = tk.StringVar(value="encrypt")
        ttk.Radiobutton(frame, text="Зашифровать", variable=self.mode_var,
                        value="encrypt", command=self.on_mode_change).grid(
            row=0, column=1, sticky='w')
        ttk.Radiobutton(frame, text="Расшифровать", variable=self.mode_var,
                        value="decrypt", command=self.on_mode_change).grid(
            row=0, column=2, sticky='w')

        # Метод дополнения
        ttk.Label(frame, text="Дополнение:", style='Header.TLabel').grid(
            row=1, column=0, sticky='w', padx=(0, 20), pady=(15, 0))

        self.padding_var = tk.StringVar(value="pkcs7")
        padding_combo = ttk.Combobox(frame, textvariable=self.padding_var,
                                     values=["pkcs7", "iso7816", "x923"],
                                     state="readonly", width=15)
        padding_combo.grid(row=1, column=1, sticky='w', pady=(15, 0))

        # Кнопка информации о дополнении
        ttk.Button(frame, text="?", command=self.show_padding_info,
                   width=2).grid(row=1, column=2, padx=(5, 0), pady=(15, 0))

    def create_password_section(self, parent):
        """Создание секции пароля"""
        frame = ttk.LabelFrame(parent, text="🔑 Безопасность", padding=15)
        frame.pack(fill='x', pady=(0, 15))

        # Пароль
        ttk.Label(frame, text="Пароль:", style='Header.TLabel').grid(
            row=0, column=0, sticky='w', pady=(0, 5))

        self.password_entry = ttk.Entry(frame, width=40, show="•")
        self.password_entry.grid(row=1, column=0, padx=(0, 10))

        # Подтверждение пароля
        ttk.Label(frame, text="Подтверждение:", style='Header.TLabel').grid(
            row=2, column=0, sticky='w', pady=(10, 5))

        self.confirm_entry = ttk.Entry(frame, width=40, show="•")
        self.confirm_entry.grid(row=3, column=0, padx=(0, 10))

        # Кнопка показа/скрытия пароля
        self.show_password_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Показать пароль",
                        variable=self.show_password_var,
                        command=self.toggle_password_visibility).grid(
            row=1, column=1, rowspan=2, padx=(10, 0))

        # Сложность пароля
        ttk.Label(frame, text="Сложность ключа:", style='Header.TLabel').grid(
            row=0, column=2, sticky='w', padx=(20, 0), pady=(0, 5))

        self.iterations_var = tk.IntVar(value=100000)
        ttk.Scale(frame, from_=10000, to=500000, variable=self.iterations_var,
                  length=150, orient='horizontal').grid(
            row=1, column=2, padx=(20, 0))

        self.iterations_label = ttk.Label(frame,
                                          text=f"Итераций: {self.iterations_var.get():,}")
        self.iterations_label.grid(row=2, column=2, padx=(20, 0))

        self.iterations_var.trace('w', self.update_iterations_label)

    def create_action_button_section(self, parent):
        """Создание секции с основной кнопкой"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=(0, 15))

        # Основная кнопка
        self.action_button = ttk.Button(frame, text="🚀 Начать обработку",
                                        command=self.start_processing, style='Custom.TButton',
                                        width=20)
        self.action_button.pack(side='left', padx=(0, 10))

        # Кнопка очистки
        ttk.Button(frame, text="🧹 Очистить",
                   command=self.clear_all, style='Custom.TButton',
                   width=15).pack(side='left', padx=(0, 10))

        # Кнопка информации
        ttk.Button(frame, text="📋 Информация",
                   command=self.show_info, style='Custom.TButton',
                   width=15).pack(side='left')

    def create_progress_section(self, parent):
        """Создание секции прогресса"""
        frame = ttk.LabelFrame(parent, text="📊 Прогресс", padding=15)
        frame.pack(fill='x', pady=(0, 15))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(frame, variable=self.progress_var,
                                            maximum=100, style='Progress.Horizontal.TProgressbar',
                                            length=650)
        self.progress_bar.pack(fill='x')

        self.progress_label = ttk.Label(frame, text="0%", font=('Arial', 10))
        self.progress_label.pack(pady=(5, 0))

    def create_log_section(self, parent):
        """Создание секции лога"""
        frame = ttk.LabelFrame(parent, text="📝 Журнал операций", padding=15)
        frame.pack(fill='both', expand=True)

        # Текстовое поле с прокруткой
        self.log_text = scrolledtext.ScrolledText(frame, height=8,
                                                  font=('Consolas', 9),
                                                  wrap='word')
        self.log_text.pack(fill='both', expand=True)

        # Кнопки управления логом
        log_buttons_frame = ttk.Frame(frame)
        log_buttons_frame.pack(fill='x', pady=(5, 0))

        ttk.Button(log_buttons_frame, text="Очистить лог",
                   command=self.clear_log, width=12).pack(side='left')

        ttk.Button(log_buttons_frame, text="Сохранить лог",
                   command=self.save_log, width=12).pack(side='left', padx=(5, 0))

        ttk.Button(log_buttons_frame, text="Экспорт настроек",
                   command=self.export_settings, width=15).pack(side='right')

    def create_bottom_buttons(self, parent):
        """Создание панели дополнительных кнопок"""
        frame = ttk.Frame(parent)
        frame.pack(fill='x', pady=(10, 0))

        ttk.Button(frame, text="🛠 Настройки",
                   command=self.open_settings, width=12).pack(side='left', padx=(0, 5))

        ttk.Button(frame, text="📖 Справка",
                   command=self.show_help, width=10).pack(side='left', padx=(0, 5))

        ttk.Button(frame, text="ℹ️ О программе",
                   command=self.show_info, width=12).pack(side='left')

    def on_mode_change(self):
        """Обработчик изменения режима"""
        mode = self.mode_var.get()
        if mode == "encrypt":
            self.status_var.set("Режим: Шифрование")
            self.log_message("Режим изменен на ШИФРОВАНИЕ", "INFO")
        else:
            self.status_var.set("Режим: Дешифрование")
            self.log_message("Режим изменен на ДЕШИФРОВАНИЕ", "INFO")

    def on_replace_mode_change(self):
        """Обработчик изменения режима замены"""
        if self.replace_mode.get():
            self.log_message("Включен режим замены исходного файла", "INFO")
        else:
            self.log_message("Режим замены отключен", "INFO")

    def select_input_file(self):
        """Выбор файла для обработки"""
        filename = filedialog.askopenfilename(
            title="Выберите файл для обработки",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Текстовые файлы", "*.txt *.docx *.pdf"),
                ("Изображения", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Архивы", "*.zip *.rar *.7z *.tar"),
                ("Видео/Аудио", "*.mp4 *.mp3 *.avi *.mkv")
            ]
        )
        if filename:
            self.input_file = filename
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, filename)
            self.log_message(f"Выбран файл: {os.path.basename(filename)}", "INFO")

    def toggle_password_visibility(self):
        """Показать/скрыть пароль"""
        show = self.show_password_var.get()
        self.password_entry.configure(show="" if show else "•")
        self.confirm_entry.configure(show="" if show else "•")

    def update_iterations_label(self, *args):
        """Обновить метку итераций"""
        value = self.iterations_var.get()
        self.iterations_label.config(text=f"Итераций: {value:,}")

        # Изменение цвета в зависимости от сложности
        if value < 50000:
            color = "#e74c3c"
        elif value < 200000:
            color = "#f39c12"
        else:
            color = "#27ae60"

        self.iterations_label.config(foreground=color)

    def show_padding_info(self):
        """Показать информацию о дополнении"""
        info = """
        Методы дополнения (padding):

        PKCS7 (Рекомендуется)
        • Стандартный метод
        • Наиболее безопасный
        • Поддерживается везде

        ISO7816
        • Используется в смарт-картах
        • Менее распространен

        x923
        • Альтернативный метод
        • Совместим с некоторыми системами

        Для большинства задач используйте PKCS7.
        """
        messagebox.showinfo("О дополнении", info)

    def log_message(self, message, level="INFO"):
        """Добавить сообщение в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Цвета и иконки для разных уровней
        level_config = {
            "INFO": ("[ℹ]", "black"),
            "SUCCESS": ("[✓]", "green"),
            "ERROR": ("[✗]", "red"),
            "WARNING": ("[⚠]", "orange"),
            "DEBUG": ("[🐛]", "gray")
        }

        icon, color = level_config.get(level, ("[?]", "black"))
        tag = f"[{timestamp}] {icon}"

        # Вставка с тегами для цветов
        self.log_text.insert(tk.END, f"{tag} ", f"timestamp_{level}")
        self.log_text.insert(tk.END, f"{message}\n", f"message_{level}")
        self.log_text.see(tk.END)

        # Настройка тегов для цветов
        self.log_text.tag_config(f"timestamp_{level}", foreground=color)
        self.log_text.tag_config(f"message_{level}", foreground="black")

        # Обновить статус бар
        self.status_var.set(f"{level}: {message}")

    def clear_log(self):
        """Очистить лог"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Журнал очищен", "INFO")

    def save_log(self):
        """Сохранить лог в файл"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить журнал",
            defaultextension=".log",
            filetypes=[("Лог файлы", "*.log"), ("Текстовые файлы", "*.txt")]
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Журнал сохранен в {filename}", "SUCCESS")
            except Exception as e:
                self.log_message(f"Ошибка сохранения: {str(e)}", "ERROR")

    def export_settings(self):
        """Экспорт настроек в JSON"""
        filename = filedialog.asksaveasfilename(
            title="Экспорт настроек",
            defaultextension=".json",
            filetypes=[("JSON файлы", "*.json")]
        )
        if filename:
            try:
                settings = {
                    "mode": self.mode_var.get(),
                    "padding": self.padding_var.get(),
                    "iterations": self.iterations_var.get(),
                    "replace_mode": self.replace_mode.get(),
                    "timestamp": datetime.now().isoformat()
                }
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                self.log_message(f"Настройки экспортированы в {filename}", "SUCCESS")
            except Exception as e:
                self.log_message(f"Ошибка экспорта: {str(e)}", "ERROR")

    def open_settings(self):
        """Открыть настройки"""
        messagebox.showinfo("Настройки",
                            "Расширенные настройки будут доступны в следующей версии.")

    def show_help(self):
        """Показать справку"""
        help_text = """
        КАК ИСПОЛЬЗОВАТЬ:

        1. Выберите файл для обработки
        2. Выберите режим (Зашифровать/Расшифровать)
        3. Отметьте "Заменить исходный файл" если нужно
        4. Введите пароль (минимум 8 символов)
        5. Подтвердите пароль
        6. Нажмите кнопку "НАЧАТЬ ОБРАБОТКУ"

        РЕЖИМЫ:
        • Замена исходного файла: файл будет изменен на месте
        • Создание копии: будет создан новый файл (режим по умолчанию)

        СОВЕТЫ:
        • Сделайте резервную копию перед работой в режиме замены
        • Используйте сложные пароли
        • Для важных файлов используйте высокую сложность ключа
        """
        messagebox.showinfo("Справка", help_text)

    def show_info(self):
        """Показать информацию о программе"""
        info_text = """
        File Encryptor Pro v2.1

        Возможности:
        • Шифрование и дешифрование файлов AES-256
        • Режим замены исходного файла
        • Использование безопасных паролей (PBKDF2)
        • Графический интерфейс с прогресс-баром
        • Журналирование операций

        Алгоритм:
        • AES-256 в режиме CBC
        • Соль и вектор инициализации (IV)
        • Дополнение PKCS7

        Безопасность:
        • Минимальная длина пароля: 8 символов
        • Настраиваемая сложность ключа
        • Проверка совпадения паролей

        Автор: File Encryptor Pro Team
        Версия: 2.1 (режим замены)
        Лицензия: MIT
        """
        messagebox.showinfo("О программе", info_text)

    def derive_key(self, password, salt=None):
        """Создание ключа из пароля с использованием PBKDF2"""
        if salt is None:
            salt = get_random_bytes(16)

        iterations = self.iterations_var.get()
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations,
            dklen=32  # AES-256 требует 32 байта
        )
        return key, salt

    def update_progress(self, value, status=""):
        """Обновить прогресс-бар"""
        self.progress_var.set(value)
        self.progress_label.config(text=f"{int(value)}%")
        if status:
            self.status_var.set(status)
        self.window.update_idletasks()

    def process_file_in_place(self, file_path, password, encrypt=True):
        """Обработка файла на месте (замена исходного)"""
        try:
            mode_text = "шифрование" if encrypt else "дешифрование"
            self.log_message(f"Начато {mode_text}: {os.path.basename(file_path)}", "INFO")
            self.update_progress(10, f"{mode_text.capitalize()}...")

            # Создаем временный файл
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"temp_enc_{os.path.basename(file_path)}")

            # Определяем функцию для обработки
            if encrypt:
                success = self._encrypt_to_temp(file_path, temp_file, password)
            else:
                success = self._decrypt_to_temp(file_path, temp_file, password)

            if not success:
                return False

            self.update_progress(80, "Замена файла...")

            # Резервное копирование (опционально)
            backup_path = file_path + ".backup"
            if os.path.exists(backup_path):
                os.remove(backup_path)
            shutil.copy2(file_path, backup_path)

            # Заменяем исходный файл
            shutil.move(temp_file, file_path)

            self.update_progress(100, f"{mode_text.capitalize()} завершено")
            self.log_message(f"Файл успешно обработан: {os.path.basename(file_path)}", "SUCCESS")

            # Удаляем резервную копию (опционально)
            # os.remove(backup_path)
            self.log_message(f"Резервная копия сохранена: {os.path.basename(backup_path)}", "INFO")

            return True

        except Exception as e:
            self.log_message(f"Ошибка обработки файла: {str(e)}", "ERROR")
            return False

    def _encrypt_to_temp(self, input_path, temp_path, password):
        """Шифрование во временный файл"""
        try:
            # Чтение исходного файла
            file_size = os.path.getsize(input_path)
            with open(input_path, 'rb') as f:
                data = f.read()

            self.update_progress(30, "Генерация ключа...")

            # Генерация ключа и соли
            salt = get_random_bytes(16)
            key, _ = self.derive_key(password, salt)
            iv = get_random_bytes(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)

            self.update_progress(50, "Шифрование данных...")

            # Шифрование с дополнением
            padded_data = pad(data, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)

            self.update_progress(70, "Сохранение...")

            # Запись во временный файл
            with open(temp_path, 'wb') as f:
                f.write(b'AES!')
                f.write(salt)
                f.write(iv)
                f.write(encrypted_data)

            return True

        except Exception as e:
            self.log_message(f"Ошибка шифрования: {str(e)}", "ERROR")
            return False

    def _decrypt_to_temp(self, input_path, temp_path, password):
        """Дешифрование во временный файл"""
        try:
            # Чтение зашифрованного файла
            with open(input_path, 'rb') as f:
                header = f.read(4)
                if header != b'AES!':
                    raise ValueError("Неверный формат файла")
                salt = f.read(16)
                iv = f.read(16)
                encrypted_data = f.read()

            self.update_progress(30, "Восстановление ключа...")

            # Восстановление ключа
            key, _ = self.derive_key(password, salt)
            cipher = AES.new(key, AES.MODE_CBC, iv)

            self.update_progress(50, "Дешифрование данных...")

            # Дешифрование
            decrypted_padded = cipher.decrypt(encrypted_data)
            decrypted_data = unpad(decrypted_padded, AES.block_size)

            self.update_progress(70, "Сохранение...")

            # Запись во временный файл
            with open(temp_path, 'wb') as f:
                f.write(decrypted_data)

            return True

        except ValueError as e:
            if "Padding" in str(e):
                self.log_message("Ошибка: Неверный пароль или поврежденный файл", "ERROR")
            else:
                self.log_message(f"Ошибка формата: {str(e)}", "ERROR")
            return False
        except Exception as e:
            self.log_message(f"Ошибка дешифрования: {str(e)}", "ERROR")
            return False

    def process_file_copy(self, input_path, output_path, encrypt=True):
        """Обработка файла с созданием копии"""
        try:
            mode_text = "шифрование" if encrypt else "дешифрование"
            self.log_message(f"Начато {mode_text}: {os.path.basename(input_path)}", "INFO")
            self.update_progress(10, "Чтение файла...")

            # Определяем функцию для обработки
            if encrypt:
                success = self._encrypt_to_temp(input_path, output_path, self.password_entry.get())
            else:
                success = self._decrypt_to_temp(input_path, output_path, self.password_entry.get())

            if success:
                self.update_progress(100, f"{mode_text.capitalize()} завершено")
                self.log_message(f"Файл сохранен: {os.path.basename(output_path)}", "SUCCESS")

            return success

        except Exception as e:
            self.log_message(f"Ошибка обработки файла: {str(e)}", "ERROR")
            return False

    def validate_inputs(self):
        """Проверка введенных данных"""
        errors = []

        # Проверка файла
        input_path = self.input_entry.get()
        if not input_path:
            errors.append("Выберите файл для обработки")
        elif not os.path.exists(input_path):
            errors.append(f"Файл не найден: {input_path}")

        # Проверка пароля
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not password:
            errors.append("Введите пароль")
        elif len(password) < 8:
            errors.append("Пароль должен содержать минимум 8 символов")
        elif password != confirm:
            errors.append("Пароли не совпадают")

        # Предупреждение для режима замены
        if self.replace_mode.get():
            mode = "шифрования" if self.mode_var.get() == "encrypt" else "дешифрования"
            if not messagebox.askyesno("Подтверждение",
                                       f"Вы собираетесь {mode} файл '{os.path.basename(input_path)}'.\n"
                                       f"Исходный файл будет заменен.\n\n"
                                       f"Рекомендуется сделать резервную копию.\n"
                                       f"Продолжить?"):
                return False

        if errors:
            messagebox.showerror("Ошибка валидации", "\n".join(errors))
            return False

        return True

    def clear_all(self):
        """Очистить все поля"""
        if messagebox.askyesno("Подтверждение",
                               "Очистить все поля и настройки?"):
            self.input_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            self.confirm_entry.delete(0, tk.END)
            self.clear_log()
            self.update_progress(0)
            self.status_var.set("Готов к работе")
            self.log_message("Все поля очищены", "INFO")

    def process_in_thread(self):
        """Обработка файла в отдельном потоке"""
        if self.is_processing:
            return

        self.is_processing = True

        try:
            # Получение данных
            input_path = self.input_entry.get()
            password = self.password_entry.get()
            mode = self.mode_var.get()
            encrypt = (mode == "encrypt")
            replace = self.replace_mode.get()

            # Блокировка кнопки
            self.action_button.config(state="disabled")

            # Выполнение операции
            success = False
            if replace:
                # Режим замены
                success = self.process_file_in_place(input_path, password, encrypt)
                output_path = input_path
            else:
                # Режим создания копии
                base, ext = os.path.splitext(input_path)
                if encrypt:
                    output_path = base + "_encrypted" + ext
                else:
                    output_path = base + "_decrypted" + ext
                success = self.process_file_copy(input_path, output_path, encrypt)

            # Показать результат
            if success:
                result_text = f"{'Зашифрован' if encrypt else 'Расшифрован'}: {os.path.basename(input_path)}"
                if not replace:
                    result_text += f"\nСохранен как: {os.path.basename(output_path)}"

                messagebox.showinfo("Успех", f"Операция завершена успешно!\n\n{result_text}")

                # Открыть папку с результатом (только если не режим замены)
                if not replace and messagebox.askyesno("Открыть папку", "Открыть папку с результатом?"):
                    folder = os.path.dirname(output_path) or "."
                    if sys.platform == "win32":
                        os.startfile(folder)
                    elif sys.platform == "darwin":
                        os.system(f'open "{folder}"')
                    else:
                        os.system(f'xdg-open "{folder}"')

        except Exception as e:
            self.log_message(f"Критическая ошибка: {str(e)}", "ERROR")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

        finally:
            self.is_processing = False
            self.update_progress(0)
            self.action_button.config(state="normal")

    def start_processing(self):
        """Начать обработку файла"""
        if self.is_processing:
            messagebox.showwarning("Внимание", "Операция уже выполняется!")
            return

        if not self.validate_inputs():
            return

        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.process_in_thread, daemon=True)
        thread.start()

    def run(self):
        """Запуск приложения"""
        # Центрирование окна
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}')

        # Начальное сообщение в лог
        self.log_message("Приложение запущено", "INFO")
        self.log_message("Режим: Создание копии файла", "INFO")
        self.log_message("Готов к работе", "SUCCESS")

        # Запуск главного цикла
        self.window.mainloop()


def main():
    """Точка входа в программу"""
    # Проверка наличия необходимых библиотек
    try:
        from Crypto.Cipher import AES
        app = FileEncryptorApp()
        app.run()
    except ImportError as e:
        print("Ошибка: Не установлены необходимые библиотеки!")
        print("Установите их с помощью: pip install pycryptodome или введите pip install -r requirements.txt")
        input("Нажмите Enter для выхода...")


if __name__ == "__main__":
    main()
