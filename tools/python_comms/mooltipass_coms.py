from array import array
from time import sleep
import platform
import usb.core
import usb.util
import random
import struct
import string
import pickle
import copy
import time
import sys
import os
from keyboard import *

USB_VID                 = 0x16D0
USB_PID                 = 0x09A0

LEN_INDEX               = 0x00
CMD_INDEX               = 0x01
DATA_INDEX              = 0x02
PREV_ADDRESS_INDEX      = 0x02
NEXT_ADDRESS_INDEX      = 0x04
NEXT_CHILD_INDEX        = 0x06
SERVICE_INDEX           = 0x08
DESC_INDEX              = 6
LOGIN_INDEX             = 37
NODE_SIZE				= 132

CMD_DEBUG               = 0x01
CMD_PING                = 0x02
CMD_VERSION             = 0x03
CMD_CONTEXT             = 0x04
CMD_GET_LOGIN           = 0x05
CMD_GET_PASSWORD        = 0x06
CMD_SET_LOGIN           = 0x07
CMD_SET_PASSWORD        = 0x08
CMD_CHECK_PASSWORD      = 0x09
CMD_ADD_CONTEXT         = 0x0A
CMD_EXPORT_FLASH        = 0x30 
CMD_EXPORT_FLASH_END    = 0x31
CMD_IMPORT_FLASH_BEGIN  = 0x32 
CMD_IMPORT_FLASH        = 0x33 
CMD_IMPORT_FLASH_END    = 0x34
CMD_EXPORT_EEPROM       = 0x35 
CMD_EXPORT_EEPROM_END   = 0x36
CMD_IMPORT_EEPROM_BEGIN = 0x37 
CMD_IMPORT_EEPROM       = 0x38 
CMD_IMPORT_EEPROM_END   = 0x39
CMD_ERASE_EEPROM        = 0x40
CMD_ERASE_FLASH         = 0x41
CMD_ERASE_SMC           = 0x42
CMD_DRAW_BITMAP         = 0x43
CMD_SET_FONT            = 0x44
CMD_EXPORT_FLASH_START  = 0x45
CMD_EXPORT_EEPROM_START = 0x46
CMD_SET_BOOTLOADER_PWD  = 0x47
CMD_JUMP_TO_BOOTLOADER  = 0x48
CMD_CLONE_SMARTCARD     = 0x49
CMD_STACK_FREE          = 0x4A
CMD_GET_RANDOM_NUMBER   = 0x4B
CMD_START_MEMORYMGMT    = 0x50
CMD_END_MEMORYMGMT      = 0x51
CMD_IMPORT_MEDIA_START  = 0x52
CMD_IMPORT_MEDIA        = 0x53
CMD_IMPORT_MEDIA_END    = 0x54
CMD_READ_FLASH_NODE     = 0x55
CMD_WRITE_FLASH_NODE    = 0x56
CMD_SET_FAVORITE        = 0x57
CMD_SET_STARTINGPARENT  = 0x58
CMD_SET_CTRVALUE        = 0x59
CMD_ADD_CARD_CPZ_CTR    = 0x5A
CMD_GET_CARD_CPZ_CTR    = 0x5B
CMD_CARD_CPZ_CTR_PACKET = 0x5C
CMD_SET_MOOLTIPASS_PARM = 0x5D
CMD_GET_MOOLTIPASS_PARM = 0x5E
CMD_GET_FAVORITE        = 0x5F
CMD_RESET_CARD          = 0x60
CMD_READ_CARD_LOGIN     = 0x61
CMD_READ_CARD_PASS      = 0x62
CMD_SET_CARD_LOGIN      = 0x63
CMD_SET_CARD_PASS       = 0x64
CMD_GET_FREE_SLOT_ADDR  = 0x65
CMD_GET_STARTING_PARENT = 0x66
CMD_GET_CTRVALUE        = 0x67
CMD_ADD_UNKNOWN_CARD    = 0x68
CMD_USB_KEYBOARD_PRESS  = 0x69
CMD_MOOLTIPASS_STATUS   = 0x70
CMD_FUNCTIONAL_TEST_RES = 0x71
CMD_SET_DATE            = 0x72
CMD_GET_30_FREE_SLOTS   = 0x73

def keyboardSend(epout, data1, data2):
	packetToSend = array('B')
	packetToSend.append(data1)
	packetToSend.append(data2)
	sendHidPacket(epout, CMD_USB_KEYBOARD_PRESS, 0x02, packetToSend)
	time.sleep(0.05)

def keyboardTestKey(epout, KEY, MODIFIER):
	if( KEY in KEYTEST_BAN_LIST ): return ''
	keyboardSend(epout, KEY, MODIFIER)
	keyboardSend(epout, KEY, MODIFIER)
	keyboardSend(epout, KEY_RETURN, 0)
	string = raw_input()
	if (string == ''):
		return string
	return string[0]

def keyboardKeyMap(epout, key):
	if ( (key & 0x3F) == KEY_EUROPE_2 ):
		if (key & (SHIFT_MASK|ALTGR_MASK) == (SHIFT_MASK|ALTGR_MASK)):
			return keyboardTestKey(epout, KEY_EUROPE_2_REAL, KEY_SHIFT|KEY_RIGHT_ALT)
		elif (key & SHIFT_MASK):
			return keyboardTestKey(epout, KEY_EUROPE_2_REAL, KEY_SHIFT)
		elif (key & ALTGR_MASK):
			return keyboardTestKey(epout, KEY_EUROPE_2_REAL, KEY_RIGHT_ALT)
		else:
			return keyboardTestKey(epout, KEY_EUROPE_2_REAL, 0)

	elif (key & (SHIFT_MASK|ALTGR_MASK) == (SHIFT_MASK|ALTGR_MASK)):
		return keyboardTestKey(epout, key & ~(SHIFT_MASK|ALTGR_MASK), KEY_SHIFT|KEY_RIGHT_ALT)
			
	elif (key & SHIFT_MASK):
		return keyboardTestKey(epout, key & ~SHIFT_MASK, KEY_SHIFT)

	if (key & ALTGR_MASK):
		return keyboardTestKey(epout, key & ~ALTGR_MASK, KEY_RIGHT_ALT)

	else:
		return keyboardTestKey(epout, key, 0)

