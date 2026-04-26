import threading
import base64
from io import BytesIO
from socket import *
from customtkinter import *
from PIL import Image, ImageGrab  # pip install Pillow

# --- ЦВЕТА ---
BG_COLOR = "#1A1A2E"
FIELD_COLOR = "#16213E"
ACCENT_COLOR = "#0F3460"
TEXT_COLOR = "#E94560"


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.title("Square Chat")
        self.geometry('600x600')
        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. ОБЛАСТЬ ЧАТА (Теперь это Frame, где можно рисовать картинки)
        self.chat_frame = CTkScrollableFrame(self, fg_color=FIELD_COLOR, corner_radius=0)
        self.chat_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # 2. ПОЛЕ ВВОДА
        self.input_area = CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.input_area.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        self.message_entry = CTkEntry(self.input_area, placeholder_text='Текст или Ctrl+V...',
                                      height=45, corner_radius=0, fg_color=FIELD_COLOR, border_color=ACCENT_COLOR)
        self.message_entry.pack(side=LEFT, fill=X, expand=True)

        self.message_entry.bind("<Return>", lambda e: self.send_text())
        self.message_entry.bind("<Control-v>", self.handle_paste)

        self.send_btn = CTkButton(self.input_area, text='SEND', width=70, height=45,
                                  corner_radius=0, fg_color=TEXT_COLOR, command=self.send_text)
        self.send_btn.pack(side=RIGHT, padx=(5, 0))

        self.username = 'Artem1'
        self.connect_to_server()

    # ФУНКЦИЯ ОТОБРАЖЕНИЯ (Текст или Картинка)
    def display_item(self, author, text=None, img_str=None):
        # Создаем контейнер для одного сообщения
        msg_box = CTkFrame(self.chat_frame, fg_color="transparent")
        msg_box.pack(fill=X, pady=5)

        title = CTkLabel(msg_box, text=f"{author}:", font=("Arial", 12, "bold"), text_color=TEXT_COLOR)
        title.pack(anchor="w")

        if text:
            lbl = CTkLabel(msg_box, text=text, font=("Arial", 14), wraplength=500, justify="left")
            lbl.pack(anchor="w", padx=10)

        if img_str:
            try:
                img_data = base64.b64decode(img_str)
                img = Image.open(BytesIO(img_data))
                # Ограничиваем размер для предпросмотра
                img.thumbnail((300, 300))
                ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)
                img_label = CTkLabel(msg_box, image=ctk_img, text="")
                img_label.pack(anchor="w", padx=10, pady=5)
            except:
                pass

    def handle_paste(self, event=None):
        try:
            img = ImageGrab.grabclipboard()
            if isinstance(img, Image.Image):
                img.thumbnail((600, 600))
                buf = BytesIO()
                img.convert("RGB").save(buf, format="JPEG", quality=70)
                img_str = base64.b64encode(buf.getvalue()).decode()

                # Показываем у себя
                self.display_item("Я", img_str=img_str)
                # Отправляем
                self.sock.sendall(f"IMAGE@{self.username}@{img_str}\n".encode())
                return "break"
        except:
            pass

    def send_text(self):
        msg = self.message_entry.get()
        if msg:
            self.display_item("Я", text=msg)
            try:
                self.sock.sendall(f"TEXT@{self.username}@{msg}\n".encode())
            except:
                pass
            self.message_entry.delete(0, END)

    def connect_to_server(self):
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)
            self.sock.connect(('localhost', 1111))
            threading.Thread(target=self.recv, daemon=True).start()
        except:
            self.display_item("СИСТЕМА", text="Сервер не найден")

    def recv(self):
        while True:
            try:
                data = self.sock.recv(1024 * 1024).decode()
                if not data: break
                for line in data.split('\n'):
                    if not line: continue
                    parts = line.split('@')
                    if parts[0] == "TEXT":
                        self.display_item(parts[1], text=parts[2])
                    elif parts[0] == "IMAGE":
                        self.display_item(parts[1], img_str=parts[2])
            except:
                break


if __name__ == "__main__":
    MainWindow().mainloop()
