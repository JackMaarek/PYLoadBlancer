import socket
from threading import Lock, Thread, Event
from time import time, ctime, sleep

HBPORT = 65438
CHECKIFALIVE = 30

class BeatDict:
    "Manage heartbeat dictionary"

    def __init__(self):
        self.beatDict = {}
        if __debug__:
            self.beatDict['127.0.0.1'] = time()
        self.dictLock = Lock()

    def __repr__(self):
        list = ''
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            list = "%sIP address: %s - Last time: %s\n" % (
                list, key, ctime(self.beatDict[key]))
        self.dictLock.release()
        return list

    def update(self, entry):
        "Create or update a dictionary entry"
        self.dictLock.acquire()
        self.beatDict[entry] = time()
        self.dictLock.release()

    def extractSilent(self, howPast):
        "Returns a list of entries older than howPast"
        silent = []
        when = time() - howPast
        self.dictLock.acquire()
        for key in self.beatDict.keys():
            if self.beatDict[key] < when:
                silent.append(key)
        self.dictLock.release()
        return silent


class BeatRec(Thread):
    "Receive UDP packets, log them in heartbeat dictionary"

    def __init__(self, goOnEvent, updateDictFunc, port):
        Thread.__init__(self)
        self.goOnEvent = goOnEvent
        self.updateDictFunc = updateDictFunc
        self.port = port
        self.recSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recSocket.bind(('', port))

    def __repr__(self):
        return "Heartbeat Server on port: %d\n" % self.port

    def run(self):
        while self.goOnEvent.isSet():
            if __debug__:
                print("Waiting to receive...")
            data, addr = self.recSocket.recvfrom(6)
            if __debug__:
                print("Received packet from " + repr(addr))
            self.updateDictFunc(addr[0])

def main():
    "Listen to the heartbeats and detect inactive clients"
    global HBPORT, CHECKIFALIVE

    beatRecGoOnEvent = Event()
    beatRecGoOnEvent.set()
    beatDictObject = BeatDict()
    beatRecThread = BeatRec(beatRecGoOnEvent, beatDictObject.update, HBPORT)
    if __debug__:
        print(beatRecThread)
    beatRecThread.start()
    print("PyHeartBeat server listening on port %d" % HBPORT)
    print("\n*** Press Ctrl-C to stop ***\n")
    while 1:
        try:
            if __debug__:
                print("Beat Dictionary")
                print(repr(beatDictObject))
            silent = beatDictObject.extractSilent(CHECKIFALIVE)
            if silent:
                print("Silent clients")
                print(repr(silent))
            sleep(CHECKIFALIVE)
        except KeyboardInterrupt:
            print("Exiting.")
            beatRecGoOnEvent.clear()
            beatRecThread.join()