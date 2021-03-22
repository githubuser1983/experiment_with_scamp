import pygame
from pygame.locals import *
import random


from scamp import Session, Ensemble

def construct_ensemble():
    global piano_clef,piano_bass, flute, strings, session
    ensemble = Ensemble(default_soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2")

    #ensemble.print_default_soundfont_presets()

    second = ensemble.new_part("Concert Bass Drum")
    first = ensemble.new_part("guitar") #("violoncello")
    return [first,second,ensemble.new_part("piano"),ensemble.new_part("piano"),ensemble.new_part("flute"),ensemble.new_part("harp")]
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


s = Session(tempo=60,default_soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2")

s.print_available_midi_output_devices()

tracks = construct_ensemble()

for t in tracks:
    s.add_instrument(t)


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
            mingusDurations = getDurationsFromTree(sumTree(max(K,1),True))
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
                volumes.append(0.5)    # todo: change this
            bar = list(zip(pitches,durations,volumes))        
            bars[tt].append(bar)    
    return(bars)

import math
SYMFUNC = lambda a : int(a[0]*a[1]*(a[0]+a[1])/int(math.gcd(a[0],a[1])**3))
NFUNC = 2
BASEFUNC = 19


def play_bar_for_instrument(instNr,bar):
    global tracks, counters
    if counters[instNr]<=0:
        return
    print(instNr,bar)
    for i in range(len(bar)):
        nc,duration,volume = bar[i]
        dur = 4.0/(duration)
        pitch = nc[0]
        if not pitch is None:
            tracks[instNr].play_note(pitch,volume, dur)



def main():
   global countBass,tracks,oneOctave,SYMFUNC,NFUNC,BASEFUNC, counters
   while True:
      nTracks = len(tracks)
      barNumbers = [counters[k]  for k in range(nTracks)]
      bars = generateBar(len(tracks), barNumbers, oneOctave, SYMFUNC,NFUNC,BASEFUNC)
      for tt in range(len(tracks)):
          for t in range(len(bars[tt])):
              if counters[tt]>0:
                  s.fork(play_bar_for_instrument,(tt,bars[tt][t]))
      for event in pygame.event.get():
            xPos,yPos = (pygame.mouse.get_pos())
            leftPressed,middlePressed,rightPressed = pygame.mouse.get_pressed()
            print(xPos,yPos,leftPressed,rightPressed)
            rect = getRect(xPos,yPos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: 
                    updateCounterForRect(rect,True)
                if event.button == 5:
                    updateCounterForRect(rect,False)
            if leftPressed:
                updateCounterForRect(rect,True)
            if rightPressed:
                updateCounterForRect(rect,False)
            #print(counters)
            if event.type == QUIT:
               pygame.quit()
               return
            elif event.type == pygame.MOUSEWHEEL:
               print(event)
               print(event.x, event.y)
               print(event.flipped)
               print(event.which)
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
