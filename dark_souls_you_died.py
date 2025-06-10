import os
import math, time

import obspython as obs
import pygame
import pygame._sdl2.audio as sdl2_audio

# project directory
dir = ""

hotkey_id = obs.OBS_INVALID_HOTKEY_ID

# scene item alignment enums (the real ones are broken?)
ALIGN_TOPLEFT = 5
ALIGN_TOPCENTER = 4
ALIGN_TOPRIGHT = 6
ALIGN_CENTERLEFT = 1
ALIGN_CENTER = 0
ALIGN_CENTERRIGHT = 2
ALIGN_BOTLEFT = 9
ALIGN_BOTCENTER = 8
ALIGN_BOTRIGHT = 10

scn_name = "dark_souls_you_died"

scn_you_died = None
scn_item_vign = None
scn_item_text = None

time_start = 0	# animation start time

#################################################
# obs
#################################################

def script_description(): # script description
  return """<center><h2>Dark Souls: You Died</h2></center>
		<p>Play the 'You died' animation from Dark Souls.</p>"""

def script_load(settings): # on script load
	print("script_load")
	global dir
	
	dir = os.path.dirname(os.path.dirname(script_path()))	#get project directory
	
	loadHotkey(settings)	# load hotkey settings
	
	obs.obs_frontend_add_event_callback(afterLoad)	# add event callback

def script_unload():
	print("script_unload")
	
	obs.obs_scene_release(scn_you_died)
	#obs.obs_sceneitem_release(scn_item_vign)
	#obs.obs_sceneitem_release(scn_item_text)
	
	obs.obs_frontend_remove_event_callback(afterLoad)	# remove event callback

def script_save(settings): # on script save
	print("script_save")
	saveHotkey(settings)	# save hotkey settings

def script_update(settings): # on change settings
	print("script_update")

def script_tick(seconds): # on tick
	pass

#################################################
# functions
#################################################

def afterLoad(event):
	if event == obs.OBS_FRONTEND_EVENT_FINISHED_LOADING:	# if event is frontend loaded
		obs.obs_frontend_remove_event_callback(afterLoad)	# remove event callback
		buildScene()										# build anim scene

def loadHotkey(settings): # load hotkey
	global hotkey_id
	hotkey_id = obs.obs_hotkey_register_frontend(script_path(), "You Died", onHotkey)	# register hotkey
	hotkey_array = obs.obs_data_get_array(settings, "you_died")							# get hotkey data
	obs.obs_hotkey_load(hotkey_id, hotkey_array)										# load hotkey
	obs.obs_data_array_release(hotkey_array)											# release hotkey data

def saveHotkey(settings): # save hotkey
	global hotkey_id
	hotkey_array = obs.obs_hotkey_save(hotkey_id)				# get hotkey data
	obs.obs_data_set_array(settings, "you_died", hotkey_array)	# save hotkey
	obs.obs_data_array_release(hotkey_array)					# release hotkey data

def onHotkey(pressed):
	global dir
	global scn_item_text
	global time_start
	global sound
	if not pressed:								# on key release
		time_start = time.time()				# start timer
		obs.timer_add(timerCallback, 1)			# add timer callback
		playAudio(dir + "/audio/you_died.mp3")	# play audio
		print("Playing animation: Dark Souls: You Died")

