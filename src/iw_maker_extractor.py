# This code will hide *any* python object into an image as an invisible watermark.
# The object can be retrieved, and it will be fully intact and operational.
#
# Want to watermark your Stable Diffusion images, so you'll always remember the seed and other params you used to make them?
# This will do it.
#
# Limitations:
#
#   The watermark will probably break, if the image is altered.
#   Every three pixels can hide one byte. (A 500 x 500 image can hide ~250 kB)
# 
# Usage:
#
#       anImage = PIL.Image.new('RGB', (100,100), color = (0, 0, 0))
#       objectToHide = {"theSecret":"I once lived inside an image, but now I'm free!"}
#       imageWithInvisbleWatermark = hideInImage(anImage,objectToHide)
#       extractedObject = suckHiddenThingFromImage(imageWithInvisbleWatermark)
#       print(extractedObject["theSecret"])
#
# (Trivia: Invisible watermarking falls under the umbrella of steganography.)
#
# Code by exo-pla-net.

#import numpy
import pickle
#import PIL

def access_bit(bytesObject, bitIndex):
    # In a bytesObject, bytesObject[3] grabs the fourth byte.
    # There are 8 bits in a byte.
    # Thus, the 33rd bit will be found in the math.floor(33/8) => 4th byte, and the particular bit in the byte will be 33%8 => remainder of 1, or the 2nd bit of that byte.
    byteIndex = int(bitIndex // 8) # // => floor division. Divides and applies math.floor() to the result
    bitIndex = int(bitIndex % 8)
    # Now we will make the bit of interest be the rightmost bit, then apply an & operator to target it, returning 1 iff the bit is 1.
    # myBits >> shiftAmount =>	moves bits of myBits to the right by shiftAmount, copying the leftmost bits and dropping the rightmost bits.
    byteWithTargetBitOnRight = bytesObject[byteIndex] >> bitIndex
    return byteWithTargetBitOnRight & 1 # bitA & bitB => 1 if both bits are 1, otherwise 0
def toBitArray(thing):
  bytesOfThing = pickle.dumps(thing) # pickle.dumps turns an object into bytes
  # simply grab each bit sequentially, and add each bit to an array
  return [access_bit(bytesOfThing,i) for i in range(len(bytesOfThing)*8)]
def bitsArrayToObject(bitsArray):
  numberOfBits = len(bitsArray)
  assert(numberOfBits%8 == 0) # 8 bits make a byte. if numberOfBits is a non-multiple of 8 bits, something is broken!
  numberOfBytes=numberOfBits//8
  # we'll inspect each byte (each set of 8 bits) and compile them into an array
  byteArray = []
  for byteIndex in range(0,numberOfBytes):
    theNumberRepresentedByTheBitsInTheByte = 0
    # For whatever terrible reason, likely "endianness", the number represented by bits in bytes is in reverse order.
    # We'll sum up all the bits, creating a normal base-10 integer and letting it represent our byte.
    # [0,1,0,0,0,0,0,0] => 00000010 => 2
    for bitIndex in reversed(range(0,8)):
      theBit=bitsArray[byteIndex*8+bitIndex]
      bitsNumberValue = theBit * 2 ** bitIndex #  ** is the exponent operator, so 2^bitIndex
      theNumberRepresentedByTheBitsInTheByte+=bitsNumberValue
    byteArray.append(theNumberRepresentedByTheBitsInTheByte)
  theBytes = bytes(byteArray) # convert the array [128,64,...] into b'\x80\x03K*.'
  return pickle.loads(theBytes) # pickle.loads turns bytes back into the object represented by said bytes

def getPixelAtBitIndex(pixelIterable,bitIndex):
  byteIndex = bitIndex // 8
  bitInByteIndex = bitIndex % 8
  # triplet == byte
  pertinentTripletIndex = byteIndex
  # (bit1,bit2,bit3),(bit4,bit5,bit6),(bit7,bit8,magicBit)
  pertinentSubTriplet = bitInByteIndex // 3
  return pixelIterable[pertinentTripletIndex + pertinentSubTriplet]

def getColorAtBitIndex(pixelIterable,bitIndex):
  pertinentPixel = getPixelAtBitIndex(pixelIterable,bitIndex)
  byteIndex = bitIndex // 8
  bitInByteIndex = bitIndex % 8
  petinentColorIndex = bitInByteIndex % 3
  return pertinentPixel[petinentColorIndex]

def makeOdd(aNumber):
  if aNumber%2 !=0:
    return aNumber
  else:
    aNumber-=1
    if(aNumber<0):
      aNumber+=2
    return aNumber
def makeEven(aNumber):
  if aNumber%2 ==0:
    return aNumber
  else:
    return aNumber-1 # given it's odd, it will be >=1, so no fear of negative


def hideInImage(anImage,thingToHide):
  thingBits = toBitArray(thingToHide)
  pixelsIterable = anImage.getdata()
  numberOfPixels = len(pixelsIterable)
  numberOfBits = len(thingBits)
  # Each pixel has 3 color values, and thus can hold 3 bits.
  # 3 pixels can encode 3x3 = 9 bits. A byte is 8 bits. Thus, 3 pixels can encode 1 byte, with 1 bit left over.
  # The leftover bit can thus be used to signal "continue reading bitstream" or "end of bitstream".
  # Given 3 pixels can encode one byte, the number of pixels required is 3 * numberOfBytes
  numberOfBytes = numberOfBits // 8
  numberOfPixelsRequired = numberOfBytes * 3
  assert(numberOfPixels >= numberOfPixelsRequired)
  # A color value of even => 0 bit
  # A color value of odd => 1 bit
  # In the 9th color, even => continue, and odd => stop
  corruptedImage = anImage.copy()
  imageWidth,imageHeight = corruptedImage.size
  corruptedImagePixels = corruptedImage.getdata()
  # We'll iterate over the pixels, corrupting them appropriately.
  bitIndex = -1
  bitInByteIndex = -1
  for pixelIndex in range(0,numberOfPixelsRequired):
    uncorruptedPixel = corruptedImagePixels[pixelIndex]
    pixelList=[]
    isFinalPixel = pixelIndex == numberOfPixelsRequired-1
    for colorIndex in range(0,3):
      bitInByteIndex +=1
      isFinalSlotInPixelTriplet = bitInByteIndex == 8
      if isFinalSlotInPixelTriplet:
        if(isFinalPixel):
          corruptedColor = makeOdd(thisColor)
        else:
          corruptedColor = makeEven(thisColor)
          bitInByteIndex=-1
      else:
        bitIndex+=1
        thisBit = thingBits[bitIndex]
        thisColor = uncorruptedPixel[colorIndex]
        if thisBit==0:
          corruptedColor = makeEven(thisColor)
        else:
          corruptedColor = makeOdd(thisColor)
      pixelList.append(corruptedColor)
    corruptedPixel = tuple(pixelList)
    row = pixelIndex // imageWidth
    column = pixelIndex % imageWidth
    # print(f"starting with {[thingBits[bitIndex-2],thingBits[bitIndex-1],thingBits[bitIndex]]} and {uncorruptedPixel} putting this pixel {corruptedPixel} into x,y {(column, row)} ")
    corruptedImage.putpixel((column, row), corruptedPixel)
  return corruptedImage

def extractBits(aCorruptedImage):
  bitsOfThing=[]
  bitIndexInByte=0
  for pixel in aCorruptedImage.getdata():
    for colorIndex in range(0,3):
      bitIndexInByte+=1
      isTheStopGoBit = bitIndexInByte==9
      if isTheStopGoBit:
        isStopBit = pixel[colorIndex]%2==1
        if isStopBit:
          return bitsOfThing
        bitIndexInByte=0
      else:
        bitsOfThing.append(pixel[colorIndex]%2)
def suckHiddenThingFromImage(aCorruptedImage):
  bitsOfThing = extractBits(aCorruptedImage)
  return bitsArrayToObject(bitsOfThing)