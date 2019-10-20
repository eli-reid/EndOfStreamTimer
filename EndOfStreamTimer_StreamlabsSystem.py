#---------------------------------------
#   Import Libraries
#---------------------------------------
import sys
import clr
import time
import os
import json
import threading
from datetime import datetime, time as datetime_time, timedelta
import codecs

clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

debuggingMode = True
ScriptName = "End Of Stream Timer"
Website = "https://www.Eliried.com"
Description = "When Will It end"
Creator = "Eli Reid"
Version = "9.0"

SettingsFile = "Settings.json"
Path = os.path.dirname(__file__)
Settings = {}
eventDATA={}
TimeFile = "end_time.txt"
TimeDir = "overlay\\"
TimerActive = False
timestampOfflineSince = 0 
TmpTime=""
OldTime=""

def Init():
    global TimeFile, Settings, SettingsFile, Path, TmpTime, OldTime, waiting
    try:# create subfolder if it doesnt exist
        if not os.path.exists(os.path.dirname(os.path.join(Path, TimeDir))):
            os.makedirs(os.path.dirname(os.path.join(Path,TimeDir)))
        # create overlay files if they dont exist
        if not os.path.exists(os.path.join(Path,TimeDir + TimeFile)):
            with open(os.path.join(Path, TimeDir + TimeFile), "w+") as f:
                f.write(" ")
    except:
         Parent.SendTwitchMessage(("Failed to make timer file!!") [:490])

    try:
        with codecs.open(os.path.join(Path, SettingsFile), encoding='utf-8-sig', mode='r') as file:
            Settings = json.load(file, encoding='utf-8-sig') 
        TmpTime=Settings["EndTime"]
        OldTime=Settings["EndTime"]
    except:
        Parent.SendTwitchMessage(("Settings failed to load") [:490])
    return 

def Execute(data):
    global Settings,TimerActive
    try:
        if data.IsChatMessage():
            if data.GetParamCount() >= 2 and data.GetParam(0).lower() == "!timer" and data.IsWhisper():
                #check commands and permissions P_[command]=command permission
                if data.GetParam(1).lower() == "start" and Parent.HasPermission(data.User, Settings["P_start"], ""):
                    if TimerActive: #check if timer is running
                        Parent.SendTwitchWhisper(data.User,"Timer is active!") 
                    else: #if timer off start timer
                        Start()
                        Parent.SendTwitchWhisper(data.User,"Timer is started!")
                
                elif data.GetParam(1).lower() == "stop" and Parent.HasPermission(data.User, Settings["P_stop"], ""): 
                    Stop()
                    Parent.SendTwitchWhisper(data.User, "Timer is stopped!")
                elif data.GetParam(1).lower() == "addmin" and Parent.HasPermission(data.User, Settings["P_addmin"], ""): 
                    if data.GetParam(2):
                        AddMin(int(data.GetParam(2)))
                        Parent.SendTwitchWhisper(data.User, "Added " + data.GetParam(2) + " Minutes!")
                    else:
                        AddMin()
                        Parent.SendTwitchWhisper(data.User, "Added 15 Minutes!")

                elif data.GetParam(1).lower() == "addhr" and Parent.HasPermission(data.User, Settings["P_addhr"], ""):   
                   if data.GetParam(2):
                        AddHour(int(data.GetParam(2)))
                        Parent.SendTwitchWhisper(data.User, "Added " + data.GetParam(2) + " Hour!")
                   else:
                        AddHour()
                        Parent.SendTwitchWhisper(data.User, "Added 1 Hour!")
                
                elif data.GetParam(1).lower() == "gettime" and Parent.HasPermission(data.User, Settings["P_gettime"], ""): 
                    Parent.SendTwitchWhisper(data.User,"Timer is set to: " + Settings["EndTime"])
                
                elif data.GetParam(1).lower() == "timeleft" and Parent.HasPermission(data.User, Settings["P_timeleft"], ""): 
                    Parent.SendTwitchWhisper(data.User,"Time to end: " + str(TimeDiff()))
               
                elif data.GetParam(1).lower() == "settime" and Parent.HasPermission(data.User, Settings["P_settime"], ""):
                    setTime(data.GetParam(2))
                    Parent.SendTwitchWhisper(data.User,"Time set to: " + Settings["EndTime"])
                
                elif data.GetParam(1).lower() == "setendmsg" and Parent.HasPermission(data.User, Settings["P_setendmsg"], ""):
                    setEndMsg(data.Message.replace(data.GetParam(0) + " " + data.GetParam(1),""))
                    Parent.SendTwitchWhisper(data.User,"New end message set to: " + Settings["EndMsg"])
               
                elif data.GetParam(1).lower() == "setmsg" and Parent.HasPermission(data.User, Settings["P_setmsg"], ""):
                    setDisplayMsg(data.Message.replace(data.GetParam(0) + " " + data.GetParam(1),""))
                    Parent.SendTwitchWhisper(data.User,"New message set to: " + Settings["DisplayMsg"])
                
                elif data.GetParam(1).lower() == "help" and Parent.HasPermission(data.User, Settings["P_setmsg"], ""):
                    Parent.SendTwitchWhisper(data.User,"\"!timer start\" - Starts timer ******* \"!timer stop\" - Stops timer ******* \"!timer gettime\" - Gets time to end timer  ******* \"!timer settime\" - sets the end time format(\'00:00:00\' 24hr) *******  ")
    except ValueError,e:
        Parent.SendTwitchWhisper(data.User,("Command Failed: Please check formats! ERR: \" " + str(e)) + "\"" [:490])
    return

