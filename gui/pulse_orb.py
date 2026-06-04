import customtkinter as ctk

class PulseOrb:
    def __init__(self, parent):
        self.canvas = ctk.CTkCanvas(
            parent,
            width=180,
            height=180,
            highlightthickness=0,
            bg="#2b2b2b"
        )
        self.center = 90
        self.radius = 25
        self.min_radius = 25
        self.max_radius = 50
        self.opacity = 100
        self.growing = True
        self.active = False
        self.idle_core_colour = "#b0d8eb"
        self.idle_colour = "#34b1eb"
        self.thinking_colour = "#ffae17"
        self.thinking_core_colour = "#ffcf75"
        self.listening_colour = "#ff3b41"
        self.listenting_core_colour = "#ff8084"
        self.processing_colour = "#21ff46"
        self.processing_core_colour = "#94ffa6"
        self.core = self.canvas.create_oval(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            width=4,
            outline="#b0d8eb",
            fill="#b0d8eb"
        )

        self.circle = self.canvas.create_oval(
            self.center - self.radius,
            self.center - self.radius,
            self.center + self.radius,
            self.center + self.radius,
            width=4,
            outline="#34b1eb"
        )

    def set_orb_colour(self, status):
        match status:
            case "idle":
                self.canvas.itemconfig(
                    self.core,
                    fill=self.idle_core_colour,
                    outline = self.idle_core_colour
                )
                self.canvas.itemconfig(
                    self.circle,
                    outline = self.idle_colour
                )
            case "thinking":
                self.canvas.itemconfig(
                    self.core,
                    fill=self.thinking_core_colour,
                    outline = self.thinking_core_colour
                )
                self.canvas.itemconfig(
                    self.circle,
                    outline = self.thinking_colour
                )
            case "listening":
                self.canvas.itemconfig(
                    self.core,
                    fill=self.listenting_core_colour,
                    outline = self.listenting_core_colour
                )
                self.canvas.itemconfig(
                    self.circle,
                    outline = self.listening_colour
                )
            case "processing audio":
                self.canvas.itemconfig(
                    self.core,
                    fill=self.processing_core_colour,
                    outline = self.processing_core_colour
                )
                self.canvas.itemconfig(
                    self.circle,
                    outline = self.processing_colour
                )


    def start(self):
        if self.active:
            return
        self.active = True
        self.animate()

    def stop(self):
        if not self.active:
            return
        self.active = False
        self.radius = self.min_radius
        self.update_circle()

    def animate(self):
        if not self.active:
            return
        if self.growing:
            self.radius += 2
            if self.radius >= self.max_radius:
                self.growing = False
        else:
            self.radius -= 2
            if self.radius <= self.min_radius:
                self.growing = True
        self.update_circle()
        self.canvas.after(30, self.animate)

    def update_circle(self):
        r = self.radius

        self.canvas.coords(
            self.circle,
            self.center - r,
            self.center - r,
            self.center + r,
            self.center + r,
        )

