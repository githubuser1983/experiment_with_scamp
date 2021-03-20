from scamp import *
from pynput import mouse

from scamp import Session, Ensemble

def construct_ensemble():
    global piano_clef,piano_bass, flute, strings, session
    ensemble = Ensemble(default_soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2")

    #ensemble.print_default_soundfont_presets()

    piano_clef = ensemble.new_part("harp")
    piano_bass = ensemble.new_part("harp")
    return [piano_clef,piano_bass]
    #strings = ensemble.new_part("strings", (0, 40))




def aT(u,a):
    if u in [1,5,7,11]:
        return lambda x : (u*x+a)%12

def mul(U,V):
    u,a = U
    x,y = V
    return ((u*x)%12,(u*y+a)%12)

def iterMul(x,k):
    if k == 1:
        return x
    else:
        return mul(iterMul(x,k-1),x)

def orderMul(x):
    y = x
    o = 1
    while y!=(1,0):
        o+=1
        y = mul(y,x)
    return o
    


def on_move(x, y):
    global currentCounter
    print('Pointer moved to {0}'.format(
        (x, y)))
    currentCounter += y-x

def on_click(x, y, button, pressed):
    print('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    
def on_scroll(x, y, dx, dy):
    global currentCounter, startPitch, oneOctave,twoLoops, instrument
    print('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))
    if dy>=0:
        currentCounter += 1
    else:
        currentCounter -= 1

# Collect events until released
#with mouse.Listener(
#        on_move=on_move,
#        on_click=on_click,
#        on_scroll=on_scroll) as listener:
#    listener.join()

# ...or, in a non-blocking fashion:
listener = mouse.Listener(on_move=on_move,on_click=on_click,on_scroll=on_scroll)

    
currentCounter = 0
oneOctave = list(range(60,72))
bassOctave = list(range(60-1*12,60-0*12))
startPitchClef = 0 
startPitchBass = 1
affineGroup = [aT(u,a) for u in [1,5,7,11] for a in range(12)]  
affineGroupIndex = [(u,a) for u in [1,5,7,11] for a in range(12)]  

affineGroupByOrder = [ (orderMul(x),x) for x in affineGroupIndex]
print(affineGroupByOrder)
twoLoops = [x for o,x in affineGroupByOrder if o==2]
threeLoops = [x for o,x in affineGroupByOrder if o==3]
fourLoops = [x for o,x in affineGroupByOrder if o==4]
print(len(twoLoops))
print(len(fourLoops))
countBass = 0

#s = Session(default_soundfont_preset="path/to/soundfont.sf2")
#s = Session(default_soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2",tempo=130)
s = Session(tempo=120)

tracks = construct_ensemble()
#s.print_default_soundfont_presets()

#print(dir(s))
#s.print_available_midi_output_devices()

#drums = s.new_part("Concert Bass Drum")
instrument = s.new_part("harp")
bass = s.new_part("harp")

def play_notes_for_clef(numNotes,duration):
    global countBass, tracks, currentCounter, startPitchClef, oneOctave,twoLoops, instrument, affineGroupIndex, bass
    print("playing clef" ,oneOctave[startPitchClef]) 
    
    for k in range(numNotes):
        tracks[0].play_note(oneOctave[startPitchClef], 0.7,duration)
        #tracks[1].play_note(bassOctave[startPitch], 1, 1.0)
        startPitchClef = aT(*affineGroupIndex[currentCounter%len(affineGroupIndex)])(startPitchClef) 
    

def play_notes_for_bass(numNotes,duration):
    global countBass,tracks, currentCounterBass, startPitchBass, oneOctave,twoLoops, instrument, affineGroupIndex, bass
    print("playing bass" ,bassOctave[startPitchBass]) 
    
    #tracks[0].play_note(oneOctave[startPitch], 0.5, 0.5)
    tracks[1].play_note(bassOctave[startPitchBass], 0.7, duration)
    countBass+=1
    startPitchBass = aT(*affineGroupIndex[currentCounter%len(affineGroupIndex)])(startPitchBass)               
    
    
if __name__=="__main__":
    listener.start()
    while True:
        if countBass%8 in [0,3,6]:
            s.fork(play_notes_for_clef,(4,0.5))
            s.fork(play_notes_for_bass,(1,2.0))
        else:
            s.fork(play_notes_for_clef,(2,0.5))
            s.fork(play_notes_for_bass,(1,1.0))
        s.wait_for_children_to_finish()