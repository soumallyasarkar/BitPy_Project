from PIL import Image
import customtkinter as ctk
import tkinter as tk
import subprocess
import threading
import socket
import sys



# List of subprocesses
subprocesses = []

# To Run Sender File
def start_send_ui():
    proc = subprocess.Popen([sys.executable, 'Drop_ui.py'])
    subprocesses.append(proc)

# To Run Receiver File
def start_receive_ui():
    proc = subprocess.Popen([sys.executable, 'Receive_ui.py'])
    subprocesses.append(proc)

# To handle window close events
def on_closing():
    for proc in subprocesses:
        proc.terminate()  
    app.destroy() 



# Setting up the main window
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")
app = ctk.CTk()
app.geometry("500x350")
app.title("BitPy Transfer")




# Centering The Window
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
window_width = 500
window_height = 350
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
app.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")




# png loading
send_icon = ctk.CTkImage(light_image=Image.open("Sbutton.png"), size=(50, 50))
receive_icon = ctk.CTkImage(light_image=Image.open("Rbutton.png"), size=(50, 50))

frame = ctk.CTkFrame(app, width=460, height=120, corner_radius=20)
frame.pack(padx=(0, 0), pady=(50, 0))

title_label = ctk.CTkLabel(frame, text="BitPy Transfer, Transfer Every Bits", font=("Arial", 22))
title_label.pack(pady=(20, 20))




# Displaying the IP of the current device
system_ip = socket.gethostbyname(socket.gethostname())
text_widget = tk.Text(frame, font=("Arial", 12), height=1, width=30, wrap='none', bg='#212121', fg='white', bd=0)
text_widget.tag_configure("center", justify='center')
text_widget.insert(tk.END, "Your System IP is: " + system_ip)
text_widget.tag_add("center", "1.0", "end")
text_widget.configure(state='normal')
text_widget.pack(padx=(30, 30), pady=(10, 5))





# Create a frame to hold the buttons
button_frame = ctk.CTkFrame(frame)
button_frame.pack(padx=(10, 10), pady=(20, 10))



# Send Button Function
def send_button_clicked():
    threading.Thread(target=start_send_ui).start()
send_button = ctk.CTkButton(button_frame, text="Send File", width=10, height=10, corner_radius=70,
                            font=("Arial", 14), fg_color="skyblue", text_color="black",
                            hover_color="darkblue", image=send_icon, compound="left",
                            command=send_button_clicked)
send_button.grid(row=0, column=0, pady=10, padx=20)


# Receive Button Function
def receive_button_clicked():
    threading.Thread(target=start_receive_ui).start()
receive_button = ctk.CTkButton(button_frame, text="Receive File", width=10, height=10, corner_radius=70,
                               font=("Arial", 14), fg_color="blue", text_color="black",
                               hover_color="darkblue", image=receive_icon, compound="left",
                               command=receive_button_clicked)
receive_button.grid(row=0, column=1, pady=10, padx=20)




# Bind the on_closing function to the window close event
app.protocol("WM_DELETE_WINDOW", on_closing)

# Run the main loop
app.mainloop()
