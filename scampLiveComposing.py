import pygame
from pygame.locals import *
import random

generalSF = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

sf = generalSF


from scamp import Session, Ensemble

def construct_ensemble(sf):
    global piano_clef,piano_bass, flute, strings, session
    ensemble = Ensemble(default_soundfont=sf)

    ensemble.print_default_soundfont_presets()

    second = ensemble.new_part("Glockenspiel")
    first = ensemble.new_part("Violin") #("violoncello")
    return [first,second,ensemble.new_part("Piano"),ensemble.new_part("Piano"),ensemble.new_part("Panflute"),ensemble.new_part("Harp"),ensemble.new_part("Violoncello"),ensemble.new_part("Acoustic Bass")]
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



pygame.init()
screen = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()

def drawRect(surface,color,xStart,yStart):
    pygame.draw.rect(surface, color, Rect(xStart,yStart,80,80),0)


def drawText(surface, text, x,y):
    textsurface = myfont.render(text, False, (255,255,255))
    surface.blit(textsurface,(x,y))

def getRect(x,y):
    k = (x//80)
    l = (y//80)
    return k+l*8

pygame.font.init() # you have to call this at the start, 
                  # if you want to use this module.
myfont = pygame.font.SysFont('Comic Sans MS', 30)
#This creates a new object on which you can call the render method.


oneOctave = list(range(60,72))
bassOctave = list(range(60-1*12,60-0*12))
startPitch = 0 
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


s = Session(tempo=120,default_soundfont=sf) #.run_as_server()

s.print_available_midi_output_devices()

tracks = construct_ensemble(sf)

for t in tracks:
    s.add_instrument(t)

piano = s.new_part("Piano")
s.add_instrument(piano)

def play_piano(pitch,volume,duration):
    global piano
    piano.play_note(pitch,volume,duration)

def callback_midi(midi):
    global s,piano
    code,pitch,volume = midi
    if volume > 0 and 144 <= code <= 159:
        s.fork(play_piano,(pitch,volume,0.5))
        #s.wait_for_children_to_finish()

s.register_midi_listener(port_number_or_device_name=1, callback_function=callback_midi)



counters =  dict(zip(range(48),48*[0]))

def updateCounterForRect(rectangleNumber,plusOne=True):
    global counters
    if plusOne:
        counters[rectangleNumber] += 1
    else:
        counters[rectangleNumber] -= 1


def digits(n,base,padto=None):
    q = n
    ret = []
    while q != 0:
        q, r = q//base,q%base # Divide by 10, see the remainder
        ret.insert(0, r) # The remainder is the first to the right digit
    if padto is None:
        return ret
    for i in range(padto-len(ret)):
        ret.insert(0,0)
    #ret.extend((padto-len(ret))*[0])    
    return ret

def repeatingNumbers(dd,D,offset=1,NStart=1,NEnd = 100):
    return [sum([n//d for d in dd])%D+offset for n in range(NStart,NEnd+1)]

def durationMingus2Music21(mingusDuration):
    if float(mingusDuration) == 0.0:
        return None
    else:
        return float(1/mingusDuration)
    
def durationMingus2MidiUtil(mingusDuration)    :
    if float(mingusDuration) == 0.0:
        return None
    else:
        return float(1/mingusDuration*4) # beats per minutes in quarternotes

def digitsReversed(n,base,padto):
    q = n
    ret = []
    while q != 0:
        q, r = q//base,q%base # Divide by 10, see the remainder
        ret.insert(0, r) # The remainder is the first to the right digit
    if padto is None:
        return ret
    for i in range(padto-len(ret)):
        ret.insert(0,0)
    #ret.extend((padto-len(ret))*[0])    
    return ret


def sumTree(n,leftToRight=True):
    if n==1:
        return []
    else:
        if leftToRight:
            return [sumTree(int(n//2),leftToRight),sumTree(n-int(n//2),leftToRight)]
        else:
            return [sumTree(n-int(n//2),leftToRight),sumTree(int(n//2),leftToRight)]


def digitsTree(n):
    if n==0:
        return []
    dd = digits(n-1,2)
    dd.reverse()
    #print(dd)
    ll = []
    oo = [dd[i] for i in range(len(dd)) if i%2==1]
    ee = [dd[i] for i in range(len(dd)) if i%2==0]
    #print(oo,ee)
    O = sum([2**(i)*oo[i] for i in range(len(oo))])
    E = sum([2**(i)*ee[i] for i in range(len(ee))])
    #print(O,E)
    return [digitsTree(O),digitsTree(E)]


def getDurationsFromTree(tree):
    # Identify leaves by their length
    if len(tree) == 0:
        return [1]
    # Take all branches, get the paths for the branch, and prepend current
    dd = []
    for t in tree:
        dd.extend([2*d for d in getDurationsFromTree(t)])
    return dd 

def getDottedDurationsFromTree(tree,dotted=True):
    if len(tree)==0:
        return [1]
    dd = []
    if (len(tree[0])==0 or len(tree[1])==0) and dotted:
        dd.extend([4/3*d for d in getDottedDurationsFromTree(tree[0],dotted)])
        dd.extend([4*d for d in getDottedDurationsFromTree(tree[1],dotted)])
    else:
        for t in tree:
            dd.extend([2*d for d in getDottedDurationsFromTree(t,dotted)])
    return dd


def generateBar(nTracks,barNumber,notelist,SYMFUNC,NFUNC,BASEFUNC):
    bars = []
    for i in range(nTracks):
        bars.append([])
        
    for tt in range(nTracks):
        barCounter = 0
        c = 1
        for bb in [barNumber]:
            K = bb[tt]
            mingusDurations = getDurationsFromTree(digitsTree(max(K,1)))
            durations = mingusDurations
            pitches = []
            volumes = []
            c = bb[tt]
            barCounter += 1
            for d in durations:
                c+= 1
                dc = digitsReversed(c,BASEFUNC,padto=NFUNC)[:NFUNC]
                pitchMod = (SYMFUNC([d+1 for d in dc]))%len(notelist)
                pitchlist = []
                if K>0:
                    pitch = notelist[pitchMod]
                else:
                    pitch = None
                pitches.append([pitch])
                volumes.append(0.50)    # todo: change this
            bar = list(zip(pitches,durations,volumes))        
            bars[tt].append(bar)    
    return(bars)

import math
SYMFUNC = lambda a : int(a[0]*a[1]*(a[0]+a[1])/int(math.gcd(a[0],a[1])**3))
NFUNC = 2
BASEFUNC = 19


import math
funcTirana = lambda a: 2*int(math.pow(a[2],2)) + 2*int(math.pow(a[3],2)) + 2*int(math.pow(a[4],2)) + 3*a[0] + 3*a[1]
funcTirana2 = lambda a: -(2*a[2]**2 + 2*a[3]**2 + 2*a[4]**2) + 3*a[0] + 3*a[1]
funcTirana3 = lambda a: (2*a[2]**2 + 2*a[3]**2 + 2*a[4]**2) + -(3*a[0] + 3*a[1])
funcTirana4 = lambda a: -(2*a[2]**2 + 2*a[3]**2 + 2*a[4]**2) + -(3*a[0] + 3*a[1])
funcABC = lambda a: int(a[0]*a[1]*(a[0]+a[1])/math.gcd(a[0],a[1])**3)
funcs = [funcTirana,funcTirana2,funcTirana3,funcTirana4]
funcKlein = lambda a : a[0]**1+a[1]**2+a[2]**1+a[3]**2
func = lambda a: sum(a) #int((a[0]**5*a[1]**1+a[0]**4*a[1]**2+a[0]**2*a[1]**4+a[0]**1*a[1]**5)/math.gcd(a[0],a[1])**6)
myfunc = func
NFUNC = 5
MFUNC = 6

listFuncs = [ 
               (funcTirana,5,6),
               (funcTirana2,5,6),
               (funcTirana3,5,6),
               (funcTirana4,5,6),
               (funcABC, 2, 19),
               (funcKlein, 4, 6),
            ]

def play_bar_for_instrument(instNr,bar):
    global tracks, counters
    if counters[instNr]<=0:
        return
    print(instNr,bar)
    for i in range(len(bar)):
        nc,duration,volume = bar[i]
        dur = 4.0/(duration)
        pitch = max(min(nc[0]+counters[16+instNr]*12,127),0) # octave at third row, counter = 0 -> 4-th octave
        if not pitch is None:
            tracks[instNr].play_note(pitch,volume, dur)



def setCounterToValue(rect,value):
    global counters
    counters[rect]= value

def main():
   global countBass,tracks,oneOctave,SYMFUNC,NFUNC,BASEFUNC, counters, listFuncs
   while True:
      nTracks = len(tracks)
      barNumbers = [counters[k]  for k in range(nTracks)]
      for tt in range(len(tracks)):
          SYMFUNC,NFUNC,BASEFUNC = listFuncs[ max(counters[8+tt],0)%len(listFuncs)]
          bars = generateBar(nTracks, barNumbers, oneOctave, SYMFUNC,NFUNC,BASEFUNC)
          for t in range(len(bars[tt])):
              if counters[tt]>0:
                  s.fork(play_bar_for_instrument,(tt,bars[tt][t]))
      for event in pygame.event.get():
            xPos,yPos = (pygame.mouse.get_pos())
            leftPressed,middlePressed,rightPressed = pygame.mouse.get_pressed()
            #print(xPos,yPos,leftPressed,rightPressed)
            rect = getRect(xPos,yPos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: 
                    updateCounterForRect(rect,True)
                if event.button == 5:
                    updateCounterForRect(rect,False)
            if leftPressed:
                val = counters[rect]//2
                setCounterToValue(rect,val)
            if middlePressed:
                setCounterToValue(rect,0)
            if rightPressed:
                val =  counters[rect]*2
                setCounterToValue(rect,val)
            #print(counters)
            if event.type == QUIT:
               #pygame.quit()
               return
               #print(event)
               #print(event.x, event.y)
               #print(event.flipped)
               #print(event.which)
               # can access properties with
               # proper notation(ex: event.y)
      for k in range(8):
          for l in range(6):
              color = ((k*5)%255,(l*5)%255,(k+l)%255)
              drawRect(screen, color,k*80,l*80)
              drawText(screen, str(counters[k+l*8]), k*80+40,l*80+40)
      pygame.display.flip()
      s.wait_for_children_to_finish()
      clock.tick()
# Execute game:
s.start_transcribing()
main()
performance = s.stop_transcribing()
score = performance.to_score()
music_xml = score.to_music_xml()
music_xml.export_to_file("my_first_music_xml.xml")
