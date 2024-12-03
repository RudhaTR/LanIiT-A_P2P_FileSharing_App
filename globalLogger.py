import queue
import threading

qSender = queue.Queue()
Senderlock = threading.Lock()

qReceiver = queue.Queue()
Receiverlock = threading.Lock()

def sendMessageSender(message):
    try:
        with Senderlock:
            qSender.put(message)
    except Exception as e:
        print("Error in sendMessageSender: ",e)

def receiveMessageSender():
    try:
        with Senderlock:
            if(not qSender.empty()):
                return qSender.get(block=False)
            return None
    except Exception as e:
        print("Error in receiveMessageSender: ",e)

def sendMessageReceiver(message):
    try:
        with Receiverlock:
            qReceiver.put(message)
    except Exception as e:
        print("Error in sendMessageReceiver: ",e)

def receiveMessageReceiver():
    try:
        with Receiverlock:
            if(not qReceiver.empty()):
                return qReceiver.get(block=False)
            return None
    except Exception as e:
        print("Error in receiveMessageReceiver: ",e)