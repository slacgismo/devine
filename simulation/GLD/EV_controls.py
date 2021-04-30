import re
import json
from datetime import datetime
import pandas as pd
# needs to add secrets
import secrets
import mysql.connector

try:
	mydb = mysql.connector.connect(
		host='docker.for.mac.localhost',
		user=secrets.db_user,
		port='3306',
		passwd=secrets.db_password,
		database=secrets.db_name,
		auth_plugin='mysql_native_password')
except Exception as e:
	print("Error in DB connection")
	print(e)


mycursor = mydb.cursor(buffered=True)

# Definitions for on_commit:
query_status = "INSERT INTO db_station_status_rt(station_id, port_number, status, port_power_kW, port_load_kWh, user_id, timedate) VALUES(%s, %s, %s, %s, %s, %s)"

query_db_station_log = "INSERT INTO db_station_log(station_id, port_number, group_name, station_load_kWh, port_status, " \
					   "shed_state, port_load_kWh, allowed_power_kW, port_power_kW, recent_user, timedate, exception_flag) " \
					   "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

charging_events = pd.read_pickle('Google/Plymouth/charging_events')
pattern = re.compile("GOOGLE / MTV-1625-3")


def on_init(t):
	# DO ON INITIALIZATION STUFF HERE
	stations = json.load(open('Google/Plymouth/google_stations.json'))
	# print('stations: ', stations)
	obj = gridlabd.get("objects")
	# pattern1 = re.compile("load_")
	pattern2 = re.compile("GOOGLE")
	ev_load = []
	for item in obj:
		# if pattern1.search(item):
		# 	ev_load.append(item)
		if pattern2.search(item):
			ev_load.append(item)
	# print(ev_load)
	# print('###############')
	for i in ev_load:
		gridlabd.set_value(i, 'phases', stations[i]+'N')
		# print('station: ', i)
		# print('phases: ', gridlabd.get_value(i, 'phases'))

	print('###############')
	# print()
	# print(gridlabd.get_value('GOOGLE / MTV-1625-2-13-1', 'phases'))
	# gridlabd.set_value('GOOGLE / MTV-1625-2-13-1', 'phases', 'BCN')
	# print(gridlabd.get_value('GOOGLE / MTV-1625-2-13-1', 'phases'))

	return True 

def on_commit(t):
	# GLOBAL ON COMMIT ie every solution 
	# http://docs.gridlabd.us/_page.html?owner=slacgismo&project=gridlabd&branch=develop&folder=/Module&doc=/Module/Python.md
	print("Unix Time: ", t)
	ts = datetime.fromtimestamp(t - 25200)
	print("Datetime: ", ts)
	# print(sum(charging_events['Datetime'] == datetime.fromtimestamp(t)))

	# This will eventually change when running optimization - need to understand what replaces the charging_events and
	# iterate
	mask_stations = charging_events[charging_events['Datetime'] == ts]
	mask_stations.reset_index(drop=True, inplace=True)

	for ind in mask_stations.index:
		if pattern.search(mask_stations['gld_station_name'][ind]):
			pass
		else:
			station_id = mask_stations['gld_station_name'][ind]
			port_number = station_id[-1]
			group_name = station_id[0:17]
			station_load = mask_stations['Energy Consumed (AC kWh)'][ind]

			shed_state = str(mask_stations['Rolling Avg. Power (AC kW)'][ind]/6.6)
			port_load = station_load
			allowed_power = str(6.6)
			port_power = mask_stations['Rolling Avg. Power (AC kW)'][ind]
			recent_user = mask_stations['User Id'][ind]
			timedate = ts
			exception_flag = False
			if not pd.isna(mask_stations['Plug Disconnect Time'][ind]):
				port_status = '0'
				print('Station', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind], 'is available')
			else:
				port_status = '1'
				print('Station', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind], 'is occupied')

			# These values will come from the algorithm
			gridlabd.set_value(station_id, "constant_power_A", str(port_power))
			power_val_A = gridlabd.get_value(station_id, "constant_power_A")

			try:
				vals = (station_id, port_number, group_name, station_load, port_status, shed_state, port_load, allowed_power,
						port_power, recent_user, timedate, exception_flag)
				mycursor.execute(query_db_station_log, vals)
				print('Succesfull values insertion in DB')
			except Exception as e:
				print('db write error:')
				print('Error: ', e)
			mydb.commit()
	return True

			# # print('Station/Port:', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind],':',power_val_A)
			# if not pd.isna(mask_stations['Plug Disconnect Time'][ind]):
			# 	# This gives station/port status available
			# 	print('Station', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind], 'is available')
			# 	try:
			# 		vals = [mask_stations['gld_station_name'], '0']
			# 		cursor.execute(query_status, vals)
			# 		conn.commit()
			# 	except Exception as e:
			# 		print('Error in station available: ', e)
			#
			# else:
			# 	# This sets station/port status to occupied
			# 	print('Station is occupied')
			# 	try:
			# 		vals = [mask_stations['gld_station_name'], '0']
			# 		cursor.execute(query_status, vals)
			# 		conn.commit()
			# 	except Exception as e:
			# 		print('Error in station occupied: ', e)



