import customtkinter as ctk
import psutil
import threading
import vars
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
import pyttsx3
import speech_recognition
import winsound
import time


def show_context():
    try:
        file = open("history.txt", "r")
        context = file.read()
        file.close()
        print(context)
    except FileNotFoundError:
        print("No previous history found")


class GUI:
    def __init__(self):
        self.refresh_button, self.mode_button, self.speak_button, self.send_button = None, None, None, None
        self.listening_stat, self.action_stat = None, None
        self.action_codes = [["Searching", "╬"], ["Listening", "╠"], ["Processing", "╩"], ["Idle", "╦"], ["Error", "┼"]]
        self.modes = [["Chat", "✉"], ["Speak", "🤙"]]

        self.model = OllamaLLM(model=vars.JARVIS_MODEL)
        self.prompt = ChatPromptTemplate.from_template(vars.TEMPLATE)
        self.chain = self.prompt | self.model
        self.speak = pyttsx3.init()

        self.recognizer = speech_recognition.Recognizer()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        self.root = ctk.CTk()
        self.root.geometry("600x400")
        self.root.title("J.A.R.V.I.S. - The Virtual Assistant")
        self.root.resizable(False, False)

        # Frame Initialization
        self.name_frame = ctk.CTkFrame(self.root, width=180, height=50)        # Name Frame
        self.name_frame.place(x=5, y=5)
        self.context_frame = ctk.CTkFrame(self.root, width=180, height=175)    # Context Frame
        self.context_frame.place(x=5, y=60)
        self.commands_frame = ctk.CTkFrame(self.root, width=180, height=75)    # Command Frame
        self.commands_frame.place(x=5, y=295)
        self.modes_frame = ctk.CTkFrame(self.root, width=180, height=55)       # Modes Frame
        self.modes_frame.place(x=5, y=237)
        self.resources_frame = ctk.CTkFrame(self.root, width=405, height=50)   # Resources Frame
        self.resources_frame.place(x=190, y=5)
        self.listening_frame = ctk.CTkFrame(self.root, width=200, height=50)   # Listening Frame
        self.listening_frame.place(x=190, y=60)
        self.action_frame = ctk.CTkFrame(self.root, width=200, height=50)      # Action Frame
        self.action_frame.place(x=395, y=60)
        self.chat_frame = ctk.CTkFrame(self.root, width=405, height=280)       # Chat Frame
        self.chat_frame.place(x=190, y=115)

        self.text()
        self.status()
        self.buttons()

        self.thread1 = threading.Thread(target=self.system)
        self.thread1.start()

        # Other
        self.input_field = ctk.CTkEntry(self.chat_frame, width=395, placeholder_text="Type Here")  # Chat Input
        self.input_field.place(anchor="center", relx=0.5, rely=0.925)

        self.root.mainloop()

    def text(self):
        title = ctk.CTkLabel(self.name_frame, text="J.A.R.V.I.S", font=("Roboto", 35))
        title.place(anchor="center", relx=0.5, rely=0.5)

        listening_text = ctk.CTkLabel(self.listening_frame, text="Listening: ", font=("Roboto", 30))
        listening_text.place(anchor="w", rely=0.5, relx=0.05)

        action_text = ctk.CTkLabel(self.action_frame, text="Main Act: ", font=("Roboto", 30))
        action_text.place(anchor="w", rely=0.5, relx=0.05)

        cpu_text = ctk.CTkLabel(self.resources_frame, text="CPU", font=("Roboto", 15))
        cpu_text.place(anchor="w", rely=0.25, relx=0.025)

        ram_text = ctk.CTkLabel(self.resources_frame, text="RAM", font=("Roboto", 15))
        ram_text.place(anchor="w", rely=0.75, relx=0.025)

        credits_1 = ctk.CTkLabel(self.root, text="Made by: Ethan Peter", font=("Roboto", 15))
        credits_1.place(relx=0.01, rely=0.925)

    def status(self):
        self.listening_stat = ctk.CTkFrame(self.listening_frame, width=40, height=40, fg_color="red")
        self.listening_stat.place(anchor="e", rely=0.5, relx=0.95)

        self.action_stat = ctk.CTkLabel(self.action_frame, text=self.action_codes[3][1], font=("Roboto", 30))
        self.action_stat.place(anchor="e", rely=0.5, relx=0.925)

    def buttons(self):
        font_size = 30

        run_button = ctk.CTkButton(self.context_frame, text="Start", width=170, height=50,
                                   font=("Roboto", font_size), command=self.get_start_info)
        run_button.place(anchor="center", relx=0.5, y=30)

        customize_button = ctk.CTkButton(self.context_frame, text="Customize", width=170, height=50,
                                         font=("Roboto", font_size))
        customize_button.place(anchor="center", relx=0.5, y=85)

        context_button = ctk.CTkButton(self.context_frame, text="History", width=170, height=50,
                                       font=("Roboto", font_size), command=show_context)
        context_button.place(anchor="center", relx=0.5, y=140)

        self.mode_button = ctk.CTkSegmentedButton(self.modes_frame, values=[self.modes[0][1], self.modes[1][1]],
                                                  width=170, height=50, font=("Roboto", font_size))
        self.mode_button.place(anchor="center", relx=0.3, rely=0.49)

        self.refresh_button = ctk.CTkButton(self.modes_frame, text="🔄", width=65, height=50,
                                            font=("Roboto", font_size))
        self.refresh_button.place(anchor="center", relx=0.8, rely=0.49)

        self.speak_button = ctk.CTkButton(self.commands_frame, text="🎤", width=80, height=60,
                                          font=("Roboto", font_size))
        self.speak_button.place(anchor="center", relx=0.25, y=35)

        self.send_button = ctk.CTkButton(self.commands_frame, text="⌨", width=80, height=60,
                                         font=("Roboto", font_size))
        self.send_button.place(anchor="center", relx=0.75, y=35)

    def system(self):
        cpu_usage = psutil.cpu_percent(2)
        ram_usage = psutil.virtual_memory()[2]

        cpu_stat = ctk.CTkProgressBar(self.resources_frame, width=340, height=15, progress_color="red")
        cpu_stat.set(cpu_usage / 100)
        cpu_stat.place(anchor="w", rely=0.25, relx=0.125)

        ram_stat = ctk.CTkProgressBar(self.resources_frame, width=340, height=15, progress_color="green")
        ram_stat.set(ram_usage / 100)
        ram_stat.place(anchor="w", rely=0.75, relx=0.125)

        while True:
            cpu_usage = psutil.cpu_percent(1)
            ram_usage = psutil.virtual_memory()[2]

            cpu_stat.set(cpu_usage / 100)
            ram_stat.set(ram_usage / 100)

    def get_start_info(self):
        if not vars.ACTIVE:
            vars.ACTIVE = True
            if self.mode_button.get() == self.modes[1][1]:
                self.refresh_button.configure(fg_color="red")
                self.speak_button.configure(fg_color="red")
                self.send_button.configure(fg_color="red")
                time.sleep(10)
                self.main_ai_model()
            elif self.mode_button.get() == self.modes[0][1]:
                self.refresh_button.configure(fg_color="red")
                self.speak_button.configure(fg_color="green")
                self.send_button.configure(fg_color="green")
                time.sleep(10)
                self.system()
            else:
                pass
        if vars.ACTIVE:
            pass

    def main_ai_model(self):
        context = ""
        start_up = "JARVIS: Hello sir, I am now active and ready to assist you."

        try:
            file = open("history.txt", "r")
            context = file.read()
            file.close()
        except FileNotFoundError:
            print("No previous history found.")

        context = context + start_up
        print(start_up)
        self.speak.say(start_up[8:])
        self.speak.runAndWait()

        while True:
            user_in = self.record_speech()
            print(f"You: {user_in}")
            start = time.time()
            if str(user_in).lower() == "bye":
                self.action_stat.set(self.action_codes[2][1])
                result = self.chain.invoke({"context": context, "question": "bye"})
                print("Jarvis: " + result, end="")
                self.speak.say(result)
                self.speak.runAndWait()
                context += f"\nUser: {user_in}\nJarvis: {result}\n"

                file = open("history.txt", "a")
                file.write(context)
                file.close()
                print("Chat history saved.")
                self.action_stat.set(self.action_codes[3][1])
                break

            self.action_stat.set(self.action_codes[2][1])
            result = self.chain.invoke({"context": context, "question": user_in})

            print("Jarvis: " + result, end="")
            self.speak.say(result)
            self.speak.runAndWait()
            end = time.time()
            self.action_stat.set(self.action_codes[3][1])

            context += f"\nUser: {user_in}\nJarvis: {result}\n"
            print(f"Jarvis took {end - start} seconds to answer")

    def step_ai_model(self):
        context = ""
        start_up = "JARVIS: Hello sir, I am now active and ready to assist you."

        try:
            file = open("history.txt", "r")
            context = file.read()
            file.close()
        except FileNotFoundError:
            print("No previous history found.")

        context = context + start_up
        print(start_up)
        self.speak.say(start_up[8:])
        self.speak.runAndWait()

        if self.speak_button.get() == "🎤":
            user_in = self.record_speech()
            print(f"You: {user_in}")
            start = time.time()
            if str(user_in).lower() == "bye":
                self.action_stat.set(self.action_codes[2][1])
                result = self.chain.invoke({"context": context, "question": "bye"})
                print("Jarvis: " + result, end="")
                self.speak.say(result)
                self.speak.runAndWait()
                context += f"\nUser: {user_in}\nJarvis: {result}\n"

                file = open("history.txt", "a")
                file.write(context)
                file.close()
                print("Chat history saved.")
                self.action_stat.set(self.action_codes[3][1])

            self.action_stat.set(self.action_codes[2][1])
            result = self.chain.invoke({"context": context, "question": user_in})

            print("Jarvis: " + result, end="")
            self.speak.say(result)
            self.speak.runAndWait()
            end = time.time()
            self.action_stat.set(self.action_codes[3][1])

            context += f"\nUser: {user_in}\nJarvis: {result}\n"
            print(f"Jarvis took {end - start} seconds to answer")

        if self.send_button.get() == "⌨":
            user_in = str(self.input_field.get())
            print(f"You: {user_in}")
            start = time.time()
            if str(user_in).lower() == "bye":
                self.action_stat.set(self.action_codes[2][1])
                result = self.chain.invoke({"context": context, "question": "bye"})
                print("Jarvis: " + result, end="")
                self.speak.say(result)
                self.speak.runAndWait()
                context += f"\nUser: {user_in}\nJarvis: {result}\n"

                file = open("history.txt", "a")
                file.write(context)
                file.close()
                print("Chat history saved.")
                self.action_stat.set(self.action_codes[3][1])

            self.action_stat.set(self.action_codes[2][1])
            result = self.chain.invoke({"context": context, "question": user_in})

            print("Jarvis: " + result, end="")
            self.speak.say(result)
            self.speak.runAndWait()
            end = time.time()
            self.action_stat.set(self.action_codes[3][1])

            context += f"\nUser: {user_in}\nJarvis: {result}\n"
            print(f"Jarvis took {end - start} seconds to answer")

    def record_speech(self):
        while 1:
            try:
                with speech_recognition.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.listening_stat.configure(fg_color="green")
                    self.action_stat.configure(text=self.action_codes[1][1])
                    print("listening...")
                    winsound.Beep(frequency=2500, duration=250)
                    audio = self.recognizer.listen(source)
                    winsound.Beep(frequency=2000, duration=250)
                    self.listening_stat.configure(fg_color="red")
                    self.action_stat.configure(text=self.action_codes[3][1])
                    return self.recognizer.recognize_google(audio)
            except speech_recognition.UnknownValueError as e:
                print("Could not understand audio: {0}".format(e))
                winsound.Beep(frequency=1000, duration=250)
                self.listening_stat.configure(fg_color="yellow")
            except speech_recognition.RequestError:
                print("Request Error Occurred")
                winsound.Beep(frequency=1000, duration=250)
                self.listening_stat.configure(fg_color="purple")
                self.action_stat.configure(text=self.action_codes[4][1])


if __name__ == "__main__":
    GUI()
