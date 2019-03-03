import RPi.GPIO as GPIO
import time
import threading
import sys
import Adafruit_DHT
import os

#LedPin = 17
LedPin = 11
FanPin = 25
count = 0
file_path = "example.mp3"

class myThread (threading.Thread):
   def __init__(self, threadID, name, TRIG, ECHO, LEDPIN, FANPIN):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.TRIG = TRIG
      self.ECHO = ECHO
      self.LEDPIN = LEDPIN
      self.FANPIN = FANPIN
   def run(self):
      print "Starting " + self.name
      # Get lock to synchronize threads
      threadLock.acquire()
      calculate_distance(self.name, self.TRIG, self.ECHO, self.LEDPIN, self.FANPIN)
      # Free lock to release next thread
      threadLock.release()

def calculate_distance(name, TRIG, ECHO, LEDPIN, FANPIN):
        count = 0
	flag = 0
	while count < 20:
		try:

		    GPIO.setup(TRIG,GPIO.OUT)
		    GPIO.setup(ECHO,GPIO.IN)

		    GPIO.output(TRIG, False)
		    time.sleep(1)

		    GPIO.output(TRIG, True)
		    time.sleep(0.00001)
		    GPIO.output(TRIG, False)

		    while GPIO.input(ECHO)==0:
		    	pulse_start = time.time()

		    while GPIO.input(ECHO)==1:
		    	pulse_end = time.time()

		    pulse_duration = pulse_end - pulse_start
		    distance = pulse_duration * 17150
		    distance = round(distance, 2)

		    print "Distance:",distance,"cm"
		    if distance < 10:
                        #Let's deal with LEDs first
                        GPIO.setup(LEDPIN, GPIO.OUT)
                        GPIO.setup(FANPIN, GPIO.OUT)
                        if flag == 0:
    	                    GPIO.output(LEDPIN, GPIO.HIGH)
                            humidity, temperature = Adafruit_DHT.read_retry(11, 4)
                            print 'Temp: {0:0.1f} C  Humidity: {1:0.1f} %'.format(temperature, humidity)
                            if temperature > 20:
                                print "Starting A/C with pin: %d" % FANPIN
                                GPIO.output(FANPIN, GPIO.HIGH)
                                time.sleep(0.5)
                                GPIO.output(FANPIN, GPIO.LOW)
    			    flag = 1
                            print "flag: %d" % flag
                            mp3 = 'omxplayer -o local ' + file_path
                            os.system(mp3)
			else:
    			    GPIO.output(LEDPIN, GPIO.LOW)
                            GPIO.output(FANPIN, GPIO.LOW)
   			    flag = 0

                    time.sleep(2)

		except KeyboardInterrupt:
			GPIO.cleanup()

                count += 1

        return distance


GPIO.setmode(GPIO.BCM)
threadLock = threading.Lock()
threads = []

# Create new threads
thread2 = myThread(2, "Sensor-2", 10, 9, 11, 25)

# Start new Threads
thread2.start()

# Add threads to thread list
threads.append(thread2)

# Wait for all threads to complete
for t in threads:
    t.join()
print "Exiting Main Thread"