def keyboardTest(epout):
	fileName = raw_input("Name of the Keyboard (example: ES): ");

	# dictionary to store the
	Layout_dict = dict()

	# No modifier combinations
	for bruteforce in range(KEY_EUROPE_2, KEY_SLASH+1):
		output = keyboardKeyMap(epout, bruteforce)
		if (output == ''): continue
		if output in Layout_dict:
			print "Already stored"
			print bruteforce
		else:
			Layout_dict.update({output: bruteforce})

	# SHIFT combinations
	for bruteforce in range(KEY_EUROPE_2, KEY_SLASH+1):
		output = keyboardKeyMap(epout, SHIFT_MASK|bruteforce)
		if (output == ''): continue
		if output in Layout_dict:
			print "Already stored"
			print SHIFT_MASK|bruteforce
		else:
			Layout_dict.update({output : SHIFT_MASK|bruteforce})

	# ALTGR combinations
	for bruteforce in range(KEY_EUROPE_2, KEY_SLASH+1):
		output = keyboardKeyMap(epout, ALTGR_MASK|bruteforce)
		if (output == ''): continue
		if output in Layout_dict:
			print "Already stored"
			print ALTGR_MASK|bruteforce
		else:
			Layout_dict.update({output : ALTGR_MASK|bruteforce})

	# ALTGR + SHIFT combinations
	for bruteforce in range(KEY_EUROPE_2, KEY_SLASH+1):
		output = keyboardKeyMap(epout, SHIFT_MASK|ALTGR_MASK|bruteforce)
		if (output == ''): continue
		if output in Layout_dict:
			print "Already stored"
			print SHIFT_MASK|ALTGR_MASK|bruteforce
		else:
			Layout_dict.update({output : SHIFT_MASK|ALTGR_MASK|bruteforce})


	hid_define_str = "const uint8_t PROGMEM keyboardLUT_"+fileName+"[95] = \n{\n"
	img_contents = array('B')

	for key in KeyboardAscii:
		if(key not in Layout_dict):
			#print key + " Not found"
			Layout_dict.update({key:0})
		#else:
			#print "BruteForced: " + key

		""" Format C code """
		keycode = hex(Layout_dict[key])+","

		# Write img file
		img_contents.append(Layout_dict[key])

		# Handle special case
		if(key == '\\'):
			comment = " // " + hex(ord(key)) + " '" + key + "'\n"
		else:
			comment = " // " + hex(ord(key)) + " " + key + "\n"

		newline = "%4s%-5s" % (" ", keycode) + comment
		# add new line into existing string
		hid_define_str = hid_define_str + newline

	# finish C array
	hid_define_str = hid_define_str + "};"
	print hid_define_str

	# finish img file
	img_file = open("_"+fileName+"_keyb_lut.img", "wb")
	img_file.write(img_contents)
	img_file.close()

	# Save C array into .c file
	text_file = open("keymap_"+fileName+".c", "w")
	text_file.write(hid_define_str)
	text_file.close()
	
def pickle_write(data, outfile):
        f = open(outfile, "w+b")
        pickle.dump(data, f)
        f.close()
		
def pickle_read(filename):
        f = open(filename)
        data = pickle.load(f)
        f.close()
        return data
		
def receiveHidPacket(epin):
	try :
		data = epin.read(epin.wMaxPacketSize, timeout=15000)
		return data
	except usb.core.USBError as e:
		#print e
		sys.exit("Mooltipass didn't send a packet")

def receiveHidPacketWithTimeout(epin):
	try :
		data = epin.read(epin.wMaxPacketSize, timeout=15000)
		return data
	except usb.core.USBError as e:
		return None


def sendHidPacket(epout, cmd, len, data):
	# data to send
	arraytosend = array('B')

	# if command copy it otherwise copy the data
	if cmd != 0:
		arraytosend.append(len)
		arraytosend.append(cmd)

	# add the data
	if data is not None:
		arraytosend.extend(data)

	#print arraytosend
	#print arraytosend

	# send data
	epout.write(arraytosend)

def sendCustomPacket(epin, epout):
	command = raw_input("CMD ID: ")
	packet = array('B')
	temp_bool = 0
	length = 0

	#fill packet
	packet.append(0)
	packet.append(int(command, 16))

	#loop until packet is filled
	while temp_bool == 0 :
		try :
			intval = int(raw_input("Byte %s: " %length), 16)
			packet.append(intval)
			length = length + 1
		except ValueError :
			temp_bool = 1

	#update packet length
	packet[0] = length

	#ask for how many packets to receiveHidPacket
	packetstoreceive = input("How many packets to be received: ")

	#send packet
	sendHidPacket(epout, 0, 0, packet)

	#receive packets
	for i in range (0, packetstoreceive):
		print receiveHidPacket(epin)

def	uploadBundle(epin, epout):
	# Empty set password packet
	mooltipass_password = array('B')
	for i in range(62):
		mooltipass_password.append(0)
	success_status = 0
	sendHidPacket(epout, CMD_IMPORT_MEDIA_START, 62, mooltipass_password)
	# Check that the import command worked
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		# Open bundle file
		bundlefile = open('bundle.img', 'rb')
		packet_to_send = array('B')
		byte = bundlefile.read(1)
		bytecounter = 0
		# While we haven't finished looping through the bytes
		while byte != '':
			# Add byte to current packet
			packet_to_send.append(struct.unpack('B', byte)[0])
			# Increment byte counter
			bytecounter = bytecounter + 1
			# Read new byte
			byte = bundlefile.read(1)
			# If packet full, send it
			if bytecounter == 33:
				sendHidPacket(epout, CMD_IMPORT_MEDIA, 33, packet_to_send)
				packet_to_send = array('B')
				bytecounter = 0
				# Check ACK
				if receiveHidPacket(epin)[DATA_INDEX] != 0x01:
					print "Error in upload"
					raw_input("press enter to acknowledge")
		# Send the remaining bytes
		sendHidPacket(epout, CMD_IMPORT_MEDIA, bytecounter, packet_to_send)
		# Wait for ACK
		receiveHidPacket(epin)
		# Inform we sent everything
		sendHidPacket(epout, CMD_IMPORT_MEDIA_END, 0, None)
		# Check ACK
		if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
			success_status = 1
		# Close file
		bundlefile.close()
	else:
		success_status = 0
		print "fail!!!"
		print "likely causes: mooltipass already setup"

	return success_status

