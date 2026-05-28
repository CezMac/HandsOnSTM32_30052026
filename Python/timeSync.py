import tkinter as tk
from tkinter import ttk
import serial
import time
import serial.tools.list_ports

class ComSenderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Warsztaty STM32 - Zegarek Binarny")
        self.port_var = tk.StringVar()          # ← zawsze istnieje
        self.ser = None                         # otwarta pozycja seryjna

        # ---------- UI ----------
        ttk.Label(root, text="Połącz port:", width=12).grid(row=0, column=0, sticky="w")
        ttk.Label(root, text=f"Status: brak połączenia").grid(row=3, column=0, sticky="w")
        self.combo_ports = ttk.Combobox(
            root,
            state="readonly",
            width=35
        )
        self.combo_ports.grid(row=0, column=1)

        # wypełniamy porty (jeśli lista nie jest pusta)
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if ports:
            self.combo_ports['values'] = ports
            self.port_var.set(ports[0])          # ← ustawiamy domyślną wartość
            self.combo_ports['textvariable'] = self.port_var
        else:
            self.combo_ports['values'] = ["--"]
            print("Brak wykrytych COM‑portów! Upewnij się, że masz uprawnienia.")

        ttk.Button(root, text="Połącz", command=self.connect).grid(
            row=0, column=2, padx=5
        )
        
        ttk.Button(root, text="Rozłącz", command=self.disconnect).grid(
            row=0, column=3, padx=5
        )

        for col in range(4):
            root.columnconfigure(col, weight=1)
        
        ttk.Button(root, text="Wyślij dane", command=self.send_data).grid(
            row=1, column=0, columnspan=4, padx=5, sticky="ew"
        )

        # label z pełnym czasem (HH:MM:SS)
        self.time_label = tk.Label(root, font=("Arial", 12))
        self.time_label.grid(row=2, column=0, pady=8, sticky="w")

        # timer – aktualizacja co 1 s
        self.update_hour()

    def connect(self):
        """Otworzyć wybrany port COM."""
        if not self.port_var.get():          # ← teraz sprawdzamy, czy ma wartość
            print("Brak wybranego portu!")
            return
        
        try:
            self.ser = serial.Serial(
                self.port_var.get(),
                baudrate=115200,
                timeout=1
            )
            print(f"Połączono z {self.port_var.get()}")
            ttk.Label(root, text=f"Status: Połączono z {self.port_var.get()}  ").grid(row=3, column=0, sticky="w")
        except Exception as e:               # np. port już nie istnieje, brak uprawnień itp.
            print("Błąd połączenia:", e)
            
    def disconnect(self):
        """Zamknij otwartą pozycję seryjna, oczyszczone UI."""
        if self.ser:                     # jeśli port jest już połączony
            try:
                self.ser.close()
                print("Port zamknięty.")
                ttk.Label(root, text=f"Status: Rozłączono z {self.port_var.get()}  ").grid(row=3, column=0, sticky="w")
            except Exception as e:
                print("Błąd przy zamykaniu portu:", e)

    def send_data(self):
        """Wyślij wiadomość SYNC HH:MM:SS;\nHH"""
        if not self.ser:
            print("Nie ma otwartej pozycji seryjnej!")
            ttk.Label(root, text=f"Status: brak połączenia!        ").grid(row=3, column=0, sticky="w")
            return

        now = time.strftime("%H:%M:%S")
        msg = (f"SYNC {now};\n\r").encode()
        
        try:
            self.ser.write(msg)
            print(msg.decode())
        except Exception as e:
            print("Błąd seryjny:", e)
            ttk.Label(root, text=f"Status: brak połączenia!        ").grid(row=3, column=0, sticky="w")

    def update_hour(self):
        """Aktualizacja label‑a pełnym czasem (HH:MM:SS)."""
        hour = time.strftime("%H:%M:%S")
        self.time_label.config(text=hour)
        self._timer = self.root.after(1000, self.update_hour)

if __name__ == "__main__":
    root = tk.Tk()
    app = ComSenderApp(root)
    root.mainloop()
