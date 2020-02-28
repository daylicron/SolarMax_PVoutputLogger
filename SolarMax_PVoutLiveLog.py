#!/usr/bin/python
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

import time
import sys
from SolarMax.solarmax import SolarMax  # API for talking to the SolarMax inverter
import MySQLdb


# Array of inverters in system. IP address and device number
# factory default is likely 192.168.1.123:12345 1
inverters = {'INVETER-IP': [1,2,3 ]}

# Set Language for Status Output
lang = "de"

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
  connection = MySQLdb.connect("localhost","DB-USER","DB-USER-PASSWORD","DB")
except:
  print "No Connection to MySQL Server. Check that MySQL is running and that the connection data are correct."

for sm in smlist:
    for (no, ivdata) in sm.inverters().iteritems():
        #try:
            # Pass the parameters you wish to get from the inverter and log. Power, Voltage and Temp are all that's required for PVoutput.
            (inverter, current) = sm.query(no, ['PAC', 'KDY', 'KMT', 'KYR', 'KT0', 'TKK', 'UL1', 'IL1', 'UDC', 'IDC', 'SYS', 'SAL'])


            #use system date/Time for logging. Close enough
            #powerdate = time.strftime("%Y%m%d")
            powerdate = str(time.strftime("%d.%m.%Y"))
            powerTime = str(time.strftime("%H:%M:%S"))
	        datetime = str(time.strftime("%Y-%m-%d %H:%M:%S"))
            #datetime = "2018-10-14 14:58:55"
            # parse the results of sm.query above
            #PowerGeneration = str(current['PAC'])
            PowerGeneration = "3010"
            EnergyToday = str(current['KDY'])
            EnergyMonth = str(current['KMT'])
            EnergyYear = str(current['KYR'])
            EnergyTotal = str(current['KT0'])
            Temperature = str(current['TKK'])
            Voltage = str(current['UL1'])
            Current = str(current['IL1'])
            #(Status, Errors) = sm.status(no, lang)
            Status = "Netzbetrieb"
            Errors = "None"
	    number = str(no)

            print "Date: " + datetime + " W: " + PowerGeneration + " Energy_Today: " + EnergyToday + " Energy_Month: " + EnergyMonth + " Energy_Year: " + EnergyYear
            print " Energy_Total: " + EnergyTotal + " Temp: " + Temperature + " Volt: " + Voltage + " Ampere: " + Current + " Status: " + Status + " Status_Error: " + Errors

	    # Write Data to MySQL Database
	    cursor = connection.cursor()
	    query = """INSERT INTO imported (Datum,NrWR,PAC,Tagesertrag,Monatsertrag,Gesamtertrag,Temperatur,UDC1,IDC1,Status,Fehler) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, "Status", "Errors")"""
	    values = (datetime,number,PowerGeneration,EnergyToday,EnergyMonth,EnergyYear,EnergyTotal,Temperature,Voltage,Current)

	    

	    #sql = "INSERT INTO imported (Datum,NrWR,PAC,Tagesertrag,Monatsertrag,Gesamtertrag,Temperatur,UDC1,IDC1,Status,Fehler) VALUES(datetime,no,PowerGeneration,EnergyToday,EnergyMonth,EnergyYear,EnergyTotal,Temperature,Voltage,Current,Status,Errors)"
	    number_of_rows = cursor.execute(query, values)
	    connection.commit() 
	    cursor.close()

	    print "SQL Insert: " + number_of_rows 
            count = count + 1      
        #except:
            print 'Communication Error, WR %i' % no
            continue
#(status, errors) = sm.status(count)

#if errors:
#    print('WR %i: %s (%s)' % (no, status, errors))
#    try:
#        print("details: ", int(PAC), int(TEMP), int(VOLTAGE))
#    except:
#        pass

#if count <= len(allinverters):
#    print 'Not all inverters queried (%i < %i)' % (count, len(allinverters))

print "Data Succesfully query and inserted into database."
time.sleep(1)