def WriteTimerFile(msg):
    global TimeFile, TimeDir
    try:
        with codecs.open(os.path.join(Path, TimeDir + TimeFile), encoding='utf-8-sig', mode="w+") as file:
                    file.write(msg)
    except :
        Debug("err") 
    return 

def StartTimer():
    global TimerActive, Settings, TmpTime, Path 
    TimerActive=True
    while TimerActive == True:
        WriteTimerFile(Settings["DisplayMsg"] + " " + str(TimeDiff(TmpTime)))
        if TimeDiff(TmpTime).total_seconds() == int(Settings["ChatSoonSlider"]) * 60 and Settings["ChatSoonEnabled"]:
                 Parent.SendTwitchMessage(str(Settings["ChatSoonMsg"]).replace("$min", str(int(Settings["ChatSoonSlider"]))) [:490])
        if TimeDiff(TmpTime).total_seconds() == 0:
            WriteTimerFile(Settings["EndMsg"])
            if Settings["ChatEndEnabled"]:
                Parent.SendTwitchMessage((Settings["ChatEndMsg"]) [:490])
            TimerActive=False
            if Settings["SoundEnabled"]:
                PlaySound()
            TmpTime=Settings["EndTime"]
            break
        time.sleep(1)

def Start():
    global TimerActive, Settings ,  TmpTime
    EventData("EVENT_START") 
    Startthread()
    return

def Startthread():
    global TimerActive, Settings ,  TmpTime

    if not TimerActive:
        TimerThread=threading.Thread(target=StartTimer, args=())
        TimerThread.start()
    return

def Stop():
    global TimerActive, TmpTime, Settings
    EventData("EVENT_STOP")
    TimerActive=False
    TmpTime = Settings["EndTime"]
    WriteTimerFile("Timer Stopped!")
    return 

def AddMin(min = 15):
    global TmpTime,TimerActive
    try:
        if TimerActive:
            tmp=TmpTime.split(":")
        else:
            tmp=str(datetime.now().time().strftime('%H:%M:%S')).split(":")
        tmp[1] = int(tmp[1]) + min
        if int(tmp[1]) > 59:
            hr=int(tmp[1])/60
            tmp[0]=int(tmp[0]) + hr
            if int(tmp[0]) >= 24:
                tmp[0] = 0
            tmp[1] = int(tmp[1]) - (hr * 60)
        TmpTime = str(tmp[0]) + ":" + str(tmp[1]) + ":" + str(tmp[2])
        EventData("EVENT_ADD_MIN")
        Startthread()
        return True
    except:
        return False

