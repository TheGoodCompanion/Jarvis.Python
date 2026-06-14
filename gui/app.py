import customtkinter as ctk
from gui.pulse_orb import PulseOrb
import queue

class JarvisGui:
    def __init__(self):
        self.ui_queue = queue.Queue()
        self.on_status_changed = None
        self.action_dict = {}
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.root = ctk.CTk()
        self.root.title("Jarvis")
        self.root.geometry("1900x1000")
        
        self.build_layout()
        self.process_ui_queue()

    def build_layout(self):
        self.main_frame = ctk.CTkFrame(self.root, height=200)
        self.main_frame.pack(fill="both", padx=20, pady=20)

        self.main_panel = ctk.CTkFrame(self.root)
        self.main_panel.pack(side="left", fill="both", expand=True, pady=10)

        self.action_panel = ctk.CTkFrame(self.root)
        self.action_panel.pack(side="right", fill="both", expand=True, pady=10)

        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="Idle",
            font=("Arial", 32, "bold")
        )
        self.status_label.pack(pady=20)

        self.pulse_orb = PulseOrb(self.main_frame)
        self.pulse_orb.canvas.pack(pady=10)

        self.transcipt_box = ctk.CTkTextbox(
            self.main_panel,
            font=("Consolas", 15)
        )
        self.transcipt_box.pack(fill="both", expand= True, padx=20, pady=20)
        self.transcipt_box.insert("end", "JARVIS Ready...\n")

        self.context_box = ctk.CTkTextbox(
            self.main_panel,
            height=120,
            font=("Consolas", 14)
        )
        self.context_box.pack(fill="x", padx=20, pady=(0,20))
        self.context_box.insert("end", "Context will show here...\n")

        self.action_box = ctk.CTkTextbox(
            self.action_panel,
            font=("Consolas", 14)
        )
        self.action_box.pack(fill="both", expand=True, padx=20, pady=20)
        self.action_box.insert("end", "Actions will show here...\n")
        


    def queue_status(self, status):
        self.ui_queue.put(("status", status))

    def queue_transcipt(self, transcipt):
        self.ui_queue.put(("transcipt", transcipt))

    def queue_response(self, response):
        self.ui_queue.put(("response", response))

    def queue_context(self, context):
        self.ui_queue.put(("context", context))

    def queue_action(self, action):
        self.ui_queue.put(("action", action))
    
    def queue_action_playing(self, action):
        self.ui_queue.put(("action_playing", action))

    def process_ui_queue(self):
        while not self.ui_queue.empty():
            eventtype, payload = self.ui_queue.get()

            if eventtype == "status":
                self.set_status(payload)
                self.pulse_orb.set_orb_colour(payload)
            elif eventtype == "transcipt":
                self.add_message("You", payload)
            elif eventtype == "response":
                self.add_message("Jarvis", payload)
            elif eventtype == "context":
                self.add_context(payload)
            elif eventtype == "action":
                self.add_action(payload)
            elif eventtype == "action_playing":
                self.add_action_playing(payload)

        self.root.after(50, self.process_ui_queue)

    def set_status(self, status):
        self.status_label.configure(
            text=status.replace("_", " ").title()
        )
        if status == "idle":
            self.pulse_orb.stop()
        else:
            self.pulse_orb.start()

    def add_message(self, speaker, message):
        self.transcipt_box.insert("end", f"{speaker}: {message}\n")
        self.transcipt_box.see("end")

    def add_context(self, context):
        self.context_box.delete("1.0", "end")
        self.context_box.insert("end", f"{context}\n")
        self.context_box.see("end")
    
    def add_action(self, action):
        if action == "STARTING":
            self.action_dict.clear()
            self.action_box.delete("1.0", "end")
            return
        self.action_dict[f"{action.get("apiendpoint")} - Params: {action.get("parameters")}"] = ""
        self.action_box.delete("1.0", "end")
        for k, v in self.action_dict.items():
            self.action_box.insert("end", f"{k} {v}\n")
            self.action_box.see("end")
        
    def add_action_playing(self, action):
        self.action_dict[f"{action.get("apiendpoint")} - Params: {action.get("parameters")}"] = "Completed"
        self.action_box.delete("1.0", "end")
        for k, v in self.action_dict.items():
            self.action_box.insert("end", f"{k} {v}\n")
            self.action_box.see("end")

    def run(self):
        self.root.mainloop()