def mooltipassInit(hid_device, intf, epin, epout):
	# Ask for Mooltipass ID
	try :
		mp_id = int(raw_input("Enter Mooltipass ID: "))
		print ""
	except ValueError :
		mp_id = 0
		print ""

	# Create text file
	f = open(time.strftime("%Y-%m-%d-%H-%M-%S-Mooltipass IDs.txt"), 'wb')

	# Loop
	try:
		temp_bool = 0
		while temp_bool == 0:
			# Operation success state
			success_status = 1

			# Empty set password packet
			mooltipass_password = array('B')

			# We need 62 random bytes to set them as a password for the Mooltipass
			sys.stdout.write('Step 1... ')
			sys.stdout.flush()
			#print "Getting first random half"
			sendHidPacket(epout, CMD_GET_RANDOM_NUMBER, 0, None)
			data = receiveHidPacketWithTimeout(epin)
			mooltipass_password.extend(data[DATA_INDEX:DATA_INDEX+32])
			#print "Getting second random half"
			sendHidPacket(epout, CMD_GET_RANDOM_NUMBER, 0, None)
			data2 = receiveHidPacketWithTimeout(epin)
			mooltipass_password.extend(data2[DATA_INDEX:DATA_INDEX+30])

			# Check that we actually received data
			if data == None or data2 == None:
				success_status = 0
				print "fail!!!"
				print "likely causes: deffective crystal or power supply"

			# Send our bundle
			if success_status == 1:
				sys.stdout.write('Step 2... ')
				sys.stdout.flush()
				sendHidPacket(epout, CMD_IMPORT_MEDIA_START, 62, mooltipass_password)
				# Check that the import command worked
				if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
					# Open bundle file
					bundlefile = open('bundle.img', 'rb')
					packet_to_send = array('B')
					byte = bundlefile.read(1)
					bytecounter = 0
					# While we haven't finished looping through the bytes
					while byte != '':
						# Add byte to current packet
						packet_to_send.append(struct.unpack('B', byte)[0])
						# Increment byte counter
						bytecounter = bytecounter + 1
						# Read new byte
						byte = bundlefile.read(1)
						# If packet full, send it
						if bytecounter == 33:
							sendHidPacket(epout, CMD_IMPORT_MEDIA, 33, packet_to_send)
							packet_to_send = array('B')
							bytecounter = 0
							# Check ACK
							if receiveHidPacket(epin)[DATA_INDEX] != 0x01:
								print "Error in upload"
								raw_input("press enter to acknowledge")
					# Send the remaining bytes
					sendHidPacket(epout, CMD_IMPORT_MEDIA, bytecounter, packet_to_send)
					# Wait for ACK
					receiveHidPacket(epin)
					# Inform we sent everything
					sendHidPacket(epout, CMD_IMPORT_MEDIA_END, 0, None)
					# Check ACK
					if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
						success_status = 1
					# Close file
					bundlefile.close()
				else:
					success_status = 0
					print "fail!!!"
					print "likely causes: mooltipass already setup"

			# Inform the Mooltipass that the bundle is sent so it can start functional test
			if success_status == 1:
				sys.stdout.write('Step 3... ')
				sys.stdout.flush()
				magic_key = array('B')
				magic_key.append(0)
				magic_key.append(241)
				sendHidPacket(epout, CMD_SET_MOOLTIPASS_PARM, 2, magic_key)
				if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
					success_status = 1
					print ""
					print "Please follow the on screen instructions on the mooltipass"
				else:
					success_status = 0
					print "fail!!!"
					print "likely causes: none"

			# Wait for the mooltipass to inform the script that the test was successfull
			temp_bool2 = False
			sys.stdout.write('Waiting for functional test result...')
			sys.stdout.flush()
			while temp_bool2 != True:
				test_result = receiveHidPacketWithTimeout(epin)
				if test_result == None:
					sys.stdout.write('.')
					sys.stdout.flush()
				else:
					if test_result[CMD_INDEX] == CMD_FUNCTIONAL_TEST_RES and test_result[DATA_INDEX] == 0:
						success_status = 1
						print " ok!"
					else:
						success_status = 0
						print " fail!!!"
						print "Please look at the screen to know the cause"
					temp_bool2 = True

			# Send set password packet
			if success_status == 1:
				sys.stdout.write('Step 4... ')
				sys.stdout.flush()
				sendHidPacket(epout, CMD_SET_BOOTLOADER_PWD, 62, mooltipass_password)
				if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
					# Write Mooltipass ID in file together with random bytes, flush write
					f.write(str(mp_id))
					f.write('|')
					f.write(''.join(format(x, '02x') for x in mooltipass_password))
					f.write('\r\n')
					f.flush()
					# Update Success status
					success_status = 1
					print ""
				else:
					success_status = 0
					print "fail!!!"
					print "likely causes: mooltipass already setup"

			# COMMENT THE NEXT LINE FOR PRODUCTION!
			#sendHidPacket(epout, CMD_JUMP_TO_BOOTLOADER, 62, mooltipass_password)

			if success_status == 1:
				# Let the user know it is done
				print "Setting up Mooltipass #"+str(mp_id)+" DONE"
				print "PLEASE WRITE \""+str(mp_id)+"\" ON THE BACK STICKER"
				# Increment Mooltipass ID
				mp_id = mp_id + 1
			else:
				print "---------------------------------------------------------"
				print "---------------------------------------------------------"
				print "Setting up Mooltipass #", mp_id, "FAILED"
				print "PLEASE PUT AWAY THIS MOOLTIPASS!!!!"
				print "---------------------------------------------------------"
				print "---------------------------------------------------------"

			# Disconnect this device
			print "\r\nPlease disconnect this Mooltipass"

			# Wait for no answer to ping
			temp_bool2 = 0
			while temp_bool2 == 0:
				# prepare ping packet
				ping_packet = array('B')
				ping_packet.append(0)
				ping_packet.append(CMD_PING)
				try:
					# try to send ping packet
					epout.write(ping_packet)
					try :
						# try to receive answer
						data = epin.read(epin.wMaxPacketSize, timeout=10000)
					except usb.core.USBError as e:
						#print e
						temp_bool2 = 1
				except usb.core.USBError as e:
					#print e
					temp_bool2 = 1
				time.sleep(.5)

			# Connect another device
			print "Connect other Mooltipass"

			# Wait for findHidDevice to return something
			temp_bool2 = 0;
			while temp_bool2 == 0:
				hid_device, intf, epin, epout = findHIDDevice(USB_VID, USB_PID, False)
				if hid_device is not None:
					temp_bool2 = 1
				time.sleep(.5)

			# Delay
			time.sleep(1)

			# New Mooltipass detected
			print "New Mooltipass detected"
			print ""
	except KeyboardInterrupt:
		f.close()
		print "File written, everything ok"

def setCurrentTimeout(epin, epout):
	packetToSend = array('B')
	packetToSend.append(2)
	choice = input("How many seconds: ")
	print ""
	packetToSend.append(choice)
	sendHidPacket(epout, CMD_SET_MOOLTIPASS_PARM, 2, packetToSend)
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Parameter changed"
	else:
		print "Couldn't change parameter"

def setCurrentKeyboard(epin, epout):
	packetToSend = array('B')
	packetToSend.append(1)
	print "0) EN_EN"
	print "1) FR_FR"
	print "2) ES_ES"
	choice = input("Make your choice: ")
	print ""
	packetToSend.append(64+18+choice)
	sendHidPacket(epout, CMD_SET_MOOLTIPASS_PARM, 2, packetToSend)
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Parameter changed"
	else:
		print "Couldn't change parameter"

def setCurrentTimeoutLockEn(epin, epout):
	packetToSend = array('B')
	packetToSend.append(3)
	choice = input("TRUE (1), FALSE (0): ")
	print ""
	packetToSend.append(choice)
	sendHidPacket(epout, CMD_SET_MOOLTIPASS_PARM, 2, packetToSend)
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Parameter changed"
	else:
		print "Couldn't change parameter"

