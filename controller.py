from db_utils import loginUser, registerUser,retrieve_file_metadata
import sender
import receiver
import globalLogger

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

def getFiles(username):
    earlierFiles = retrieve_file_metadata(username)
    return earlierFiles

def AddFileTodatabase(username,filepath):
    sender.add_files_from_user_gui(username,filepath)

def startSending(username):
    sender.guiMain(username)

def Messages():
    try:
        message = globalLogger.receiveMessageSender()
        if message is not None:
            return message
        else:
            return None
    except Exception as e:
        print("Error in Messages: ",e)