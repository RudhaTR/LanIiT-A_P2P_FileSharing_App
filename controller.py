from db_utils import loginUser, registerUser
import sender
import receiver

def handle_login(username, password):
    if loginUser(username, password):
        return True, "Login successful!"
    else:
        return False, "Invalid username or password."

def handle_registration(username, password):
    if registerUser(username, password):
        return True, "Registration successful!"
    else:
        return False, "Registration failed. User may already exist."

def handle_mode_selection(username, mode):
    if mode == "sender":
        print(f"{username} selected Sender mode.")
        sender.main(username)  # Call sender functionality
    elif mode == "receiver":
        print(f"{username} selected Receiver mode.")
        receiver.main()  # Call receiver functionality