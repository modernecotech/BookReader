#!/usr/bin/python

"""commands for book reader
The OICO book reader will start the cmu sphinx listener on startup awaiting one of two words. 

READ - will:
disable voice recognition
scan page, 
carry out OCR and save it to a text file, 
generate a Text To Speech WAV file
play the WAV file
Start voice recognition again
 

HELP - 
disable voice recognition
read out a canned cycle help file.
start voice recogntion again

pause - 
pause the playback

continue
-continue playback

again
-replay the wav file


joypad commands
j1.get_axis(0) > 0.0: #right
j1.get_axis(0) < 0.0: #left
j1.get_axis(1) > 0.0: #down
j1.get_axis(1) < 0.0: #up
j1.get_button(1) == 1: #A
j1.get_button(2) == 1: #B
j1.get_button(9) == 1: #start
j1.get_button(8) == 1: #select


===abbyy=======
licence SWEE-1101-1003-8368-1709-8357


use festival 2.4 with the voice_cmu_us_slt_cg voice. save the .festivalrc file in home. 

on the PC run the festival 2.4 from /festival/festival/bin with the /.festival command

"""

#subprocess for running scanimage and abbyy and tts
#pyaudio for the voice recognition and pygame for audio playback and 
#joypad control
import sys,os,subprocess,pyaudio,time,pygame

#for saving and loading settings
import cPickle as pickle 

#the pyinotify (for USB insertion), and pygame (for joypad entries) listeners run in parallel, thus multiprocessing is used to run them together. 
from multiprocessing import Process

#for notifying on insertion of USB memory or disk. in add_watch() include
#auto_add=True and watch for wm.addwatch('/MEDIA', pyinotify.IN_CREATE)
import pyinotify, pyttsx


#python sane library for scanning
import pyinsane.abstract_th as pyinsane
import PIL

#startup the scanning interface
devices = pyinsane.get_devices()
print devices
assert(len(devices)>0)
device=devices[0]
scanner_id=device.name
device.options['mode'].value='Gray'
device.options['resolution'].value=300


#startup the pygame system for joypad controls
pygame.init()
pygame.joystick.init()
j1=pygame.joystick.Joystick(0)
j1.init()


#the text to speech engine using espeak. for user interface
engine = pyttsx.init()
#the speed and voice of speech. 
engine.setProperty('rate',120)
engine.setProperty('voice',mb-en1)
#engine.say('testing. espeak')
engine.runAndWait()


#help system
def helping():
	pygame.mixer.init()
	pygame.mixer.music.load("help.wav")
	pygame.mixer.music.play(0)
	while pygame.mixer.music.get_busy() == True:
		pygame.event.wait()
		if j1.get_button(1) == 1: #A
			Lastpos=pygame.mixer.music.get_pos()
			pickle.dump(Lastpos, open("save.p","wb"))
			pygame.mixer.music.pause()
		elif j1.get_button(2) == 1: #B
			Lastpos=0.0
			pickle.dump(Lastpos, open("save.p","wb"))
			pygame.mixer.music.unpause()
		elif j1.get_axis(1) > 0.0: #down
			volume=pygame.mixer.music.get_volume() - 0.1
			pygame.mixer.music.set_volume(volume)
		elif j1.get_axis(1) < 0.0: #up
			volume=pygame.mixer.music.get_volume() + 0.1
			pygame.mixer.music.set_volume(volume)
		elif j1.get_button(9) == 1: #select - back to menu
			break
		elif j1.get_button(8) == 1: #start - scan new page and play
			pygame.mixer.music.quit()
			capture()					
	pygame.mixer.quit()

#playback for read and again
def playback():
	pygame.mixer.init()
	pygame.mixer.music.load("test.wav")
	pygame.mixer.music.play(0)
	while pygame.mixer.music.get_busy() == True:
		pygame.event.wait()
		if j1.get_button(1) == 1: #A - pause playback
			Lastpos=pygame.mixer.music.get_pos()
			pickle.dump(Lastpos, open("save.p","wb"))
			pygame.mixer.music.pause()
		elif j1.get_button(2) == 1: #B - resume playback
			Lastpos=0.0
			pickle.dump(Lastpos, open("save.p","wb"))
			pygame.mixer.music.unpause()
		elif j1.get_axis(1) > 0.0: #down - lower volume
			volume=pygame.mixer.music.get_volume() - 0.1
			pygame.mixer.music.set_volume(volume)
		elif j1.get_axis(1) < 0.0: #up - raise volume
			volume=pygame.mixer.music.get_volume() + 0.1
			pygame.mixer.music.set_volume(volume)
		elif j1.get_button(9) == 1: #select - back to menu
			break
		elif j1.get_button(8) == 1: #start - scan new page and play
			pygame.mixer.quit()
			capture()			
	pygame.mixer.quit()


