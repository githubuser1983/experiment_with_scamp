import pygame
from pygame.locals import *


from scamp import Session, Ensemble

def construct_ensemble():
    global piano_clef,piano_bass, flute, strings, session
    ensemble = Ensemble(default_soundfont="/usr/share/sounds/sf2/FluidR3_GM.sf2")

    #ensemble.print_default_soundfont_presets()

    piano_clef = ensemble.new_part("harp")
    piano_bass = ensemble.new_part("violoncello")
    return [piano_clef,piano_bass,ensemble.new_part("piano"),ensemble.new_part("piano"),ensemble.new_part("harp"),ensemble.new_part("flute")]
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


s = Session(tempo=120)

tracks = construct_ensemble()


def play_notes_for_instrument(instNr, numNotes,duration):
    global tracks, counters, startPitchBass,bassOctave, affineGroupIndex, oneOctave, startPitch, countBass
    if instNr == 1:
        octave = bassOctave
        pitch = startPitchBass
    else:
        octave = oneOctave
        pitch = startPitch
    #tracks[0].play_note(oneOctave[startPitch], 0.5, 0.5)
    countClick = counters[0]
    volume =  1-1.0/(abs(counters[1])+2)
    currentCounter  = counters[2]

    for k in range(numNotes):
        print("playing" , instNr,  octave[pitch], volume,duration)
        tracks[(countClick%len(tracks)+(countClick+instNr)%2)%len(tracks)].play_note(octave[pitch],volume, duration)
        if instNr==1: countBass+=1
        pitch = aT(*affineGroupIndex[currentCounter%len(affineGroupIndex)])(pitch)
    if instNr ==1:
        startPitchBass = pitch
    else:
        startPitch = pitch

counters =  dict(zip(range(48),48*[0]))

def updateCounterForRect(rectangleNumber,plusOne=True):
    global counters
    if plusOne:
        counters[rectangleNumber] += 1
    else:
        counters[rectangleNumber] -= 1

def main():
   global countBass
   while True:
      if countBass%8 in [0,3,6]:
            s.fork(play_notes_for_instrument,(0,4,0.5))
            s.fork(play_notes_for_instrument,(1,1,2.0))
      else:
            s.fork(play_notes_for_instrument,(0,2,0.5))
            s.fork(play_notes_for_instrument,(1,1,1.0))
      for event in pygame.event.get():
            xPos,yPos = (pygame.mouse.get_pos())
            leftPressed,middlePressed,rightPressed = pygame.mouse.get_pressed()
            print(xPos,yPos,leftPressed,rightPressed)
            rect = getRect(xPos,yPos)
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
main()
