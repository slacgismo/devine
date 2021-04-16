import re

def on_init(t):

	# DO ON INITIALIZATION STUFF HERE
	obj = gridlabd.get("objects")
	pattern = re.compile("load_")
	ev_load = []
	for item in obj:
		if pattern.search(item):
			ev_load.append(item)
	print(ev_load)
	return True 

def on_commit(t):
	# GLOBAL ON COMMIT ie every solution 
	# http://docs.gridlabd.us/_page.html?owner=slacgismo&project=gridlabd&branch=develop&folder=/Module&doc=/Module/Python.md
	print("Time: ", t)
	# load_AB = gridlabd.get_object("load_20")
	# print("EV AB: ", load_AB)
	# power_val_A = gridlabd.get_value("load_1","constant_power_A")
	# if t>1608973200 :
	# 	gridlabd.set_value("load_1","constant_power_B", "30")
	#
	# print("Power drawn on phase A load 1", power_val_A)
	# power_val_B = gridlabd.get_value("load_1","constant_power_B")
	# print("Power drawn on phase B load 1", power_val_B)
	return True 

