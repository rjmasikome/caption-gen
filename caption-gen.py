from time import sleep
import pyupm_i2clcd as lcd
import urllib2
import json
import re
import random
import mraa

# digital input - button in D6
touchPin = mraa.Gpio(6)
touchPin.dir(mraa.DIR_IN)

# digital output - led in D8
ledPin = mraa.Gpio(8) 
ledPin.dir(mraa.DIR_OUT)
ledPin.write(0)

# Some invalid json repair: http://stackoverflow.com/questions/15198426/fixing-invalid-json-escape
invalid_escape = re.compile(r'\\[0-7]{1,6}')  # up to 3 digits for byte values up to FF

def replace_with_byte(match):
        return unichr(int(match.group(0)[1:], 8))

def repair(brokenjson):
            return invalid_escape.sub(replace_with_byte, brokenjson) 
#################################################################

while 1:
    while touchPin.read() == 1:
        ledPin.write(1)
        sleep(2)

        print "Getting some quotes online..."

        url = 'http://api.forismatic.com/api/1.0/'
        params = 'method=getQuote&key=457653&format=json&lang=en'
        respJson = urllib2.urlopen(url, params).read()

        try:
            #Repair invalid json escape character
            repairMap = repair(respJson)
            respMap = json.loads(repairMap)

            print "Quotes received!"

            quoteText = respMap["quoteText"]
            quoteAuthor = respMap["quoteAuthor"]
            quote = list(quoteText + ' -' + quoteAuthor)
        except:
            print "Illegal character found, using generic"
            quote = list("Today is gonna be a great day.-")

        myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
        myLcd.setColor(random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))
        myLcd.cursorBlinkOn()

        line = 0

        for i in range(len(quote)):
            if i%16 == 0:
                if i%32 == 0:
                    # clear the whole screen if the LCD is fully occupied
                    sleep(0.7)
                    myLcd.setCursor(0,0)
                    myLcd.write("                ")
                    myLcd.setCursor(1,0)
                    myLcd.write("                ")
                if i > 0:
                    line += 1
            line = line % 2
            myLcd.setCursor(line,i%16)
            myLcd.write(str(quote[i]))
            sleep(0.2)

        sleep(3)

        myLcd.clear()
        myLcd.cursorBlinkOff()
        myLcd.setColor(0,0,0)
        ledPin.write(0)