def buildScene():
	global dir
	global scn_you_died
	global scn_item_text
	global scn_item_vign
	
	print("BUILD SCENE")
	
	config = obs.obs_frontend_get_profile_config()			# get profile settings
	w_src = obs.config_get_uint(config, "Video", "BaseCX")	# get canvas width
	h_src = obs.config_get_uint(config, "Video", "BaseCY")	# get canvas height
	
	src_you_died = obs.obs_get_source_by_name(scn_name)			# find scene source
	if src_you_died:											# if source found
		scn_you_died = obs.obs_scene_from_source(src_you_died)	# create scene
	else:														# if source not found
		scn_you_died = obs.obs_scene_create(scn_name)			# create scene
	
	# image
	src_name = "img_you_died"
	scn_item_vign = obs.obs_scene_find_source(scn_you_died, src_name)			# get item in scene by name
	if not scn_item_vign:														# if item not found
		src_vign = obs.obs_source_create("image_source", src_name, None, None)	# create source
		scn_item_vign = obs.obs_scene_add(scn_you_died, src_vign)				# add item from source
	src_vign = obs.obs_sceneitem_get_source(scn_item_vign)						# get source from item
	settings = obs.obs_data_create()											# create settings
	obs.obs_data_set_string(settings, "file", dir + "/sprites/vignette.png")	# set vignette
	obs.obs_source_update(src_vign, settings)									# update item settings
	obs.obs_data_release(settings)												# release settings
	
	pos = obs.vec2()												# create position
	pos.x = w_src / 2												# set x position
	pos.y = h_src / 2												# set y position
	obs.obs_sceneitem_set_pos(scn_item_vign, pos)					# set position
	obs.obs_sceneitem_set_alignment(scn_item_vign, ALIGN_CENTER)	# set alignment
	scale = obs.vec2()												# create scale
	obs.obs_sceneitem_get_scale(scn_item_vign, scale)				# get scale
	scale.x = 7.5													# set x scale
	obs.obs_sceneitem_set_scale(scn_item_vign, scale)				# set scale
	obs.obs_sceneitem_set_locked(scn_item_vign, True)				# lock vignette
	
	# filter
	src_name = "opacity"
	flt_opc = obs.obs_source_get_filter_by_name(src_vign, src_name)				# get vignette filter
	if not flt_opc:																# if filter not found
		flt_opc = obs.obs_source_create("color_filter", src_name, None, None)	# create filter source
		obs.obs_source_filter_add(src_vign, flt_opc)							# add filter to vignette
	settings = obs.obs_source_get_settings(flt_opc)								# create settings
	obs.obs_data_set_double(settings, "opacity", 0)								# set filter opacity
	obs.obs_source_update(flt_opc, settings)									# update settings
	obs.obs_data_release(settings)												# release settings
	
	# text
	src_name = "text_you_died"
	scn_item_text = obs.obs_scene_find_source(scn_you_died, src_name)			# get item in scene by name
	if not scn_item_text:														# if item not found
		src_text = obs.obs_source_create("text_gdiplus", src_name, None, None)	# create source
		scn_item_text = obs.obs_scene_add(scn_you_died, src_text)				# add item from source
	src_text = obs.obs_sceneitem_get_source(scn_item_text)						# get source from item
	
	settings = obs.obs_data_create()							# create settings
	obs.obs_data_set_string(settings, "text", "YOU DIED")		# set text
	obs.obs_data_set_int(settings, "color", 4278190148)			# set text color
	font = obs.obs_data_create()								# create font
	obs.obs_data_set_string(font, "face", "Times New Roman")	# set font face
	obs.obs_data_set_int(font, "size", int(h_src * .2))			# set font size
	obs.obs_data_set_obj(settings, "font", font)				# set font
	obs.obs_data_set_int(settings, "opacity", 0)				# set opacity
	obs.obs_source_update(src_text, settings)					# update settings
	
	pos = obs.vec2()												# create position
	pos.x = w_src / 2												# set x position
	pos.y = h_src / 2												# set y position
	obs.obs_sceneitem_set_pos(scn_item_text, pos)					# set position
	obs.obs_sceneitem_set_alignment(scn_item_text, ALIGN_CENTER)	# set alignment
	scale = obs.vec2()												# create scale
	obs.obs_sceneitem_get_scale(scn_item_text, scale)				# get scale
	scale.x = scale.y * .81											# set x scale
	obs.obs_sceneitem_set_scale(scn_item_text, scale)				# set scale
	obs.obs_sceneitem_set_locked(scn_item_text, True)				# lock text
	obs.obs_data_release(settings)
	
	# reference release
	#obs.obs_source_release(src_you_died)	# release source
	#obs.obs_source_release(src_vign)		# release vignette source
	#obs.obs_source_release(flt_opc)			# release vignette opacity filter source
	#obs.obs_source_release(src_text)		# release text source
	
	#obs.obs_data_save_json(settings, dir + "/TEMP.json")

def setOpacity(scn_item, value: float):
	value = int(min(max(0, value), 1) * 100)
	src = obs.obs_sceneitem_get_source(scn_item)
	ftr_opacity = obs.obs_source_get_filter_by_name(src, "opacity")
	settings = obs.obs_source_get_settings(ftr_opacity)
	obs.obs_data_set_double(settings, "opacity", value)
	obs.obs_source_update(ftr_opacity, settings)
	
	# reference release
	#obs.obs_source_release(src)			# release scene item source
	#obs.obs_source_release(ftr_opacity)	# release filter source
	#obs.obs_data_release(settings)		# release settings

def timerCallback(): # timer callback (every millisecond)
	global scn_item_vign
	global scn_item_text
	global time_start
	
	setOpacity(scn_item_vign, min(time.time() - time_start, 1) - max(time.time() - time_start - 4, 0))
	
	src_text = obs.obs_sceneitem_get_source(scn_item_text)
	opacity = (min(time.time() - time_start - 1, 1) - max(time.time() - time_start - 4, 0))
	settings = obs.obs_source_get_settings(src_text)
	obs.obs_data_set_int(settings, "opacity", int(min(max(0, opacity), 1) * 100))
	obs.obs_source_update(src_text, settings)
	
	# reference release
	obs.obs_data_release(settings)	# release settings
	
	# end timer
	if time.time() - time_start >= 5:		# if timer complete
		obs.timer_remove(timerCallback)		# remove timer callback
		

#################################################
# pygame
#################################################

def getAudioDevices(capture_devices: bool = False) -> tuple[str, ...]: # get available audio devices
	init = pygame.mixer.get_init()										# get mixer initialization
	if not init: pygame.mixer.init()									# if mixer not initialized, initialize mixer
	devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))	# get devices
	if init: pygame.mixer.quit()										# if mixer initialized, quit mixer
	return devices														# return devices
	
def playAudio(path_audio: str): # play audio at given path
	pygame.mixer.music.load(path_audio)	# load audio
	pygame.mixer.music.play()			# play audio

#################################################
# run
#################################################

devices = getAudioDevices()								# get audio devices
device = devices[0]										# set device to default audio device
if "CABLE In 16ch (VB-Audio Virtual Cable)" in devices:	# if vbcable found
	device = "CABLE In 16ch (VB-Audio Virtual Cable)"	# set device to vbcable
pygame.mixer.init(devicename=device)					# initialize mixer with device

#pygame.mixer.get_busy()