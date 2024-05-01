import tkinter
import tkinter.messagebox
import customtkinter
from main import Recorder
import threading

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.recorder = Recorder()
        self.recorder.gui = self

        self.recorder.tts.status_update_callback = self.update_status
        # Configure window
        self.title("AlwaysReddy GUI")
        self.geometry(f"{1100}x{580}")
 
        # Configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        
        #Set Icon
        self.iconbitmap(default="Speaker_Icon.ico")

        # Create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=700, height=1200)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")

        # Create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="Always Reddy", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_1_event)
        self.sidebar_button_1.configure(text="Record", fg_color="green")
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, command=self.sidebar_button_2_event)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2.configure(text="Clear History", fg_color="red")
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(20, 20))

        # Create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Enter Text HERE")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(20, 0), pady=(20, 20), sticky="nsew")
        self.entry.bind("<Return>", lambda event: self.submit_text())
        
        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"), text="Submit", command=self.submit_text)
        self.main_button_1.grid(row=3, column=3, padx=(20, 20), pady=(20, 20), sticky="nsew")

        # Set default values
        self.sidebar_button_1_state = True
        self.sidebar_button_2_state = True
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")

        self.recorder.tts.status_update_callback = self.update_status
        
        self.recorder = Recorder()
        print("Recorder instance created.")  # Debug print

        self.recorder.tts.status_update_callback = self.update_status
        print("status_update_callback set.")  # Debug print
        
    def submit_text(self, event=None):
        text = self.entry.get()
        if text.strip():
            self.recorder.handle_response(text)
            self.entry.delete(0, "end")

        
    def update_textbox(self, message):
        self.textbox.insert("end", message + "\n")
        self.textbox.see("end")
        print("Textbox updated successfully.")  # Confirmation that the function executed
            
    def set_transcribing_state(self, is_transcribing):
        if is_transcribing:
            self.sidebar_button_1.configure(state="disabled", text="Transcribing...")
        else:
            self.sidebar_button_1.configure(state="normal", text="Record", fg_color="green")
            self.sidebar_button_1_state = True

    def sidebar_button_1_event(self):
        if self.sidebar_button_1_state:
            self.sidebar_button_1.configure(fg_color="red", text="Stop Recording")
            self.sidebar_button_1_state = False
            self.sidebar_button_2.configure(fg_color="blue", text="cancel")
            self.recorder.start_recording()  # Start recording
        else:
            self.set_transcribing_state(True)  # Set the button to "Transcribing..." state
            self.recorder.stop_recording()  # Stop recording
            self.set_transcribing_state(False)  # Reset the button after transcription
        print("sidebar_button_1 click")

    def sidebar_button_2_event(self):
        if self.sidebar_button_2.cget("text") == "cancel":
            self.sidebar_button_1.configure(fg_color="green", text="Record")
            self.sidebar_button_1_state = True
            self.sidebar_button_2.configure(fg_color="red", text="Clear History")
            self.recorder.cancel_all()  # Cancel recording and TTS
        else:
            self.recorder.clear_messages()  # Clear message history
        print("sidebar_button_2 click")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def update_status(self, status):
        self.textbox.insert("end", status + "\n")
        self.textbox.see("end")

if __name__ == "__main__":
    app = App()
    recorder = Recorder()  # Create a new Recorder instance
    app.recorder = recorder  # Assign the Recorder instance to the App's recorder attribute
    print("Recorder instance created and assigned to App.")  # Debug print
    
    recorder.gui = app  # Set the gui attribute of the Recorder instance to the App instance
    print("App instance assigned to Recorder's gui attribute.")  # Debug print
    
    recorder_thread = threading.Thread(target=recorder.run)
    recorder_thread.start()
    app.mainloop()
