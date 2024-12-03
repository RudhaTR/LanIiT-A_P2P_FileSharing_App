import tkinter as tk
from tkinter import messagebox, filedialog
from controller import handle_login, handle_registration, handle_mode_selection, getFiles,AddFileTodatabase,startSending,Messages,stopSending,getBroadcastedFiles,displayReceivedFiles,startReceiver
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
        open_receive_window(username, window)
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



def open_receive_window(username, root):
    # Destroy previous root window
    root.destroy()

    # Create the new receive window
    window = tk.Tk()
    window.title("Receive Window")
    window.geometry("900x600")

    # Variable to store the destination folder path
    destination_folder = tk.StringVar()
    destination_folder.set("No folder selected")

    finalFiles = {}
    finalSelected = []

    # Mock function to get broadcasted files (replace with actual backend)

    # Function to update the broadcasted files list
    def populate_broadcasted_files():
        broadcasted_listbox.delete(0, tk.END)  # Clear the listbox
        broadcasted_listbox.insert(tk.END, "Fetching files...")  # Placeholder text while fetching
        broadcasted_listbox.update_idletasks()  # Update the listbox immediately
        files = getBroadcastedFiles() # Fetch the files from the backend
        print("received files: ",files)

        nonlocal finalFiles 
        finalFiles = displayReceivedFiles(files)
        broadcasted_listbox.delete(0, tk.END)  # Clear the listbox again
        for file in finalFiles.values():
            broadcasted_listbox.insert(tk.END, file[0])

    # Function to select the destination folder
    def choose_destination_folder():
        folder_selected = filedialog.askdirectory(title="Select Destination Folder")
        if folder_selected:
            destination_folder.set(folder_selected)

    # Function to select a file from the broadcasted files
    def add_to_selected():
        try:
            selected_index = broadcasted_listbox.curselection()
            if not selected_index:
                messagebox.showinfo("Info", "Please select a file to add.")
                return

            selected_file = broadcasted_listbox.get(selected_index)
           
            # Add the file to the selected listbox if not already added
            if selected_file not in selected_files_listbox.get(0, tk.END):
                selected_files_listbox.insert(tk.END, selected_file)
                for i in selected_index:
                    finalSelected.append(i)
            else:
                messagebox.showinfo("Info", "File already selected.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Function to remove a file from the selected files list
    def remove_from_selected():
        try:
            selected_index = selected_files_listbox.curselection()
            if not selected_index:
                messagebox.showinfo("Info", "Please select a file to remove.")
                return

            selected_files_listbox.delete(selected_index)
            for i in selected_index:
                finalSelected.remove(i)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # Function to start receiving selected files
    def receive_files():
        try:
            selected_files = [finalFiles[i] for i in finalSelected]
            folder = destination_folder.get()

            if folder == "No folder selected":
                messagebox.showinfo("Info", "Please select a destination folder.")
                return

            if not selected_files:
                messagebox.showinfo("Info", "No files selected to receive.")
                return

            startReceiver(selected_files, folder)  # Call the backend function to start receiving files
        except Exception as e:
            messagebox.showinfo("Error occured please contact the developer")
            print("Error", f"An error occurred: {e}")

    # Create the layout frames
    frame_top = tk.Frame(window)
    frame_top.pack(fill="x", padx=10, pady=10)

    frame1 = tk.Frame(window)
    frame1.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    frame2 = tk.Frame(window)
    frame2.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    frame3 = tk.Frame(window)
    frame3.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    # Configure column weights for resizing
    window.grid_columnconfigure(0, weight=3)
    window.grid_columnconfigure(1, weight=2)
    window.grid_columnconfigure(2, weight=2)

    # Top Section: Destination Folder
    tk.Label(frame_top, text="Destination Folder:", font=("Arial", 12)).pack(side="left", padx=5)
    destination_label = tk.Label(frame_top, textvariable=destination_folder, font=("Arial", 10), fg="blue")
    destination_label.pack(side="left", padx=5, fill="x", expand=True)
    choose_folder_button = tk.Button(frame_top, text="Choose Folder", command=choose_destination_folder)
    choose_folder_button.pack(side="right", padx=5)

    # First Column: Broadcasted Files
    tk.Label(frame1, text="Broadcasted Files", font=("Arial", 12)).pack(pady=5)
    broadcasted_listbox = tk.Listbox(frame1, height=20, width=30)
    broadcasted_listbox.pack(pady=5, fill="y")
    refresh_button = tk.Button(frame1, text="Refresh", command=populate_broadcasted_files)
    refresh_button.pack(pady=5)

    # Second Column: Selected Files
    tk.Label(frame2, text="Selected Files", font=("Arial", 12)).pack(pady=5)
    selected_files_listbox = tk.Listbox(frame2, height=20, width=30)
    selected_files_listbox.pack(pady=5, fill="y")
    add_button = tk.Button(frame2, text="Add to Selected", command=add_to_selected)
    add_button.pack(pady=5)
    remove_button = tk.Button(frame2, text="Remove from Selected", command=remove_from_selected)
    remove_button.pack(pady=5)

    # Third Column: Status
    tk.Label(frame3, text="Download Status", font=("Arial", 12)).pack(pady=5)
    status_text = tk.Text(frame3, height=20, width=40)
    status_text.pack(pady=5, fill="y")
    receive_button = tk.Button(frame3, text="Receive Files", command=receive_files)
    receive_button.pack(pady=5)

    # Populate the broadcasted files list initially
    populate_broadcasted_files()

    # Start the Tkinter event loop
    window.mainloop()

    

def open_main_window():
    root = tk.Tk()
    root.title("LanIIT")
    root.geometry("300x200")

    tk.Label(root, text="Welcome to LanIIT a File Sharing App").pack(pady=10)
    tk.Button(root, text="Login", command=lambda: open_login_window(root)).pack(pady=5)
    tk.Button(root, text="Register", command=lambda: open_registration_window(root)).pack(pady=5)

    root.mainloop()
