import tkinter as tk
from tkinter import messagebox, filedialog
from controller import handle_login, handle_registration, handle_mode_selection, getFiles,AddFileTodatabase,startSending,Messages,stopSending
import os
import globalLogger


def open_login_window(root):
    root.destroy()
    open_username_password_window("login")

def open_registration_window(root):
    root.destroy()
    open_username_password_window("register")

def open_username_password_window(action):
    def submit():
        username = username_entry.get()
        password = password_entry.get()

        if action == "login":
            success, message = handle_login(username, password)
            if success:
                messagebox.showinfo("Success", message)
                open_sender_receiver_window(username,window)
            else:
                messagebox.showerror("Error", message)
        elif action == "register":
            success, message = handle_registration(username, password)
            if success:
                messagebox.showinfo("Success", message)
                open_sender_receiver_window(username,window)
            else:
                messagebox.showerror("Error", message)

    window = tk.Tk()
    window.title("Username and Password")
    window.geometry("300x200")

    tk.Label(window, text="Username:").pack(pady=5)
    username_entry = tk.Entry(window)
    username_entry.pack(pady=5)

    tk.Label(window, text="Password:").pack(pady=5)
    password_entry = tk.Entry(window, show="*")
    password_entry.pack(pady=5)

    tk.Button(window, text="Submit", command=submit).pack(pady=10)
    window.mainloop()

def open_sender_receiver_window(username,root):
    root.destroy()
    def select_sender():
        open_sender_window(username,window)

    def select_receiver():
        handle_mode_selection(username, "receiver")
    window = tk.Tk()
    window.title("Select Mode")
    window.geometry("300x200")

    tk.Label(window, text=f"Welcome {username}!").pack(pady=10)
    tk.Button(window, text="Sender", command=select_sender).pack(pady=5)
    tk.Button(window, text="Receiver", command=select_receiver).pack(pady=5)

    window.mainloop()



def open_sender_window(username,root):
    # Create a new window
    root.destroy()
    window = tk.Tk()
    window.title("Sender Window")
    window.geometry("800x400")

    is_sending = False  # Initially, sending is not in progress

    def populate_files():
        file_listbox.delete(0, tk.END)  # Clear the listbox
        files_to_send = getFiles(username)  # Fetch the files from the backend
        for file in files_to_send:
            file_listbox.insert(tk.END, file[0])  # Assuming file[0] is the filename

    # Function to handle file selection and add it to the listbox
    def add_file():
        # Open a file dialog to choose a file
        file_path = filedialog.askopenfilename(title="Select a file to send")
        if file_path:  # If a file is selected
            AddFileTodatabase(username, file_path)
            filename = os.path.basename(file_path)
            file_listbox.insert(tk.END, filename)  # Add file name to the listbox
            print(f"File added: {filename}")  # For debugging, can be removed later

    # Function to handle sending files
    def send_files():
        nonlocal is_sending
        # This is where you would integrate file sending functionality
        startSending(username)  # Call backend function to start sending
        status_text.insert(tk.END, "Sending files...\n")  # Show that sending has started
        is_sending = True

    def update_status():
        try:
            log_message = Messages()  # Call the Messages function to get the status
            if log_message:  # If there's a new message
                status_text.insert(tk.END, log_message + "\n")  # Insert log message into status text widget
                status_text.yview('end')  # Scroll to the end of the text widget

            # Call update_status again after 100ms (or any interval you prefer)
            if window.winfo_exists():
                window.after(100, update_status)
        except Exception as e:
            print("Error in update_status: ",e)
    
    def go_back_to_sender_receiver():
        nonlocal is_sending
        if(is_sending):
            stopSending()
        open_sender_receiver_window(username,window)

    # Create frames for layout
    frame1 = tk.Frame(window)
    frame1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

    frame2 = tk.Frame(window)
    frame2.grid(row=0, column=1, padx=20, pady=25, sticky="nsew")

    # Configure column weights to make the frames expand properly
    window.grid_columnconfigure(0, weight=3)
    window.grid_columnconfigure(1, weight=1)
    
    # Frame 1 (First column)
    # Add File button
    add_file_button = tk.Button(frame1, text="Add File", command=add_file)
    add_file_button.pack(pady=10)

    # Listbox for displaying files available to send
    available_files_label = tk.Label(frame1, text="Files to Send", font=("Arial", 12))
    available_files_label.pack(pady=5)

    file_listbox = tk.Listbox(frame1, height=15, width=40)
    file_listbox.pack(pady=5)

    # Send button (at the bottom of the first column)
    send_button = tk.Button(frame1, text="Send Files", command=send_files)
    send_button.pack(pady=5)

    # Frame 2 (Second column) - for displaying the sending status
    status_label = tk.Label(frame2, text="Sending Status", font=("Arial", 12))
    status_label.pack(pady=5)

    status_text = tk.Text(frame2, height=15, width=30)
    status_text.pack(pady=5)

    go_back_to_sender_receiver_button = tk.Button(frame2, text="Go Back", command=lambda: go_back_to_sender_receiver())
    go_back_to_sender_receiver_button.pack(pady=5)

    if(window.winfo_exists()):
        window.after(100, update_status)  # Start checking for log messages every 100ms

    # Function to populate the listbox with current files
    

    # Populate the listbox with current files
    populate_files()

    # Start the GUI main loop
    window.mainloop()
    

def open_main_window():
    root = tk.Tk()
    root.title("LanIIT")
    root.geometry("300x200")

    tk.Label(root, text="Welcome to LanIIT a File Sharing App").pack(pady=10)
    tk.Button(root, text="Login", command=lambda: open_login_window(root)).pack(pady=5)
    tk.Button(root, text="Register", command=lambda: open_registration_window(root)).pack(pady=5)

    root.mainloop()
