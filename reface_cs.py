import time
import rtmidi
import typer
import os,pickle

app = typer.Typer()
midiout = rtmidi.MidiOut()
midiin = rtmidi.MidiIn()

waiting = 1
data_buffer = []
db = []
FILENAME = "db_reface_cs"

cc_by_byte = [ # cc channels for each byte received in sysex
    78,
    77,
    76,
    20,
    80,
    81,
    82,
    74,
    71,
    83,
    73,
    75,
    79,
    72,
    17,
    18,
    19,
]

def initData():
    db = [None]*100
    return db

def storeData():
    global db
    # database

    # Its important to use binary mode
    dbfile = open(FILENAME, 'wb')

    # source, destination
    pickle.dump(db, dbfile)
    dbfile.close()

def loadData():
    global db
        # for reading also binary mode is important
    dbfile = open(FILENAME, 'rb')
    db = list(pickle.load(dbfile))
    dbfile.close()

def callback(message, data):
    global waiting
    global data_buffer

    # print(message)
    if len(message[0])==35:
        print(len(message[0]))
        start=13
        data_buffer = message[0][start:start+17]
        data_buffer[0] = data_buffer[0]*26
        data_buffer[4] = data_buffer[4]*26
        data_buffer[14] = data_buffer[14]*26
        for i in data_buffer:
            print(hex(i))
        print("__________________")
        waiting = 0
    print("leaving callback")

def init():
    global db
    available_ports = midiout.get_ports()
    for index, value in enumerate(available_ports):
        if not value.find("reface CS"):
            midiout.open_port(index)
            midiin.open_port(index)
    midiin.set_callback(callback)
    midiin.ignore_types(sysex=False)
    if not os.path.isfile(FILENAME):
        storeData(initData())
    loadData()

def dump_request():
    cs_dump_req=[0xF0, 0x43, 0x20, 0x7F, 0x1C, 0x03, 0x0E, 0x0F, 0x00, 0xF7] # from web search
    midiout.send_message(cs_dump_req)

@app.command()
def main(command: str = typer.Argument(default = "play"), mem: int = typer.Argument(default = 0)):
    global waiting
    global data_buffer
    global db
    init()
    if command == "rec":
        print("rec")
        dump_request()
        waiting = 1
        while(waiting==1):
            pass
        print("out of loop")
    elif command == "play":
        print("play")
    elif command == "int":
        while(1):
             print('r or p:')
             command = input()
             if command == "r":
                dump_request()
                waiting = 1
                while(waiting==1):
                    pass
                print("Bank #:")
                bank = int(input())
                print(db)
                db[bank]=data_buffer
                storeData()
             elif command == 'p':
                 print("Bank #:")
                 bank=int(input())
                 data_buffer=db[bank]
                 for cc, value in zip(cc_by_byte,data_buffer):
                    midiout.send_message([0xB0,cc,value])
                    print("cc="+str(cc)+"  value="+str(value))
             elif command == "q":
                 exit

if __name__ == "__main__":
    typer.run(main)




