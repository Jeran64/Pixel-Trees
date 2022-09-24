from PIL import Image, ImageDraw, ImageStat
import random
import math
import time
print "hello"

pixelsPerFrame=5000#make it equivilant to either the width or the height for coolness.
width=1920
height=1080
colorDepth=44 #should be a pre calculated amount that is divisible by an even number of colors.
maxAttempts=64 #howmany times a pixel should be checked
maxFailures=80# how many pixels should be attempted to be placed before the overal tolerance is increased .
maxTolerance=1#how similar in color the pixel has to be to its neighbors average


loadImageFlag=1
randomSeedsFlag=1
autoColorFlag=0

seedCount=10

pixelsPlaced=0;
listOfColors=[]
unusedNeighbors=[]
seeds=[(255,255,255,255),(0,0,0,255)]
seedLocations=[]
directions=[(-1,-1),(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1)]

#perhaps add colors to the RGB color space by counting the total pixels in the image, rather than estimating.

canvas = Image.new("RGBA",(width+2,height+2),0)
pixels = canvas.load()
width+=2 #now that we have accounted for the buffer spacing, amke sur ethe actual values reflect this alteration.
height+=2


print time.time()
if(loadImageFlag==0):
    if(autoColorFlag==1):
        colorDepth=int(math.pow(width*height,1.0/3.0))
        print "calculated color depth of: "+str(colorDepth)
    for red in range(0,colorDepth):
        print "Building Color List... "+str(float(red)/colorDepth)
        for green in range(0,colorDepth):
            for blue in range(0,colorDepth):
                listOfColors.append((int((float(red)/colorDepth)*255),int((float(green)/colorDepth)*255),int((float(blue)/colorDepth)*255),255)) #add the colors in tuples. divide each value to normalize the values to runt he full gamut of the color.
else:
    print "Loading Image."
    inputImage=Image.open("input.jpg")
    width=inputImage.size[0]+2
    height=inputImage.size[1]+2
    canvas = Image.new("RGBA",(width,height),0)
    pixels = canvas.load()
    listOfColors=list(inputImage.getdata())
    print "using "+str(len(listOfColors))+" pixels. size: "+str(width)+","+str(height)

def CheckNeighborhood(xPos,yPos):
    for offset in directions:
        checkingPixel=pixels[xPos+offset[0],yPos+offset[1]]
        if(checkingPixel[3]==0):##if the opacity of the pixel is completly transparent, it means it has not been used yet
            if(unusedNeighbors.count((xPos+offset[0],yPos+offset[1]))==0): #check to see if the neighbor is not on the list, and is within the desired pixel boundries.
                if(xPos+offset[0]>0):
                    if(yPos+offset[1]>0):
                        if(xPos+offset[0]<width-1):
                            if(yPos+offset[1]<height-1):
                                unusedNeighbors.append((xPos+offset[0],yPos+offset[1]))#add the calculated coordinates to the list.
def AverageNeighborhood(xPos, yPos):
    opaqueCount=0
    sumRGB=(0,0,0)
    for a in directions:
        currentPixel=pixels[xPos+a[0],yPos+a[1]]
        if(currentPixel[3]==255):##returns true, and adds one when the pixel in question is OPAQUE. ignore transparent pixels.
            opaqueCount+=1
            sumRGB=(currentPixel[0]+sumRGB[0],currentPixel[1]+sumRGB[1],currentPixel[2]+sumRGB[2])##create a tuple with the total colors
    return (sumRGB[0]/opaqueCount,sumRGB[1]/opaqueCount,sumRGB[2]/opaqueCount)##make the tuple divided

def ColorDistance(colorA, colorB):
    return math.sqrt(math.pow(colorA[0]-colorB[0],2)+math.pow(colorA[1]-colorB[1],2)+math.pow(colorA[2]-colorB[2],2))

#double check the possibilities.
if(len(listOfColors)>((width)*(height))):
    print "color count higher than the canvas size. exiting."+str(len(listOfColors))+"/"+str((width-2)*(height-2))
    exit()

print "growing "+str(len(listOfColors))+" different colors.\n Estimated frame output: "+str(float(len(listOfColors))/pixelsPerFrame)




print "Planting Seeds."
if(randomSeedsFlag==0):
    for a in range(0,len(seeds)):
        initialX=random.randint(2,width-3)
        initialY=random.randint(2,height-3)
        pixels[initialX,initialY]=seeds[a]
        print "planting seed: "+str(seeds[a])
        CheckNeighborhood(initialX,initialY)
else:
    for a in range(0,seedCount):
        initialX=random.randint(2,width-3)
        initialY=random.randint(2,height-3)
        seedColor=listOfColors[random.randint(0,len(listOfColors))]
        listOfColors.remove(seedColor)
        pixels[initialX,initialY]=seedColor
        print "planting seed: "+str(seedColor)
        CheckNeighborhood(initialX,initialY)
print "germinating..."
print "Watering seeds...."

while len(listOfColors)>0:
    tryCount=0
    while tryCount<maxFailures:
        #print str(len(listOfColors))+"/"+str(len(unusedNeighbors))
        if(len(listOfColors)>1):
            currentColor=listOfColors[random.randint(0,len(listOfColors)-1)]
        else:
            currentColor=listOfColors[0]
        attempt=0
        while attempt<maxAttempts:

            attempt+=1
            if(len(unusedNeighbors)>1): 
                currentNeighbor=unusedNeighbors[random.randint(0,len(unusedNeighbors)-1)]
            else:
                currentNeighbor=unusedNeighbors[0]
            variance=ColorDistance(currentColor,AverageNeighborhood(currentNeighbor[0],currentNeighbor[1]))
            if(variance < maxTolerance):
                pixels[currentNeighbor[0],currentNeighbor[1]]=currentColor
                unusedNeighbors.remove(currentNeighbor)
                listOfColors.remove(currentColor)
                CheckNeighborhood(currentNeighbor[0],currentNeighbor[1])
                tryCount=0 #prevent the try count from being cumulitive. see if this also makes the if statement a few lines down redundant.
                if(pixelsPlaced%pixelsPerFrame==0):
                    print str(len(listOfColors))+" colors left to place."
                    canvas.save("Output"+str(pixelsPlaced/pixelsPerFrame)+".png")
                pixelsPlaced+=1
                break #break from the loop
        if(attempt==maxAttempts): #if the attempt count managed to get this high, we know it had to give up.
            tryCount+=1
        if(len(listOfColors)==0):
            break
    print "Adjusting Tolerances: "+str(maxTolerance)
    maxTolerance+=1#increase the tolerance a touch. 
        
print "Pruning stray branches."
for a in unusedNeighbors:
    pixels[a[0],a[1]]=(0,0,0,255)
canvas.save("outputFinal.png")
print time.time()
print "finished!"

#next version should have preset seeds with LOCATIONS. multiple pictures should be generated. animate the many finished renders.
#tolerance threshold for finding best fit algorithms, rather than randomizing whats left. (perhaps reverse search. fill by going through the neighbor and finding closest color, rather than finding the closest neighbor to the color.


#http://codegolf.stackexchange.com/questions/22144/images-with-all-colors
