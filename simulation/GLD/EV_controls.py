import re
import json
from datetime import datetime
import pandas as pd
import numpy as np
# needs to add secrets
import secrets
import mysql.connector

# SETTING UP THE DATABASE COMMUNICATION AND ALL REQUIREMENTS
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

query_n_stations = "SELECT COUNT(*) FROM db_stations"
n_stations = mycursor.execute(query_n_stations)
recent_departure = np.zeros(n_stations)

# Definitions for on_commit:
query_status = "INSERT INTO db_station_status_rt(station_id, port_number, status, port_power_kW, port_load_kWh, user_id, timedate) VALUES(%s, %s, %s, %s, %s, %s)"

query_db_station_log = "INSERT INTO db_station_log(station_id, port_number, group_name, station_load_kWh, port_status, " \
					   "shed_state, port_load_kWh, allowed_power_kW, port_power_kW, recent_user, timedate, exception_flag) " \
					   "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

query_update = "UPDATE db_station_status_rt SET status = %s, port_power_kW = %s, port_load_kWh = %s, user_id = %s," \
			   "arrival = %s, timedate = %s  WHERE station_id = %s"

charging_events = pd.read_pickle('Google/Plymouth/charging_events')
pattern = re.compile("GOOGLE / MTV-1625-3")

query_status_rt = "SELECT status from db_station_status_rt ORDER BY id ASC"
query_arrival_rt = "SELECT arrival from db_station_status_rt ORDER BY id ASC"
query_evid_rt = "SELECT user_id from db_station_status_rt ORDER BY id ASC"

def query_select(mycursor, query):
	print('query: ', query)
	try:
		mycursor.execute(query)
		db_data = np.asarray(mycursor.fetchall()).flatten()
		db_data = db_data.astype(int)
	except Exception as e:
		print('Error: ', e)
	return db_data

# OPTIMIZATION FUNCTIONS
# Pulling departure times based on historical data
try:
	dep_times = json.load(open('Google/Plymouth/data_dep_times.json'))
except:
	print('COULD NOT OPEN FILE')
# Function to generate potential departure times
def potential_dep_times(lowBound, uppBound, num_desired_time, increment=15):
	sortedInterval = dep_times
	filtered_data = []
	minTime = (60 / increment) * lowBound + 1
	maxTime = (60 / increment) * uppBound + 1
	for user in sortedInterval:
		for j in range(len(sortedInterval[user])):
			if (sortedInterval[user][j][0] > minTime and sortedInterval[user][j][0] <= maxTime):
				filtered_data.append(sortedInterval[user][j][1])
	predictions = list()
	for i in range(num_desired_time):
		predictions.append(np.random.choice(filtered_data))
	return predictions

# INITIALIZING GLD SIMULATION
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
	mask_stations = charging_events[charging_events['Datetime'] == ts] # getting information from field on what's happening at each station in this time
	mask_stations.reset_index(drop=True, inplace=True)

	for ind in mask_stations.index:
		if pattern.search(mask_stations['gld_station_name'][ind]): # filtering stations for just GOOGLE-2
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

			# Checking port status: available (0) or occupied (1)
			if not pd.isna(mask_stations['Plug Disconnect Time'][ind]):
				port_status = '0'
				# print('Station', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind], 'is available')
			else:
				port_status = '1'
				'''TODO: if port status is occupied check departure times and remove if time has passed. If the there's
				 no departure times generate one more'''
				# print('Station', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind], 'is occupied')

			# Checking for arrival
			if not pd.isna(mask_stations['Plug Connect Time'][ind]):
				arrival = '1'
				'''TODO: implement function to generate potential dep_times (done) and add to db_station_status_rt'''
				print('Station', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind], 'has just arrived')
				print(potential_dep_times(np.maximum(ts.hour - 1, 0), np.minimum(ts.hour + 1, 24), 3))
			else:
				arrival = '0'
				# print('Station', mask_stations['EVSE ID'][ind], '/', mask_stations['Port'][ind], 'has been connected')

			# These values will come from the algorithm
			gridlabd.set_value(station_id, "constant_power_A", str(port_power))
			power_val_A = gridlabd.get_value(station_id, "constant_power_A")

			# Saving log information
			try:
				vals_log = (station_id, port_number, group_name, station_load, port_status, shed_state, port_load, allowed_power,
						port_power, recent_user, timedate, exception_flag)
				mycursor.execute(query_db_station_log, vals_log)
				mydb.commit()
				print('Succesfull values insertion in DB log')
			except Exception as e:
				print('db_log write error:')
				print('Error: ', e)

			try:
				vals_rt = (port_status, port_power, port_load, recent_user, arrival, timedate, station_id)
				mycursor.execute(query_update, vals_rt)
				mydb.commit()
				print('Successfull update: ', vals_rt)
			except Exception as e:
				print('db_rt update error:')
				print('Error: ', e)

	'''
	1 - Convert data from DB, after commit, to algorithm's inputs variables
	2 - Write algorithm as a module to be called in this function
	'''
	'''
	# num_EVs_charging - #current number of EVs plugged in at time t -> Get from "status" column in db_station_status_rt [number]
	# num_arr_current - #current number of arrivals at time t -> Get from "arrival" column in db_station_status_rt [number]
	# charger_occupy_array - #0 when empty, 1 when occupied, num_chargers x T array -> Get from "status" column in db_station_status_rt [array of chargers]
	charger_occupy_EVid - #-1 when empty, EVid when occupied, num_chargers x T array -> Get from "user_id" column in db_station_status_rt [array of chargers]
	EV_charger_assigned - #to which charger is the arrival assigned -> Get from "arrival" and "station_id" column in db_station_status_rt [array] 
	arrival_number - #maps the EV number to arrival number -> Get from "arrival" and "user id" column in db_station_status_rt 
	'''

	# num_arr_current = np.sum(query_select(mycursor, query_arrival_rt))
	# charger_occupy_array = query_select(mycursor, query_status_rt)
	# num_EV_charging = np.sum(charger_occupy_array)
	# charger_occupy_EVid = query_select(mycursor, query_evid_rt)



	# T is the number of timestamps (Nate's simulation is 15min [96 slots], GLD is 1min [1440 slots])
	T = 60*24



	return True