def setCurrentTimeoutLock(epin, epout):
	packetToSend = array('B')
	packetToSend.append(4)
	choice = input("How many minutes: ")
	print ""
	packetToSend.append(choice)
	sendHidPacket(epout, CMD_SET_MOOLTIPASS_PARM, 2, packetToSend)
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Parameter changed"
	else:
		print "Couldn't change parameter"

def setGenericParameter(epin, epout, choice):
	packetToSend = array('B')
	packetToSend.append(choice)
	intval = int(raw_input("Hex value: "), 16)
	print ""
	packetToSend.append(intval)
	sendHidPacket(epout, CMD_SET_MOOLTIPASS_PARM, 2, packetToSend)
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Parameter changed"
	else:
		print "Couldn't change parameter"


def readCurrentUser(epin, epout):
	sendHidPacket(epout, CMD_READ_CARD_LOGIN, 0, None)
	data = receiveHidPacket(epin)
	if data[LEN_INDEX] == 1:
		print "Card not inserted"
	else:
		print "Current user:", "".join(map(chr, data[DATA_INDEX:])).split(b"\x00")[0]

def readCurrentPass(epin, epout):
	sendHidPacket(epout, CMD_READ_CARD_PASS, 0, None)
	data = receiveHidPacket(epin)
	if data[LEN_INDEX] == 1:
		print "Card not inserted or request not accepted"
	else:
		print "Current password:", "".join(map(chr, data[DATA_INDEX:])).split(b"\x00")[0]