#playback for paused item
def playbackSaved():
	pygame.mixer.init()
	pygame.mixer.music.load("test.wav")
	Lastpos= pickle.load(open("save.p","rb"))
	pygame.mixer.music.play(0,Lastpos)
	while pygame.mixer.music.get_busy() == True:
		pygame.event.wait()
		Lastpos=0.0
		if j1.get_button(1) == 1: #A - pause playback
			Lastpos=pygame.mixer.music.get_pos()
			pickle.dump(Lastpos, open("save.p","wb"))
			pygame.mixer.music.pause()
		elif j1.get_button(2) == 1: #B - resume playback
			Lastpos=0.0
			pickle.dump(Lastpos, open("save.p","wb"))
			pygame.mixer.music.unpause()
		elif j1.get_button(9) == 1: #select - back to menu
			break
		elif j1.get_axis(1) > 0.0: #down - lower volume
			volume=pygame.mixer.music.get_volume() - 0.1
			pygame.mixer.music.set_volume(volume)
		elif j1.get_axis(1) < 0.0: #up - raise volume
			volume=pygame.mixer.music.get_volume() + 0.1
			pygame.mixer.music.set_volume(volume)
		elif j1.get_button(8) == 1: #start - scan new page and play
			pygame.mixer.quit()
			capture()
	pygame.mixer.quit()



def capture():
	data=""
	#if using scanner for image capture below
	print "options set" 
	scan_session=device.scan(multiple=False)
	try:
		while True:
			print "scan read started"
			scan_session.scan.read()
	except EOFError:
		print "pass"
		pass
	print "scanning done"
	img = scan_session.images[0]
	print "img setting done"
	img.save("test.jpeg")
	print "img saving done"
	#if using abbyyocr for OCR below	
	subprocess.call(["abbyyocr11", "-if", "test.jpeg", "-f", "TextUnicodeDefaults", "-tet", "UTF8", "-of", "test.txt"])
	data=open("test.txt")
	#calling ivona TTS engine to convert the text to audio	
	subprocess.call(["./test_tts_engine", "-cert", "Certificate_of_authenticity_a2529366_140717134620-signed.ca", "-voice", "./libvoice_en_gb_brian.so", "-vox", "./vox_en_gb_brian16i-mf", "-t", data.read(), "-o", "test.wav"])
	#playback the audio recorded
	playback()


#this runs when a USB memory is insterted
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self,event):
		usb_insertion(event.name, event.pathname)


#notification manager for usb memory insertions
wm=pyinotify.WatchManager()
handler=EventHandler()
notifier=pyinotify.ThreadedNotifier(wm, handler)
notifier.start()
wdd=wm.add_watch('/media', pyinotify.IN_CREATE, rec=True, auto_add=True)


#when a USB memory is inserted it reads the memory stick, and generates a new folder.
def usb_insertion(name, path):
	time.sleep(0.1)	
	libraryfolder=os.getenv("HOME")+"/"+name
	print "library folder is", libraryfolder
	if os.path.exists(libraryfolder)==True:	
		message = "folder exists. rescanning for changes"
		print message
		engine.say(message)
		buildLibrary(path,libraryfolder)
	elif os.path.exists(libraryfolder)==False:
		message = "folder doesnt exist, making folder"		
		print message
		engine.say(message)
		os.mkdir(libraryfolder)
		buildLibrary(path,libraryfolder)

#build a library of the files in the USB memory and convert them to text for readback
def buildLibrary(path, libraryFolder):
	message = "build library"
	print message
	engine.say(message)
	files= [f for f in os.listdir(path) if f.lower().endswith(('.azw', '.azw4', '.cbz', '.cbr', '.cbc', '.chm', '.djvu', '.docx', '.epub', '.fb2', '.htm', '.html', '.htmlz', '.lit', '.lrf', '.mobi',  '.odt', '.prc', '.pdb', '.pml', '.rb', '.rtf', '.snb', '.tcr', '.txt', '.pdf', '.txtz'))]	
	print "file list after filtering", files
	pickle.dump(files, open(libraryFolder+"/save.p", "wb"))
	#use ebook-convert "./iPad intro.pdf" "./iPad intro.txt" and ivona to build a library of files that can be played back and save to a library file in the folder. then split into 50 lines per page.
	for s in files:
		inputfile = path+"/"+s
		outputfile = libraryFolder+"/"+s+".txt"
		subprocess.call(["ebook-convert", inputfile, outputfile])
	libraryPlayback(libraryFolder)

def libraryPlayback(libraryFolder):
	pygame.event.wait()
	message = "library playback"
	print message
	engine.say(message) 
	#begin playback of menu items to select which text to play
	if j1.get_button(9) == 1: #start
		print 'read'
		capture()
	elif j1.get_button(8) == 1: #select
		playback()
		print 'again'
	elif j1.get_button(1) == 1: #A
		playback()
		print 'help'
	elif j1.get_button(2) == 1: #B
		playback()
		print 'other'


#the main program loop using only joypad
while True:
	pygame.event.wait()
	if j1.get_button(9) == 1: #start
		print 'scan and read'
		capture()
	elif j1.get_button(8) == 1: #select - back to menu / exit
		message = "you are at the top menu"
		engine.say(message)
		print 'again'
	elif j1.get_button(2) == 1: #B - playback paused position
		playbackSaved()
		print 'playback saved'
	elif j1.get_button(1) == 1: #A - help 
		helping()
		print 'help'

