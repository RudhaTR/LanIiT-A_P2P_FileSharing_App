import tkinter as tk
from tkinter import messagebox
from controller import handle_login, handle_registration, handle_mode_selection


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
    def select_sender():
        handle_mode_selection(username, "sender")

    def select_receiver():
        handle_mode_selection(username, "receiver")
    root.destroy()
    window = tk.Tk()
    window.title("Select Mode")
    window.geometry("300x200")

    tk.Label(window, text=f"Welcome {username}!").pack(pady=10)
    tk.Button(window, text="Sender", command=select_sender).pack(pady=5)
    tk.Button(window, text="Receiver", command=select_receiver).pack(pady=5)

    window.mainloop()

def open_main_window():
    root = tk.Tk()
    root.title("LanIIT")
    root.geometry("300x200")

    tk.Label(root, text="Welcome to LanIIT a File Sharing App").pack(pady=10)
    tk.Button(root, text="Login", command=lambda: open_login_window(root)).pack(pady=5)
    tk.Button(root, text="Register", command=lambda: open_registration_window(root)).pack(pady=5)

    root.mainloop()
