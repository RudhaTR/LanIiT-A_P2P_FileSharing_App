from db_utils import loginUser, registerUser,retrieve_file_metadata
import sender
import receiver
import globalLogger
import threading
import queue



def stopSending():
    currstopevent.set()

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
    global currstopevent 
    currstopevent = sender.guiMain(username)

def Messages():
    try:
        message = globalLogger.receiveMessageSender()
        if message is not None:
            return message
        else:
            return None
    except Exception as e:
        print("Error in Messages: ",e)

def getBroadcastedFiles():
    try:
        return receiver.getBroadcastedFiles()
    except Exception as e:
        print("Error in getBroadcastedFiles: ",e)

def displayReceivedFiles(peers):
    try:
        finalFiles = {}
        iterator = 0
        for peer_ip, info in peers.items():
            sender = info['username']
            for file in info['files']:
                finalFileName = file+" - "+sender
                finalFiles[iterator]=((finalFileName,peer_ip))
                iterator+=1
        return finalFiles
    except Exception as e:
        print("Error in displayReceivedFiles: ",e)

def startReceiver(selected_files,folder):
    try:
        selectedFilesToBeSent = []
        for file,peer_ip in selected_files:
            newfilename = file.rsplit(" - ",1)[0]
            selectedFilesToBeSent.append((peer_ip,newfilename))
        receiver.guiReceiver(selectedFilesToBeSent,download_folder=folder)
    except Exception as e:
        print("Error in startReceiver: ",e)