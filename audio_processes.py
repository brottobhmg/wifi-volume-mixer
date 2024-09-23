from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume, IAudioEndpointVolume
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
#library comtypes/_post_coinit/unknwn.py commented row 386 


def set_volume(name, new_volume):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        if session.Process and session.Process.name() == name + ".exe":
            volume.SetMasterVolume(new_volume, None)

def get_process_names():
    process_names = []
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name():
            process_names.append(session.Process.name())
    return process_names

def get_volume(name):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        if session.Process and session.Process.name() == name + ".exe":
            volume_value = volume.GetMasterVolume()
            return volume_value if volume_value is not None else 0

def get_master_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume.GetMasterVolumeLevelScalar()
    return current_volume

def set_master_volume(new_volume):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    try:
        volume.SetMasterVolumeLevelScalar(new_volume, None)
    except Exception as e:
        print(f"Errore nell'impostazione del volume master: {e}")