def setCurrentUser(epin, epout):
	user = raw_input("New username: ")
	print "Please accept prompts on the Mooltipass"

	# Check that the context doesn't exist
	sendHidPacket(epout, CMD_SET_CARD_LOGIN, len(user)+1, array('B', user + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Username changed"
	else:
		print "Couldn't change username"

def setCurrentPass(epin, epout):
	user = raw_input("New password: ")
	print "Please accept prompts on the Mooltipass"

	# Check that the context doesn't exist
	sendHidPacket(epout, CMD_SET_CARD_PASS, len(user)+1, array('B', user + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Password changed"
	else:
		print "Couldn't change password"

def randomBytesGeneration(epin, epout):
	f = open('randombytes.bin', 'wb')

	for i in range(0, 1000000/32) :
		print i*32, "bytes out of 1M\r",
		sendHidPacket(epout, CMD_GET_RANDOM_NUMBER, 0, None)
		data = receiveHidPacket(epin)
		data[DATA_INDEX:DATA_INDEX+32].tofile(f)
		f.flush()

	f.close()

def unlockSmartcard(epin, epout):
	unlockPacket = array('B')
	pincode = raw_input("Enter pin code: ")
	unlockPacket.append(int(pincode, 16)/256)
	unlockPacket.append(int(pincode, 16)%256)
	# send packet, check answer
	sendHidPacket(epout, CMD_RESET_CARD, 2, unlockPacket)
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Smartcard erased"
	else:
		print "Couldn't erase smartcard"

def addServiceAndUser(epin, epout):
	tempPacket = array('B')
	service = raw_input("Service name: ")
	username = raw_input("Username: ")
	password = raw_input("Password: ")
	print "Please accept prompts on the Mooltipass"

	# Check that the context doesn't exist
	sendHidPacket(epout, CMD_CONTEXT, len(service)+1, array('B', service + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Service exists"
	else:
		print "Service doesn't exist, adding it"
		# Send the add context packet
		sendHidPacket(epout, CMD_ADD_CONTEXT, len(service)+1, array('B', service + b"\x00"))
		if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
			print "Service added"
		else:
			print "Couldn't add service"
			return

	# Set context
	sendHidPacket(epout, CMD_CONTEXT, len(service)+1, array('B', service + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Service set"
	else:
		print "Service couldn't be set"
		return

	# Add user
	sendHidPacket(epout, CMD_SET_LOGIN, len(username)+1, array('B', username + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "User set"
	else:
		print "User couldn't be set"
		return

	# Change password
	sendHidPacket(epout, CMD_SET_PASSWORD , len(password)+1, array('B', password + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Password changed"
	else:
		print "Password couldn't be changed"

def checkPasswordForService(epin, epout):
	tempPacket = array('B')
	service = raw_input("Service name: ")
	username = raw_input("Username: ")
	password = raw_input("Password: ")
	print "Please accept prompts on the Mooltipass"

	# Check that the context doesn't exist
	sendHidPacket(epout, CMD_CONTEXT, len(service)+1, array('B', service + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Service exists"
	else:
		print "Service doesn't exist"
		return

	# Add user
	sendHidPacket(epout, CMD_SET_LOGIN, len(username)+1, array('B', username + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "User set"
	else:
		print "User couldn't be set"
		return

	# Change password
	sendHidPacket(epout, CMD_CHECK_PASSWORD , len(password)+1, array('B', password + b"\x00"))
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Password OK"
	else:
		print "Password NOK"
		
def credGen(epin, epout):
	for i in range(0, 40):
		tempPacket = array('B')
		service = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))
		username = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))
		# Check that the context doesn't exist
		sendHidPacket(epout, CMD_CONTEXT, len(service)+1, array('B', service + b"\x00"))
		if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
			print "Service exists"
		else:
			print "Service doesn't exist, adding it"
			# Send the add context packet
			sendHidPacket(epout, CMD_ADD_CONTEXT, len(service)+1, array('B', service + b"\x00"))
			if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
				print "Service added"
			else:
				print "Couldn't add service"
				continue

		# Set context
		sendHidPacket(epout, CMD_CONTEXT, len(service)+1, array('B', service + b"\x00"))
		if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
			print "Service set"
		else:
			print "Service couldn't be set"
			continue

		# Add user
		sendHidPacket(epout, CMD_SET_LOGIN, len(username)+1, array('B', username + b"\x00"))
		if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
			print "User set"
		else:
			print "User couldn't be set"
			continue
		

def favoritePrint(epin, epout):
	favoriteArg = array('B')
	favoriteArg.append(0)

	# get user profile
	sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)
	print "Please accept memory management mode on the MP"
	while receiveHidPacket(epin)[DATA_INDEX] != 1:
		print "Please accept memory management mode on the MP"
		sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)
		data = receiveHidPacket(epin)

	# loop through fav slots
	for count in range(0, 15):
		favoriteArg[0] = count
		# request favorite
		sendHidPacket(epout, CMD_GET_FAVORITE, 1, favoriteArg)
		fav_data = receiveHidPacket(epin)
		# check if it is defined
		if fav_data[DATA_INDEX+0] != 0 or fav_data[DATA_INDEX+1] != 0:
			# read parent node
			sendHidPacket(epout, CMD_READ_FLASH_NODE, 2, fav_data[DATA_INDEX+0:DATA_INDEX+2])
			# read it
			data_parent = receiveHidPacket(epin)
			data_parent.extend(receiveHidPacket(epin)[DATA_INDEX:])
			data_parent.extend(receiveHidPacket(epin)[DATA_INDEX:])
			# read child node
			sendHidPacket(epout, CMD_READ_FLASH_NODE, 2, fav_data[DATA_INDEX+2:DATA_INDEX+4])
			# read it
			data_child = receiveHidPacket(epin)
			data_child.extend(receiveHidPacket(epin)[DATA_INDEX:])
			data_child.extend(receiveHidPacket(epin)[DATA_INDEX:])
			# truncate data to get service name
			print "slot", count, "service:", "".join(map(chr, data_parent[DATA_INDEX+SERVICE_INDEX:])).split(b"\x00")[0], "login:", "".join(map(chr, data_child[DATA_INDEX+LOGIN_INDEX:])).split(b"\x00")[0]
		else:
			print "slot", count, "doesn't have a favorite"

	# end memory management mode
	sendHidPacket(epout, CMD_END_MEMORYMGMT, 0, None)
	receiveHidPacket(epin)

def favoriteSelectionScreen(epin, epout):
	found_credential_sets = array('B')
	next_service_addr = array('B')
	next_child_addr = array('B')
	service_number_i = 0

	# get user profile
	sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)
	print "Please accept memory management mode on the MP"
	while receiveHidPacket(epin)[DATA_INDEX] != 1:
		print "Please accept memory management mode on the MP"
		sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)

	# get starting node
	sendHidPacket(epout, CMD_GET_STARTING_PARENT, 0, None)
	data = receiveHidPacket(epin)

	# print "starting node is address is", data[DATA_INDEX] + data[DATA_INDEX+1]*256
	next_service_addr.append(data[DATA_INDEX])
	next_service_addr.append(data[DATA_INDEX+1])
	next_child_addr.append(data[DATA_INDEX]);
	next_child_addr.append(data[DATA_INDEX]);

	# start printing credentials, loop until next service address is equal to node_addr_null
	while next_service_addr[0] != 0 or next_service_addr[1] != 0:
		# print empty line
		print ""
		# request parent node
		sendHidPacket(epout, CMD_READ_FLASH_NODE, 2, next_service_addr)
		# read it
		data_parent = receiveHidPacket(epin)
		data_parent.extend(receiveHidPacket(epin)[DATA_INDEX:])
		data_parent.extend(receiveHidPacket(epin)[DATA_INDEX:])
		# extract next child address
		next_child_addr[0] = data_parent[DATA_INDEX+NEXT_CHILD_INDEX]
		next_child_addr[1] = data_parent[DATA_INDEX+NEXT_CHILD_INDEX+1]
		# truncate data to get service name
		print "service found:", "".join(map(chr, data_parent[DATA_INDEX+SERVICE_INDEX:])).split(b"\x00")[0]
		# loop in the child nodes
		while next_child_addr[0] != 0 or next_child_addr[1] != 0:
			# store parent and child addresses for future tagging
			found_credential_sets.extend(next_service_addr)
			found_credential_sets.extend(next_child_addr)
			# request child node
			sendHidPacket(epout, CMD_READ_FLASH_NODE, 2, next_child_addr)
			# read it
			data_child = receiveHidPacket(epin)
			data_child.extend(receiveHidPacket(epin)[DATA_INDEX:])
			data_child.extend(receiveHidPacket(epin)[DATA_INDEX:])
			# extract next child address
			next_child_addr[0] = data_child[DATA_INDEX+NEXT_ADDRESS_INDEX]
			next_child_addr[1] = data_child[DATA_INDEX+NEXT_ADDRESS_INDEX+1]
			# truncate data to get login
			print service_number_i, "- login:", "".join(map(chr, data_child[DATA_INDEX+LOGIN_INDEX:])).split(b"\x00")[0], ", description:", "".join(map(chr, data_child[DATA_INDEX+DESC_INDEX:])).split(b"\x00")[0]
			service_number_i += 1
		# extract next parent address (see gNode def)
		next_service_addr[0] = data_parent[DATA_INDEX+NEXT_ADDRESS_INDEX]
		next_service_addr[1] = data_parent[DATA_INDEX+NEXT_ADDRESS_INDEX+1]

	# ask the user to pick a favorite
	print ""
	user_fav = 1000
	while user_fav >= service_number_i:
		user_fav = input("Choose your favorite: ")

	fav_slot_id = 1000
	while fav_slot_id > 15:
		fav_slot_id = input("Choose your slotid: ")

	# prepare packet to send
	favorite_set_packet = array('B')
	favorite_set_packet.append(fav_slot_id)
	favorite_set_packet.extend(found_credential_sets[user_fav*4:user_fav*4+4])

	# send packet, check answer
	sendHidPacket(epout, CMD_SET_FAVORITE, 5, favorite_set_packet)
	if receiveHidPacket(epin)[DATA_INDEX] == 0x01:
		print "Favorite added on the Mooltipass"
	else:
		print "Couldn't add favorite on Mooltipass"

	# end memory management mode
	sendHidPacket(epout, CMD_END_MEMORYMGMT, 0, None)
	receiveHidPacket(epin)
	
def exportUser(epin, epout):
	parent_nodes_addr_export = list()
	parent_nodes_export = list()
	child_nodes_addr_export = list()
	child_nodes_export = list()
	cpz_ctr_export = list()
	next_service_addr = array('B')
	next_child_addr = array('B')

	# get user profile
	sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)
	print "Please accept memory management mode on the MP"
	while receiveHidPacket(epin)[DATA_INDEX] != 1:
		print "Please accept memory management mode on the MP"
		sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)

	# get starting node
	sendHidPacket(epout, CMD_GET_STARTING_PARENT, 0, None)
	data = receiveHidPacket(epin)

	# print starting node
	print "Starting node address is at", format(data[DATA_INDEX] + data[DATA_INDEX+1]*256, '#04X')
	next_service_addr.append(data[DATA_INDEX])
	next_service_addr.append(data[DATA_INDEX+1])
	next_child_addr.append(data[DATA_INDEX]);
	next_child_addr.append(data[DATA_INDEX]);
	
	# write the starting node
	pickle_write(next_service_addr, "starting_node.txt")

	# start printing credentials, loop until next service address is equal to node_addr_null
	while next_service_addr[0] != 0 or next_service_addr[1] != 0:
		# request parent node
		sendHidPacket(epout, CMD_READ_FLASH_NODE, 2, next_service_addr)
		# read it and keep the node part
		data_parent = receiveHidPacket(epin)
		data_parent.extend(receiveHidPacket(epin)[DATA_INDEX:])
		data_parent.extend(receiveHidPacket(epin)[DATA_INDEX:])
		data_parent = data_parent[DATA_INDEX:DATA_INDEX+NODE_SIZE]
		# store node data together with its address
		print "Found parent node at", format(next_service_addr[0] + next_service_addr[1]*256, '#04X'), "- service name:", "".join(map(chr, data_parent[SERVICE_INDEX:])).split(b"\x00")[0]
		parent_nodes_addr_export.append(next_service_addr)
		parent_nodes_export.append(data_parent)
		# extract next child address
		next_child_addr[0] = data_parent[NEXT_CHILD_INDEX]
		next_child_addr[1] = data_parent[NEXT_CHILD_INDEX+1]
		# loop in the child nodes
		while next_child_addr[0] != 0 or next_child_addr[1] != 0:
			# request child node
			sendHidPacket(epout, CMD_READ_FLASH_NODE, 2, next_child_addr)
			# read it
			data_child = receiveHidPacket(epin)
			data_child.extend(receiveHidPacket(epin)[DATA_INDEX:])
			data_child.extend(receiveHidPacket(epin)[DATA_INDEX:])
			data_child = data_child[DATA_INDEX:DATA_INDEX+NODE_SIZE]
			# truncate data to get login
			print "Found child node at", format(next_child_addr[0] + next_child_addr[1]*256, '#04X'), "- login:", "".join(map(chr, data_child[LOGIN_INDEX:])).split(b"\x00")[0]
			child_nodes_addr_export.append(next_child_addr)
			child_nodes_export.append(data_child)
			# extract next child address
			next_child_addr = array('B')
			next_child_addr.append(data_child[NEXT_ADDRESS_INDEX])
			next_child_addr.append(data_child[NEXT_ADDRESS_INDEX+1])
		# extract next parent address (see gNode def)
		next_service_addr = array('B')
		next_service_addr.append(data_parent[NEXT_ADDRESS_INDEX])
		next_service_addr.append(data_parent[NEXT_ADDRESS_INDEX+1])

	# write the export
	pickle_write(parent_nodes_addr_export, "parent_nodes_addr.txt")
	pickle_write(parent_nodes_export, "parent_nodes.txt")
	pickle_write(child_nodes_addr_export, "child_nodes_addr.txt")
	pickle_write(child_nodes_export, "child_nodes.txt")
	
	# get the CPZ & CTR LUT entries
	sendHidPacket(epout, CMD_GET_CARD_CPZ_CTR, 0, None)
	temp_bool = True
	while temp_bool == True:
		received_data = receiveHidPacket(epin)
		# check if we received end of export packet
		if received_data[CMD_INDEX] == CMD_GET_CARD_CPZ_CTR:
			temp_bool = False
		else:
			cpz_ctr_export.append(received_data[DATA_INDEX:DATA_INDEX + received_data[LEN_INDEX]])
		
	# write the export
	pickle_write(cpz_ctr_export, "cpz_ctr_export.txt")
	
	# get the user CTR value
	sendHidPacket(epout, CMD_GET_CTRVALUE, 0, None)
	ctr_packet = receiveHidPacket(epin)
	pickle_write(ctr_packet[DATA_INDEX:DATA_INDEX + ctr_packet[LEN_INDEX]], "ctr_value.txt")
	
	# end memory management mode
	sendHidPacket(epout, CMD_END_MEMORYMGMT, 0, None)
	receiveHidPacket(epin)
	
def importUser(epin, epout):
	#print "parent nodes:"
	#print pickle_read("parent_nodes.txt")
	#print "child nodes:"
	#print pickle_read("child_nodes.txt")
	#print "parent addr:"
	#print pickle_read("parent_nodes_addr.txt")
	#print "child addr:"
	#print pickle_read("child_nodes_addr.txt")
	#print "cpz ctr:"
	#print pickle_read("cpz_ctr_export.txt")
	#print "ctr:"
	#print pickle_read("ctr_value.txt")
	#print "starting:"
	#print pickle_read("starting_node.txt")
	
	# Check Mootipass status
	sendHidPacket(epout, CMD_MOOLTIPASS_STATUS, 0, None)
	if receiveHidPacket(epin)[DATA_INDEX] == 9:
		# Unknown card inserted
		print "Unknown card inserted"
	else:
		print "Unsupported mode"

def recoveryProc(epin, epout):
	found_credential_sets = array('B')
	next_node_addr = array('B')
	service_addresses = list()
	service_names = list()
	service_nodes = list()
	login_addresses = list()
	login_names = list()
	login_nodes = list()
	pointed_logins = list()

	# get user profile
	sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)
	print "Please accept memory management mode on the MP"
	while receiveHidPacket(epin)[DATA_INDEX] != 1:
		print "Please accept memory management mode on the MP"
		sendHidPacket(epout, CMD_START_MEMORYMGMT, 0, None)
		
	# find mooltipass version
	sendHidPacket(epout, CMD_VERSION, 0, None)
	data = receiveHidPacket(epin)
	
	# print Mooltipass version, compute number of available pages and nodes per page
	print "Mooltipass has " + str(data[DATA_INDEX]) + "Mb of data"
	if data[DATA_INDEX] >= 16:
		number_of_pages = 256 * data[DATA_INDEX]
	else:
		number_of_pages = 512 * data[DATA_INDEX]
	if data[DATA_INDEX] >= 16:
		nodes_per_page = 4
	else:
		nodes_per_page = 2

	# get starting node
	sendHidPacket(epout, CMD_GET_STARTING_PARENT, 0, None)
	data = receiveHidPacket(epin)

	# print starting node
	print "Starting node address is at", format(data[DATA_INDEX] + data[DATA_INDEX+1]*256, '#04X')
	
	# start looping through the slots
	completion_percentage = 1
	#for pagei in range(128, number_of_pages):
	for pagei in range(128, 220):
		if int(float(float(pagei) / (float(number_of_pages) - 128)) * 100) != completion_percentage:
			completion_percentage = int(float(float(pagei) / (float(number_of_pages) - 128)) * 100)
			print "Scanning: " + str(completion_percentage) + "%, address", format(next_node_addr[0] + next_node_addr[1]*256, '#04X')
		for nodei in range(0, nodes_per_page):
			# request node
			next_node_addr = array('B')
			next_node_addr.append((nodei + (pagei << 3)) & 0x00FF)
			next_node_addr.append((pagei >> 5) & 0x00FF)
			#print "Scanning", format(next_node_addr[0] + next_node_addr[1]*256, '#04X')
			sendHidPacket(epout, CMD_READ_FLASH_NODE, 2, next_node_addr)
			# see if we are allowed
			node_data = receiveHidPacket(epin)
			if node_data[LEN_INDEX] > 1:
				# receive the two other packets
				node_data.extend(receiveHidPacket(epin)[DATA_INDEX:])
				node_data.extend(receiveHidPacket(epin)[DATA_INDEX:])
				if node_data[DATA_INDEX+1] & 0xC0 == 0x00:
					# if we found a parent node, store it along its address and service name
					print "Found parent node at", format(next_node_addr[0] + next_node_addr[1]*256, '#04X'), "- service name:", "".join(map(chr, node_data[DATA_INDEX+SERVICE_INDEX:])).split(b"\x00")[0]
					service_names.append("".join(map(chr, node_data[DATA_INDEX+SERVICE_INDEX:])).split(b"\x00")[0])
					service_addresses.append(next_node_addr[0] + next_node_addr[1]*256)
					service_nodes.append(node_data[DATA_INDEX:])
				elif node_data[DATA_INDEX+1] & 0xC0 == 0x40:
					# if we found a child node, store it along its address and login name
					print "Found child node at", format(next_node_addr[0] + next_node_addr[1]*256, '#04X'), "- login:", "".join(map(chr, node_data[DATA_INDEX+LOGIN_INDEX:])).split(b"\x00")[0]
					login_names.append("".join(map(chr, node_data[DATA_INDEX+LOGIN_INDEX:])).split(b"\x00")[0])
					login_addresses.append(next_node_addr[0] + next_node_addr[1]*256)
					pointed_logins.append(next_node_addr[0] + next_node_addr[1]*256)
					login_nodes.append(node_data[DATA_INDEX:])

	# sort service list together with addresses list
	service_names, service_addresses, service_nodes = (list(t) for t in zip(*sorted(zip(service_names, service_addresses, service_nodes))))
	
	# set correct parent
	starting_parent_data = array('B')
	starting_parent_data.append(service_addresses[0] & 0x00FF)
	starting_parent_data.append((service_addresses[0] >> 8) & 0x00FF)
	print "Starting parent set to", format(service_addresses[0], '#04X')
	sendHidPacket(epout, CMD_SET_STARTINGPARENT, 2, starting_parent_data)
	receiveHidPacket(epin)
	
	# check parent addresses validity
	for i in range(len(service_nodes)):
		next_child_addr = service_nodes[i][6] + (service_nodes[i][7] * 256)
		next_node_addr = service_nodes[i][4] + (service_nodes[i][5] * 256)
		prev_node_addr = service_nodes[i][2] + (service_nodes[i][3] * 256)
		# if next child address different than NODE_ADDR_NULL
		if next_child_addr != 0:
			# if we can find a child whose address corresponds...
			if next_child_addr in login_addresses:
				print "Checked first child for parent", format(service_addresses[i], '#04X'), "at address", format(next_child_addr, '#04X')
				pointed_logins.remove(next_child_addr)
			else:
				print "Wrong first child address for parent", format(service_addresses[i], '#04X'), "at address", format(next_child_addr, '#04X')
				raw_input("confirm")
		# Compute the normal prev and next in the linked list
		if i == 0:
			normal_prev_node = 0
		else:
			normal_prev_node = service_addresses[i-1]
		if i == len(service_nodes) - 1:
			normal_next_node = 0
		else:
			normal_next_node = service_addresses[i+1]
		# Check the prev and next nodes
		if next_node_addr == normal_next_node:
			print "Checked next node for parent", format(service_addresses[i], '#04X'), "at address", format(next_node_addr, '#04X')
		else:
			print "Wrong next node address for parent", format(service_addresses[i], '#04X'), "at address", format(next_node_addr, '#04X'), "should be", format(normal_next_node, '#04X')
			raw_input("confirm")
		if prev_node_addr == normal_prev_node:
			print "Checked prev node for parent", format(service_addresses[i], '#04X'), "at address", format(next_node_addr, '#04X')
		else:
			print "Wrong prev node address for parent", format(service_addresses[i], '#04X'), "at address", format(next_node_addr, '#04X'), "should be", format(normal_prev_node, '#04X')
			raw_input("confirm")	

	# check child addresses validity
	for i in range(len(login_nodes)):
		next_node_addr = login_nodes[i][4] + (login_nodes[i][5] * 256)
		prev_node_addr = login_nodes[i][2] + (login_nodes[i][3] * 256)
		# if next child address different than NODE_ADDR_NULL
		if next_node_addr != 0:
			# if we can find a child whose address corresponds...
			if next_node_addr in login_addresses:
				print "Checked next node for child", format(login_addresses[i], '#04X'), "at address", format(next_node_addr, '#04X')
				try:
					pointed_logins.remove(next_node_addr)
				except:
					pass
			else:
				print "Wrong next node for child", format(login_addresses[i], '#04X'), "at address", format(next_node_addr, '#04X')
				raw_input("confirm")
		# if prev child address different than NODE_ADDR_NULL
		if prev_node_addr != 0:
			# if we can find a child whose address corresponds...
			if prev_node_addr in login_addresses:
				print "Checked prev node for child", format(login_addresses[i], '#04X'), "at address", format(prev_node_addr, '#04X')
				try:
					pointed_logins.remove(prev_node_addr)
				except:
					pass
			else:
				print "Wrong prev node for child", format(login_addresses[i], '#04X'), "at address", format(prev_node_addr, '#04X')
				raw_input("confirm")
				
	# find if we have child nodes that are not registered
	if len(pointed_logins) != 0:
		print "There are orphan child nodes!"
		for orphan_child in pointed_logins:
			print "Address:", format(orphan_child, '#04X'), "- login:", login_names[login_addresses.index(orphan_child)]
			choice = raw_input("Do you want to delete it? (yes/no): ")
			if choice == "yes":
				empty_packet = array('B')
				for i in range(62):
					empty_packet.append(255)
				empty_packet[0] = orphan_child & 0x00FF
				empty_packet[1] = (orphan_child >> 8) & 0x00FF
				empty_packet[2] = 0
				sendHidPacket(epout, CMD_WRITE_FLASH_NODE, 62, empty_packet)
				if receiveHidPacket(epin)[DATA_INDEX] != 0x01:
					print "Error in writing"
				empty_packet[2] = 1
				sendHidPacket(epout, CMD_WRITE_FLASH_NODE, 62, empty_packet)
				if receiveHidPacket(epin)[DATA_INDEX] != 0x01:
					print "Error in writing"
				empty_packet[2] = 2
				empty_packet = empty_packet[0:16]
				sendHidPacket(epout, CMD_WRITE_FLASH_NODE, 17, empty_packet)
				if receiveHidPacket(epin)[DATA_INDEX] != 0x01:
					print "Error in writing"
	else:
		print "No orphan nodes"
		
	# end memory management mode
	sendHidPacket(epout, CMD_END_MEMORYMGMT, 0, None)
	receiveHidPacket(epin)

def findHIDDevice(vendor_id, product_id, print_debug):
	# Find our device
	hid_device = usb.core.find(idVendor=vendor_id, idProduct=product_id)

	# Was it found?
	if hid_device is None:
		if print_debug:
			print "Device not found"
		return None, None, None, None

	# Device found
	if print_debug:
		print "Mooltipass found"

	# Different init codes depending on the platform
	if platform.system() == "Linux":
		# Need to do things differently
		try:
			hid_device.detach_kernel_driver(0)
			hid_device.reset()
		except Exception, e:
			pass # Probably already detached
	else:
		# Set the active configuration. With no arguments, the first configuration will be the active one
		try:
			hid_device.set_configuration()
		except Exception, e:
			if print_debug:
				print "Cannot set configuration the device:" , str(e)
			return None, None, None, None

	#for cfg in hid_device:
	#	print "configuration val:", str(cfg.bConfigurationValue)
	#	for intf in cfg:
	#		print "int num:", str(intf.bInterfaceNumber), ", int alt:", str(intf.bAlternateSetting)
	#		for ep in intf:
	#			print "endpoint addr:", str(ep.bEndpointAddress)

	# Get an endpoint instance
	cfg = hid_device.get_active_configuration()
	intf = cfg[(0,0)]

	# Match the first OUT endpoint
	epout = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT)
	if epout is None:
		hid_device.reset()
		return None, None, None, None
	#print "Selected OUT endpoint:", epout.bEndpointAddress

	# Match the first IN endpoint
	epin = usb.util.find_descriptor(intf, custom_match = lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN)
	if epin is None:
		hid_device.reset()
		return None, None, None, None
	#print "Selected IN endpoint:", epin.bEndpointAddress

	# prepare ping packet
	byte1 = random.randint(0, 255)
	byte2 = random.randint(0, 255)
	ping_packet = array('B')
	ping_packet.append(2)
	ping_packet.append(CMD_PING)
	ping_packet.append(byte1)
	ping_packet.append(byte2)

	time.sleep(0.5)
	try:
		# try to send ping packet
		epout.write(ping_packet)
		# try to receive one answer
		temp_bool = 0
		while temp_bool == 0:
			try :
				# try to receive answer
				data = epin.read(epin.wMaxPacketSize, timeout=2000)
				if data[CMD_INDEX] == CMD_PING and data[DATA_INDEX] == byte1 and data[DATA_INDEX+1] == byte2 :
					temp_bool = 1
					if print_debug:
						print "Mooltipass replied to our ping message"
				else:
					if print_debug:
						print "Cleaning remaining input packets"
				time.sleep(.5)
			except usb.core.USBError as e:
				if print_debug:
					print e
				return None, None, None, None
	except usb.core.USBError as e:
		if print_debug:
			print e
		return None, None, None, None

	# Return device & endpoints
	return hid_device, intf, epin, epout

if __name__ == '__main__':
	# Main function
	print ""
	print "Mooltipass USB client"

	# Search for the mooltipass and read hid data
	hid_device, intf, epin, epout = findHIDDevice(USB_VID, USB_PID, True)

	if hid_device is None:
		sys.exit(0)
		
	# Print Mootipass status
	sendHidPacket(epout, CMD_MOOLTIPASS_STATUS, 0, None)
	status_data = receiveHidPacket(epin)
	if status_data[DATA_INDEX] == 0:
		print "No card in Mooltipass"
	elif status_data[DATA_INDEX] == 1:
		print "Mooltipass locked"
	elif status_data[DATA_INDEX] == 3:
		print "Mooltipass locked, unlocking screen"
	elif status_data[DATA_INDEX] == 5:
		print "Mooltipass unlocked"
	elif status_data[DATA_INDEX] == 9:
		print "Unknown smartcard inserted"

	choice = 1
	while choice != 0:
		# print use
		print ""
		print "0) Quit"
		print "1) Add a favorite"
		print "2) See current favorites"
		print "3) Erase unknown smartcard"
		print "4) Store 1M random bytes"
		print "5) Add service and username"
		print "6) Change password for username in service"
		print "7) Read current user name"
		print "8) Read current user password"
		print "9) Change current user name"
		print "10) Change current password"
		print "11) Jump to bootloader"
		print "12) Change Mooltipass keyboard layout"
		print "13) Change Mooltipass interaction timeout"
		print "14) Custom packet"
		print "15) Mooltipass initialization process (ONLY FOR MANUFACTURER)"
		print "16) Keyboard Test"
		print "17) Change Mooltipass timeout bool"
		print "18) Change Mooltipass timeout"
		print "19) Change Mooltipass touch detection integrator"
		print "20) Change Mooltipass touch wheel over sample"
		print "21) Change Mooltipass touch proximity param"
		print "22) Upload Bundle"
		print "23) Recovery program"
		print "24) Credential generator"
		print "25) Set screen saver bool"
		print "26) Export current user"
		print "27) Import user to unknown card"
		print "28) Check password for service & login"
		choice = input("Make your choice: ")
		print ""

		if choice == 1:
			favoriteSelectionScreen(epin, epout)
		elif choice == 2:
			favoritePrint(epin, epout)
		elif choice == 3:
			unlockSmartcard(epin, epout)
		elif choice == 4:
			randomBytesGeneration(epin, epout)
		elif choice == 5:
			addServiceAndUser(epin, epout)
		elif choice == 6:
			addServiceAndUser(epin, epout)
		elif choice == 7:
			readCurrentUser(epin, epout)
		elif choice == 8:
			readCurrentPass(epin, epout)
		elif choice == 9:
			setCurrentUser(epin, epout)
		elif choice == 10:
			setCurrentPass(epin, epout)
		elif choice == 11:
			sendHidPacket(epout, CMD_JUMP_TO_BOOTLOADER, 0, None)
		elif choice == 12:
			setCurrentKeyboard(epin, epout)
		elif choice == 13:
			setCurrentTimeout(epin, epout)
		elif choice == 14:
			sendCustomPacket(epin, epout)
		elif choice == 15:
			mooltipassInit(hid_device, intf, epin, epout)
		elif choice == 16:
			keyboardTest(epout)
		elif choice == 17:
			setCurrentTimeoutLockEn(epin, epout)
		elif choice == 18:
			setCurrentTimeoutLock(epin, epout)
		elif choice == 19:
			setGenericParameter(epin, epout, choice-14)
		elif choice == 20:
			setGenericParameter(epin, epout, choice-14)
		elif choice == 21:
			setGenericParameter(epin, epout, choice-14)
		elif choice == 22:
			uploadBundle(epin, epout)
		elif choice == 23:
			recoveryProc(epin, epout)
		elif choice == 24:
			credGen(epin, epout)
		elif choice == 25:
			setGenericParameter(epin, epout, 9)
		elif choice == 26:
			exportUser(epin, epout)
		elif choice == 27:
			importUser(epin, epout)
		elif choice == 28:
			checkPasswordForService(epin, epout)

	hid_device.reset()
