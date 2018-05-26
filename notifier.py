
#!/usr/bin/python

#notifier setup
import pyinotify, os, subprocess, time, pyttsx, pygame
import cPickle as pickle

#for joystick activation
pygame.init()
pygame.joystick.init()
j1=pygame.joystick.Joystick(0)
j1.init()


#the text to speech engine using espeak. 
engine = pyttsx.init()
#the speed of speech. 
engine.setProperty('rate',150)
engine.say('testing. espeak')
engine.runAndWait()
#notification manager for usb memory insertions
wm=pyinotify.WatchManager()

#this runs when a USB memory is insterted
class EventHandler(pyinotify.ProcessEvent):
	def process_IN_CREATE(self,event):
		usb_insertion(event.name, event.pathname)

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
	
#	os.listdir(path+"/")		
#	print os.path.isfile(path)

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
	message = "library playback"
	print message
	engine.say(message) 
	#begin playback of menu items to select which text to play

#start the pyinotifier and keep running it.
handler=EventHandler()
notifier=pyinotify.Notifier(wm, handler)
wdd=wm.add_watch('/media', pyinotify.IN_CREATE, rec=True, auto_add=True)
notifier.loop()

