import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import serial
import threading
import time

class LoraControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LoRa Renk Kontrol Arayüzü")
        self.root.geometry("400x350")

        # Değişkenler
        self.selected_color = tk.StringVar()
        self.serial_connection = None
        self.is_connected = False

        # Stil
        style = ttk.Style()
        style.configure("TButton", padding=6, relief="flat", font=('Helvetica', 10))
        style.configure("TLabel", font=('Helvetica', 10))
        style.configure("Header.TLabel", font=('Helvetica', 12, 'bold'))

        # Arayüz elemanlarını oluştur
        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Bağlantı Bölümü ---
        connection_frame = ttk.LabelFrame(main_frame, text="Seri Port Bağlantısı", padding="10")
        connection_frame.pack(fill=tk.X, pady=5)

        ttk.Label(connection_frame, text="COM Port:").pack(side=tk.LEFT, padx=(0, 5))
        self.port_entry = ttk.Entry(connection_frame, width=10)
        self.port_entry.pack(side=tk.LEFT, padx=5)
        self.port_entry.insert(0, "COM3")  # Windows için varsayılan, kendi portunuzla değiştirin

        self.connect_button = ttk.Button(connection_frame, text="Bağlan", command=self.connect_serial)
        self.connect_button.pack(side=tk.LEFT, padx=5)

        self.disconnect_button = ttk.Button(connection_frame, text="Bağlantıyı Kes", command=self.disconnect_serial, state=tk.DISABLED)
        self.disconnect_button.pack(side=tk.LEFT, padx=5)

        # --- Renk Seçim Bölümü ---
        color_frame = ttk.LabelFrame(main_frame, text="Renk Seçimi", padding="10")
        color_frame.pack(fill=tk.X, pady=10)

        red_button = ttk.Button(color_frame, text="Kırmızı", command=lambda: self.select_color("kirmizi"))
        red_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        green_button = ttk.Button(color_frame, text="Yeşil", command=lambda: self.select_color("yesil"))
        green_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

        blue_button = ttk.Button(color_frame, text="Mavi", command=lambda: self.select_color("mavi"))
        blue_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        # --- Gönderme ve Durum Bölümü ---
        action_frame = ttk.Frame(main_frame, padding="5")
        action_frame.pack(fill=tk.X, pady=10)

        ttk.Label(action_frame, text="Seçilen Renk:", style="Header.TLabel").pack(pady=(0,5))
        self.selected_label = ttk.Label(action_frame, textvariable=self.selected_color, font=('Helvetica', 11, 'italic'), foreground="blue")
        self.selected_label.pack(pady=(0,10))
        self.selected_color.set("Henüz bir renk seçilmedi.")

        self.send_button = ttk.Button(action_frame, text="Seçili Rengi Gönder", command=self.send_data, state=tk.DISABLED)
        self.send_button.pack(fill=tk.X, ipady=10)

        # --- Durum Çubuğu ---
        self.status_label = ttk.Label(self.root, text="Bağlantı bekleniyor...", relief=tk.SUNKEN, anchor=tk.W, padding=5)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def select_color(self, color):
        """Renk butonuna basıldığında çağrılır."""
        self.selected_color.set(color.capitalize()) # Ekranda büyük harfle başlasın
        self.status_label.config(text=f"'{color}' rengi seçildi. Gönderilmeye hazır.")
        if self.is_connected:
            self.send_button.config(state=tk.NORMAL)

    def connect_serial(self):
        """Bağlan butonuna basıldığında yeni bir thread başlatır."""
        # Bağlantı işlemini arayüzü kilitlememesi için thread içinde çalıştır
        thread = threading.Thread(target=self._connect_thread)
        thread.daemon = True # Ana program kapanınca thread de kapansın
        thread.start()

    def _connect_thread(self):
        """Seri bağlantıyı kuran asıl fonksiyon (Thread içinde çalışır)."""
        port = self.port_entry.get()
        if not port:
            messagebox.showerror("Hata", "Lütfen geçerli bir COM portu girin.")
            return

        try:
            self.status_label.config(text=f"{port} portuna bağlanılıyor...")
            # Arduino'dan gelen '\n' karakterini beklediğimiz için baudrate'in eşleştiğinden emin olalım
            self.serial_connection = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Arduino'nun resetlenmesi için kısa bir bekleme süresi
            
            if self.serial_connection.is_open:
                self.is_connected = True
                self.status_label.config(text=f"Bağlantı başarılı: {port}")
                self.connect_button.config(state=tk.DISABLED)
                self.disconnect_button.config(state=tk.NORMAL)
                # Eğer bir renk seçilmişse gönder butonunu aktifleştir
                if "Henüz" not in self.selected_color.get():
                     self.send_button.config(state=tk.NORMAL)

        except serial.SerialException as e:
            self.is_connected = False
            self.status_label.config(text="Bağlantı hatası!")
            messagebox.showerror("Bağlantı Hatası", f"Porta bağlanılamadı: {e}")

    def disconnect_serial(self):
        """Bağlantıyı güvenli bir şekilde kapatır."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        self.is_connected = False
        self.status_label.config(text="Bağlantı kesildi.")
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

    def send_data(self):
        """Gönder butonuna basıldığında yeni bir thread başlatır."""
        thread = threading.Thread(target=self._send_thread)
        thread.daemon = True
        thread.start()

    def _send_thread(self):
        """Veriyi seri porta yazan asıl fonksiyon (Thread içinde çalışır)."""
        if not self.is_connected:
            messagebox.showwarning("Uyarı", "Veri göndermek için önce bağlantı kurmalısınız.")
            return
        
        color_to_send = self.selected_color.get().lower()
        if "henüz" in color_to_send:
            messagebox.showwarning("Uyarı", "Lütfen göndermek için bir renk seçin.")
            return
        
        try:
            # Arduino kodumuz readStringUntil('\n') kullandığı için verinin sonuna '\n' ekliyoruz.
            data_with_newline = color_to_send + '\n'
            self.serial_connection.write(data_with_newline.encode('utf-8'))
            self.status_label.config(text=f"'{color_to_send}' verisi başarıyla gönderildi.")
        except Exception as e:
            self.status_label.config(text="Veri gönderme hatası!")
            messagebox.showerror("Gönderme Hatası", f"Veri gönderilirken bir hata oluştu: {e}")
            self.disconnect_serial() # Hata oluşursa bağlantıyı kesmek iyi bir pratik

    def on_closing(self):
        """Pencere kapatıldığında seri portun açık kalmamasını sağlar."""
        self.disconnect_serial()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LoraControllerApp(root)
    # Pencere kapatma butonuna basıldığında on_closing fonksiyonunu çağır
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()