def AddHour(hr = 1):
    global TmpTime,TimerActive
    try:
        if TimerActive:
            tmp=TmpTime.split(":")
        else:
            tmp=str(datetime.now().time().strftime('%H:%M:%S')).split(":")
        tmp[0] = int(tmp[0]) + hr
        if int(tmp[0]) >= 24:
            tmp[0] = int(tmp[0]) - 24
        TmpTime = str(tmp[0]) + ":" + str(tmp[1]) + ":" + str(tmp[2])
        EventData("EVENT_ADD_HOUR") 
        Startthread()
        return True
    except:
        return False

def setTime(stime):
    global Settings
    assert datetime.strptime(stime,"%H:%M:%S"), "Please format time 00:00:00"
    Settings["EndTime"] = stime
    Save()
    return      

def setEndMsg(msg):
    global Settings

    Settings["EndMsg"] = msg
    Save()
    return
   
def setDisplayMsg(msg):
    global Settings
    Settings["DisplayMsg"] = msg
    Debug(msg)
    Save()
    return

def Tick():
    global timestampOfflineSince,Settings
    if Parent.IsLive():
        if Settings["AutoStart"] and not TimerActive and (( time.time() - timestampOfflineSince > 60) or  timestampOfflineSince == 0):
            Start()
        timestampOfflineSince = time.time()
    return  

def Unload():
    Stop()
    return

def Debug(message):
    if debuggingMode:
        Parent.Log("End of streamless",message)
    return

def ReloadSettings(jsonData):
    global Settings, TmpTime, OldTime
    Settings=json.loads(jsonData, encoding='utf-8-sig')
    if OldTime != Settings["EndTime"] and TmpTime == OldTime:
        TmpTime = Settings["EndTime"]
        OldTime = Settings["EndTime"]
    EventData("EVENT_UPDATE") 
    return

def TimeDiff(EndTime):
    Start = datetime.strptime(str(datetime.now().time().strftime('%H:%M:%S')),'%H:%M:%S')
    End = datetime.strptime(EndTime,'%H:%M:%S')
    if Start > End:
        End += timedelta(1) 
        assert End > Start       
    return End - Start
   
def Open():   
    global Path, TimeDir
    os.startfile(os.path.join(Path,TimeDir))
    return

def OpenSounds():   
    global Path
    os.startfile(os.path.join(Path,"Sounds"))
    return

def Save():
    global SettingsFile
    with codecs.open(os.path.join(Path, SettingsFile), encoding='utf-8-sig', mode='w+') as file:
        json.dump(Settings, file)
    with codecs.open(os.path.join(Path, SettingsFile), encoding='utf-8-sig', mode='r') as file:
        ReloadSettings(json.dumps(json.load(file, encoding='utf-8-sig'))) 
    return

def PlaySound():
    global Path, Settings
    Parent.PlaySound(os.path.join( Path,"Sounds\\" + Settings["SoundFile"]),float(Settings["SoundVolume"])/100)

def EventData(event):
    global Settings,TmpTime, eventDATA
    t=TmpTime.split(":")
    eventDATA["Hr"] = t[0]
    eventDATA["Min"] = t[1]
    eventDATA["DisplayMsg"] = Settings["DisplayMsg"]
    eventDATA["EndMsg"] = Settings["EndMsg"]
    eventDATA["TextSize"] = Settings["TextSizeSlider"]
    eventDATA["Style"] = Settings["Style"]
    eventDATA["RainbowSlider"] = Settings["RainbowSlider"]
    eventDATA["Colors"] = Settings["Colors"]
    eventDATA["Color1"] = Settings["Color1"]
    eventDATA["Color2"] = Settings["Color2"]
    eventDATA["Color3"] = Settings["Color3"]
    eventDATA["Color4"] = Settings["Color4"]
    eventDATA["Color5"] = Settings["Color5"]
    eventDATA["Color6"] = Settings["Color6"]
    eventDATA["Color7"] = Settings["Color7"]
    data=json.dumps(eventDATA)
    Parent.BroadcastWsEvent(event,data)
    return



