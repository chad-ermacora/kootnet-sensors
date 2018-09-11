'''
    KootNet Sensors is a collection of programs and scripts to deploy,
    interact with, and collect readings from various Sensors.  
    Copyright (C) 2018  Chad Ermacora  chad.ermacora@gmail.com  

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import sqlite3, socket
from envirophat import motion
from time import sleep

sensorDB_Location = '/home/sensors/data/SensorTriggerDatabase.sqlite'
var_motion_variance = 0.045
sleep(10)


def database_write(wvar_motion):
    var1 = float(wvar_motion[0])
    var2 = float(wvar_motion[1])
    var3 = float(wvar_motion[2])
    var_host = str(socket.gethostname())
    testIP = ""
    print(str(var1))
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("192.168.10.1", 80))
        testIP = (s.getsockname()[0])
        s.close()
    except BaseException:
        testIP = "0.0.0.0"
        
    testIP = str(testIP)
    conn = sqlite3.connect(sensorDB_Location)
    c = conn.cursor()
    print("x: " + str(var1))
    print("y: " + str(var2))
    print("z: " + str(var3))
    c.execute("INSERT OR IGNORE INTO Motion_Data (Time,IP, X, Y, Z, hostName) VALUES ((CURRENT_TIMESTAMP),?,?,?,?,?)",(testIP,var1,var2,var3,var_host))
    conn.commit()
    c.close()
    conn.close()

conn = sqlite3.connect(sensorDB_Location)
c = conn.cursor()
try:
    c.execute('CREATE TABLE {tn} ({nf} {ft})'\
        .format(tn='Motion_Data', nf='Time', ft='TEXT'))
    print("Table Created")
except:
    print("Table Already Created")

try:
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn='Motion_Data', cn='IP', ct='TEXT'))
except:
    print("Column Already Created")

try:
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
            .format(tn='Motion_Data', cn='X', ct='BLOB'))
except:
    print("Column Already Created")

try:
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn='Motion_Data', cn='Y', ct='BLOB'))
except:
    print("Column Already Created")

try:
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn='Motion_Data', cn='Z', ct='BLOB'))
except:
    print("Column Already Created")

try:
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
        .format(tn='Motion_Data', cn='hostName', ct='TEXT'))
except:
    print("Column Already Created")

c.close()
conn.close()

var_real = motion.accelerometer()
database_write(var_real)
var_motion_last1 = round(float(var_real[0]),3)
var_motion_last2 = round(float(var_real[1]),3)
var_motion_last3 = round(float(var_real[2]),3)

while True:
    sleep(0.25)
    var_real = motion.accelerometer()
    var_motion_now1 = round(float(var_real[0]),3)
    var_motion_now2 = round(float(var_real[1]),3)
    var_motion_now3 = round(float(var_real[2]),3)

#    print("now1: " + str(var_motion_now1))
#    print("now2: " + str(var_motion_now2))
#    print("now3: " + str(var_motion_now3))
    
    if var_motion_last1 > (var_motion_now1 + var_motion_variance):
        database_write(var_real)
    elif var_motion_last1 < (var_motion_now1 - var_motion_variance):
        database_write(var_real)
    elif var_motion_last2 > (var_motion_now2 + var_motion_variance):
        database_write(var_real)
    elif var_motion_last2 < (var_motion_now2 - var_motion_variance):
        database_write(var_real)
    elif var_motion_last3 > (var_motion_now3 + var_motion_variance):
        database_write(var_real)
    elif var_motion_last3 < (var_motion_now3 - var_motion_variance):
        database_write(var_real)

    var_motion_last1 = var_motion_now1
    var_motion_last2 = var_motion_now2
    var_motion_last3 = var_motion_now3
        
c.close()
conn.close()