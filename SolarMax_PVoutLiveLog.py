#!/usr/bin/python3
# -* coding: utf-8 *-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# SolarMax API Developed 2009-2010 by Bernd Wurst <bernd@schokokeks.org>
# for own use.
# Released to the public in 2012.

# Combined 2014 Matt Cordell <Solar@snoyowie.com>

# Reworked for MySQL Usage 2020 Dennis W. daylicron <https://github.com/daylicron>

import time
import sys
from SolarMax.solarmax import SolarMax  # API for talking to the SolarMax inverter
import MySQLdb


# Array of inverters in system. IP address and device number
# factory default is likely 192.168.1.123:12345 1
inverters = {'192.168.1.123': [1,]}
# If you have 3 inverters it works like this
# inverters = {'192.168.1.123': [1,2,3]}

# get pvoutput API details
apiDelay = 5  # time to delay after API calls
# API Key and SystemId must be entered as arguments for script.

smlist = []
for host in inverters.keys():
    sm = SolarMax(host, 12345)  # using port 12345
    sm.use_inverters(inverters[host])
    smlist.append(sm)
allinverters = []
for host in inverters.keys():
    allinverters.extend(inverters[host])

# cycle through the known inverters
count = 1
power_exp = [0] * (len(allinverters) + 1)
temp = [0] * (len(allinverters) + 1)
vdc = [0] * (len(allinverters) +1)
energy_exp = [0] * (len(allinverters) +1)

# Establish MySQL Connection
try:
  connection = MySQLdb.connect("localhost","db_user","db_password","db")
except:
  print("No Connection to MySQL Server. Check that MySQL is running and that the connection data are correct.")

for sm in smlist:
    for (no, ivdata) in sm.inverters().items():
        try:
          # Pass the parameters you wish to get from the inverter and log. Power, Voltage and Temp are all that's required for PVoutput.
          (inverter, current) = sm.query(no, ['PAC', 'KDY', 'KMT', 'KYR', 'KT0', 'TKK', 'UL1', 'IL1', 'UDC', 'IDC', 'SYS', 'SAL'])
          #use system date/Time for logging. Close enough
          #powerdate = time.strftime("%Y%m%d")
          powerdate = str(time.strftime("%d.%m.%Y"))
          powerTime = str(time.strftime("%H:%M:%S"))
          datetime = str(time.strftime("%Y-%m-%d %H:%M:%S"))

          # parse the results of sm.query above
          PowerGeneration = str(current['PAC'])
          EnergyToday = str(current['KDY'])
          EnergyMonth = str(current['KMT'])
          EnergyYear = str(current['KYR'])
          EnergyTotal = str(current['KT0'])
          Temperature = str(current['TKK'])
          Voltage = str(current['UL1'])
          Current = str(current['IL1'])

          (status, errors) = sm.status(count)
          number = str(no)

          # Write Data to MySQL Database
          cursor = connection.cursor()
          query = """INSERT INTO <table_name> (datum,nrwr,pac,tagesertrag,monatsertrag,jahresertrag,gesamtertrag,temperatur,udc1,idc1,status,fehler) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
          values = (datetime,number,PowerGeneration,EnergyToday,EnergyMonth,EnergyYear,EnergyTotal,Temperature,Voltage,Current,status,errors)

          cursor.execute(query,values)
          connection.commit() 
          cursor.close()

          count = count + 1      
        except:
          print('Communication Error, WR %i' % no)
          continue

if count <= len(allinverters):
  print('Not all inverters queried (%i < %i)' % (count, len(allinverters)))

print("Data succesfully queried and inserted into database.")
time.sleep(1)
