#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 26 17:47:54 2022

@author: caitlinferrie
"""

import smbus2 as smbus
import time
import math
import datetime
import json

# Get I2C bus
bus = smbus.SMBus(1)
# BMP280 address, 0x76(118)
# Read data back from 0x88(136), 24 bytes
import paho.mqtt.client as mqtt
client = mqtt.Client()
client.connect("broker.mqttdashboard.com",port=1883)


#global variables
health = False
big_dictionary = {}
warning_dict = {}
altitude_array = []
temp_array = []
pressure_array = []
alt_dict = {}
press_dict = {}
temp_dict = {}
changes_dict = {}
warnacc = 0

def Convert(lst):
    res_dct = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
    return res_dct

def on_message(client, userdata, message):
    global health
    health = int((message.payload).decode("utf-8"))
    print(health)
    print("Receivedmessage:{}on topic{}".format(message.payload, message.topic))
    #client.disconnect()
client.on_message = on_message

client.subscribe("IC.embedded/symbioticback/#")

""" 
start of Caitlins code -> WARNINGS

FUNCTION TO GENERATE WARNINGS: """

def warnings(alt, temp, press):
    global warnacc
    if (warnacc %  60) == 0: #Infinite loop
        print("we are going in")
        if(health):
            ill_warn_altitude(alt)
            ill_warn_pressure(press)
            ill_warn_temp(temp)
            print("ill")
        else:
            warn_altitude(alt)
            warn_pressure(press)
            warn_temp(temp)
            print("not ill")
    warnacc = warnacc + 1
        #time.sleep(900) #Wait 900s (15 mins)
    
def warn_temp(temp):
    if(temp < 10):
        client.publish("IC.embedded/symbiotic/warning/temp","Warning: air temperature is low (" + str(temp) + "C). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="Low Air Temperature ("+str(temp)+" C)"
    if(temp > 30):
        client.publish("IC.embedded/symbiotic/warning/temp","Warning: air temperature is high (" + str(temp) + "C). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="High Air Temperature ("+str(temp)+" C)"
    if(temp > 5 and temp <25):
        client.publish("IC.embedded/symbiotic/warning/no","Air temperature is at a safe level (" + str(temp) + "C)")
        
def ill_warn_temp(temp):
    if(temp < 10):
        client.publish("IC.embedded/symbiotic/warning/temp","Warning: air temperature is low (" + str(temp) + "C). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="Low Air Temperature ("+str(temp)+" C)"
    if(temp > 25):
        client.publish("IC.embedded/symbiotic/warning/temp","Warning: air temperature is high (" + str(temp) + "C). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="High Air Temperature ("+str(temp)+" C)"
    if(temp > 5 and temp <25):
        client.publish("IC.embedded/symbiotic/warning/no","Air temperature is at a safe level (" + str(temp) + "C)")
    
def warn_pressure(pressure):
    if(pressure < 700):
        client.publish("IC.embedded/symbiotic/warning/pres","Warning: air pressure is low (" + str(pressure) + "hPa). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="Low Air Pressure ("+str(pressure)+" kPa)"
    else:
        client.publish("IC.embedded/symbiotic/warning/no","Air pressure is at a safe level (" + str(pressure) + "hPa)")
        
def ill_warn_pressure(pressure):
    if(pressure < 850):
        client.publish("IC.embedded/symbiotic/warning/pres","Warning: air pressure is low (" + str(pressure) + "hPa). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="Low Air Pressure ("+str(pressure)+" Pa)"
    else:
        client.publish("IC.embedded/symbiotic/warning/no","Air pressure is at a safe level (" + str(pressure) + "hPa)")
        
def warn_altitude(altitude):
    if(altitude >= 2000):
        client.publish("IC.embedded/symbiotic/warning/alt","Warning: altitude is high (" + str(altitude) + "m). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="High Altitude ("+str(altitude)+" m)"
    else:
        client.publish("IC.embedded/symbiotic/warning/no","Altitude is at a safe level (" + str(alt) + "m)")

def ill_warn_altitude(altitude):
    if(altitude >= 1500):
        client.publish("IC.embedded/symbiotic/warning/alt","Warning: altitude is high (" + str(altitude) + "m). Exposure in these conditions for extended periods of time can be dangerous")
        warning_dict[str(datetime.datetime.now())]="High Altitude ("+str(altitude)+" m)"
    else:
        client.publish("IC.embedded/symbiotic/warning/no","Altitude is at a safe level (" + str(alt) + "m)")

""" END OF CODE ABOUT WARNINGS

START OF CODE ABOUT CHANGES OVER TIME """    

def changes(alt, press, temp):
    
    import time
    if (warnacc %  60) == 0: #Infinite loop
        print("we are going in")
    
        alt_dict[str(datetime.datetime.now())] = alt
        temp_dict[str(datetime.datetime.now())] = temp
        press_dict[str(datetime.datetime.now())] = press
    
        fill_arrays(altitude_array, alt_dict, temp_array, temp_dict, pressure_array, press_dict)
        fifteen_mins(altitude_array, temp_array, pressure_array)
        one_hr(altitude_array, temp_array, pressure_array)
        six_hr(altitude_array, temp_array, pressure_array)
        twelve_hr(altitude_array, temp_array, pressure_array)
        twenty_four_hr(altitude_array, temp_array, pressure_array)
        fourty_eight_hr(altitude_array, temp_array, pressure_array)
        
        #time.sleep(900) #Wait 900s (15 mins)
    
#tested + works
def fill_arrays(altitude_array, alt_dict, temp_array, temp_dict, pressure_array, press_dict):
    
    changes_dict.clear()
    
    for time in alt_dict:
       altitude_array.append(alt_dict[time]) 
    
    for time in temp_dict:
       temp_array.append(temp_dict[time])
       
    for time in press_dict:
        pressure_array.append(press_dict[time])
        
    changes_dict["time"]=str(datetime.datetime.now())
    
#tested + works
def fifteen_mins(altitude_array, temp_array, pressure_array):
  # most recent - 2nd most recent - > if number of entries <2 do not calculate
  
  change_altitude_15m = 0         
  change_pressure_15m = 0
  change_temp_15m = 0
  
  if(len(altitude_array)>1):
      
      change_altitude_15m = altitude_array[-1] - altitude_array[-2]
      client.publish("IC.embedded/symbiotic/changes","Altitude change in the past 15 minutes is " + str(change_altitude_15m) + " m")
      changes_dict["Altitude change in the past 15 minutes is "] = change_altitude_15m
      
      change_temp_15m = temp_array[-1] - temp_array[-2]
      client.publish("IC.embedded/symbiotic/changes","Temperature change in the past 15 minutes is " + str(change_temp_15m) + " C")
      changes_dict["Temperature change in the past 15 minutes is "] = change_temp_15m
      
      change_pressure_15m = pressure_array[-1] - pressure_array[-2]
      client.publish("IC.embedded/symbiotic/changes","Pressure change in the past 15 minutes is " + str(change_pressure_15m) + " hPa")
      changes_dict["Pressure change in the past 15 minutes is "] = change_pressure_15m
      
  else:
      
      client.publish("IC.embedded/symbiotic/changes","Not enough readings to calculate differences over the past 15 minutes")
      changes_dict["Changes in the past 15 minutes are "] = "Not Available (Not enough Readings)"
 
#tested + works    
def one_hr(altitude_array, temp_array, pressure_array):
  # most recent - 4th most recent-> if number of entries <4 do not calculate
  
  change_altitude_1h = 0         
  change_pressure_1h = 0
  change_temp_1h = 0
  
  if(len(altitude_array)>4):
      
      change_altitude_1h = altitude_array[-1] - altitude_array[-5]
      client.publish("IC.embedded/symbiotic/changes","Altitude change in the past 1 hour is " + str(change_altitude_1h) + " m")
      changes_dict["Altitude change in the past 1 hour is "] = change_altitude_1h
      
      change_temp_1h = temp_array[-1] - temp_array[-5]
      client.publish("IC.embedded/symbiotic/changes","Temperature change in the past 1 hour is " + str(change_temp_1h) + " C")
      changes_dict["Temperature change in the past 1 hour is "] = change_temp_1h
      
      change_pressure_1h = pressure_array[-1] - pressure_array[-5]
      client.publish("IC.embedded/symbiotic/changes","Pressure change in the past 1 hour is " + str(change_pressure_1h) + " hPa")
      changes_dict["Pressure change in the past 1 hour is "] = change_pressure_1h
      
  else:
      
      client.publish("IC.embedded/symbiotic/changes","Not enough readings to calculate differences over the past 1 hour")
      changes_dict["Changes in the past 1 hour are "] = "Not Available (Not enough Readings)"
  
 #tested + works   
def six_hr(altitude_array, temp_array, pressure_array):
  # most recent - 24th most recent -> if number of entries <24 do not calculate
  
  change_altitude_6h = 0          
  change_pressure_6h = 0
  change_temp_6h = 0
  
  if(len(altitude_array)>24):
      
      change_altitude_6h = altitude_array[-1] - altitude_array[-25]
      client.publish("IC.embedded/symbiotic/changes","Altitude change in the past 6 hours is " + str(change_altitude_6h) + " m")
      changes_dict["Altitude change in the past 6 hours is "] = change_altitude_6h
      
      change_temp_6h = temp_array[-1] - temp_array[-25]
      client.publish("IC.embedded/symbiotic/changes","Temperature change in the past 6 hours is " + str(change_temp_6h) + " C")
      changes_dict["Temperature change in the past 6 hours is "] = change_temp_6h
      
      change_pressure_6h = pressure_array[-1] - pressure_array[-25]
      client.publish("IC.embedded/symbiotic/changes","Pressure change in the past 6 hours is " + str(change_pressure_6h) + " hPa")
      changes_dict["Pressure change in the past 6 hours is "] = change_pressure_6h
      
  else:
      
      client.publish("IC.embedded/symbiotic/changes","Not enough readings to calculate differences over the past 6 hours")
      changes_dict["Changes in the past 6 hours are "] = "Not Available (Not enough Readings)"
  
 #tested + works   
def twelve_hr(altitude_array, temp_array, pressure_array):
  # most recent - 48th most recent -> if number of entries <48 do not calculate 
  
  change_altitude_12h = 0         
  change_pressure_12h = 0
  change_temp_12h = 0
  
  if(len(altitude_array)>48):
      
      change_altitude_12h = altitude_array[-1] - altitude_array[-49]
      client.publish("IC.embedded/symbiotic/changes","Altitude change in the past 12 hours is " + str(change_altitude_12h) + " m")
      changes_dict["Altitude change in the past 12 hours is "] = change_altitude_12h
      
      change_temp_12h = temp_array[-1] - temp_array[-49]
      client.publish("IC.embedded/symbiotic/changes","Temperature change in the past 12 hours is " + str(change_temp_12h) + " C")
      changes_dict["Temperature change in the past 12 hours is "] = change_temp_12h
      
      change_pressure_12h = pressure_array[-1] - pressure_array[-49]
      client.publish("IC.embedded/symbiotic/changes","Pressure change in the past 12 hours is " + str(change_pressure_12h) + " hPa")
      changes_dict["Pressure change in the past 12 hours is "] = change_pressure_12h
      
  else:
      
      client.publish("IC.embedded/symbiotic/changes","Not enough readings to calculate differences over the past 12 hours")
      changes_dict["Changes in the past 12 hours are "] = "Not Available (Not enough Readings)"
  
#tested + works
def twenty_four_hr(altitude_array, temp_array, pressure_array):
  # most recent - 96th most recent -> if number of entries <96 do not calculate 
  
  change_altitude_24h = 0         
  change_pressure_24h = 0
  change_temp_24h = 0
  
  if(len(altitude_array)>96):
      
      change_altitude_24h = altitude_array[-1] - altitude_array[-97]
      client.publish("IC.embedded/symbiotic/changes","Altitude change in the past 24 hours is " + str(change_altitude_24h) + " m")
      changes_dict["Altitude change in the past 24 hours is "] = change_altitude_24h
      
      change_temp_24h = temp_array[-1] - temp_array[-97]
      client.publish("IC.embedded/symbiotic/changes","Temperature change in the past 24 hours is " + str(change_temp_24h) + " C")
      changes_dict["Temperature change in the past 24 hours is "] = change_temp_24h
      
      change_pressure_24h = pressure_array[-1] - pressure_array[-97]
      client.publish("IC.embedded/symbiotic/changes","Pressure change in the past 24 hours is " + str(change_pressure_24h) + " hPa")
      changes_dict["Pressure change in the past 24 hours is "] = change_pressure_24h
      
  else:
      
      client.publish("IC.embedded/symbiotic/changes","Not enough readings to calculate differences over the past 24 hours")
      changes_dict["Changes in the past 24 hours are "] = "Not Available (Not enough Readings)"
  
 #tested + works   
def fourty_eight_hr(altitude_array, temp_array, pressure_array):
  # most recent - 192nd most recent -> if number of entries <192 do not calculate
  
  change_altitude_48h = 0         
  change_pressure_48h = 0
  change_temp_48h = 0
  
  if(len(altitude_array)>192):
      
      change_altitude_48h = altitude_array[-1] - altitude_array[-193]
      client.publish("IC.embedded/symbiotic/changes","Altitude change in the past 48 hours is " + str(change_altitude_48h) + " m")
      changes_dict["Altitude change in the past 48 hours is "] = change_altitude_48h
      
      change_temp_48h = temp_array[-1] - temp_array[-193]
      client.publish("IC.embedded/symbiotic/changes","Temperature change in the past 48 hours is " + str(change_temp_48h) + " C")
      changes_dict["Temperature change in the past 48 hours is "] = change_temp_48h
      
      change_pressure_48h = pressure_array[-1] - pressure_array[-193]
      client.publish("IC.embedded/symbiotic/changes","Pressure change in the past 48 hours is " + str(change_pressure_48h) + " hPa")
      changes_dict["Pressure change in the past 48 hours is "] = change_pressure_48h
      
  else:
      
      client.publish("IC.embedded/symbiotic/changes","Not enough readings to calculate differences over the past 48 hours")
      changes_dict["Changes in the past 48 hours are "] = "Not Available (Not enough Readings)"
      
def reset(altitude_array, temp_array, pressure_array):
    
    altitude_array.clear()
    temp_array.clear()
    pressure_array.clear()
  
""" END OF CODE ABOUT CHANGES 
    End of Caitlin's code """ 

#converting list of variables to dict
#def Convert(lst):
#    res_dct = {a: b for a,b in lst}
#    return res_dct

# reading in sensor data
while True:
    client.loop()
    print(health)
    b1 = bus.read_i2c_block_data(0x76, 0x88, 24)
    # Convert the data
    # Temp coefficents
    dig_T1 = b1[1] * 256 + b1[0]
    dig_T2 = b1[3] * 256 + b1[2]
    if dig_T2 > 32767 :
        dig_T2 -= 65536
    dig_T3 = b1[5] * 256 + b1[4]
    if dig_T3 > 32767 :
        dig_T3 -= 65536
    # Pressure coefficents
    dig_P1 = b1[7] * 256 + b1[6]
    dig_P2 = b1[9] * 256 + b1[8]
    if dig_P2 > 32767 :
        dig_P2 -= 65536
    dig_P3 = b1[11] * 256 + b1[10]
    if dig_P3 > 32767 :
        dig_P3 -= 65536
    dig_P4 = b1[13] * 256 + b1[12]
    if dig_P4 > 32767 :
        dig_P4 -= 65536
    dig_P5 = b1[15] * 256 + b1[14]
    if dig_P5 > 32767 :
        dig_P5 -= 65536
    dig_P6 = b1[17] * 256 + b1[16]
    if dig_P6 > 32767 :
        dig_P6 -= 65536
    dig_P7 = b1[19] * 256 + b1[18]
    if dig_P7 > 32767 :
        dig_P7 -= 65536
    dig_P8 = b1[21] * 256 + b1[20]
    if dig_P8 > 32767 :
        dig_P8 -= 65536
    dig_P9 = b1[23] * 256 + b1[22]
    if dig_P9 > 32767 :
        dig_P9 -= 65536
    # BMP280 address, 0x76(118)
    # Select Control measurement register, 0xF4(244)
    # 0x27(39) Pressure and Temperature Oversampling rate = 1
    # Normal mode
    bus.write_byte_data(0x76, 0xF4, 0x27)
    # BMP280 address, 0x76(118)
    # Select Configuration register, 0xF5(245)
    # 0xA0(00) Stand_by time = 1000 ms
    bus.write_byte_data(0x76, 0xF5, 0xA0)
    time.sleep(0.5)
    # BMP280 address, 0x76(118)
    # Read data back from 0xF7(247), 8 bytes
    # Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
    # Temperature xLSB, Humidity MSB, Humidity LSB
    data = bus.read_i2c_block_data(0x76, 0xF7, 8)
    # Convert pressure and temperature data to 19-bits
    adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
    adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
    # Temperature offset calculations
    var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
    var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
    t_fine = (var1 + var2)
    cTemp = (var1 + var2) / 5120.0
    fTemp = cTemp * 1.8 + 32
    # Pressure offset calculations
    var1 = (t_fine / 2.0) - 64000.0
    var2 = var1 * var1 * (dig_P6) / 32768.0
    var2 = var2 + var1 * (dig_P5) * 2.0
    var2 = (var2 / 4.0) + ((dig_P4) * 65536.0)
    var1 = ((dig_P3) * var1 * var1 / 524288.0 + ( dig_P2) * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * (dig_P1)
    p = 1048576.0 - adc_p
    p = (p - (var2 / 4096.0)) * 6250.0 / var1
    var1 = (dig_P9) * p * p / 2147483648.0
    var2 = p * (dig_P8) / 32768.0
    pressure = (p + (var1 + var2 + (dig_P7)) / 16.0) / 100
    # Output data to screen
    print("Temperature in Celsius : %.2f C" %cTemp)
    print("Temperature in Fahrenheit : %.2f F" %fTemp)
    print("Pressure : %.2f hPa" %pressure)
    config = [0x00, 0x5C, 0x00]
    bus.write_i2c_block_data(0x0C, 0x60, config)# Read data back, 1 byte# Status byte
    data = bus.read_byte(0x0C)# MLX90393 address, 0x0C(12)# Select write register command, 0x60(96)# AH = 0x02, AL = 0xB4, RES for magnetic measurement = 0, Address register (0x02 << 2)
    config = [0x02, 0xB4, 0x08]
    bus.write_i2c_block_data(0x0C, 0x60, config)# Read data back, 1 byte# Status byte
    data = bus.read_byte(0x0C)# MLX90393 address, 0x0C(12)# Start single meaurement mode, X, Y, Z-Axis enabled
    bus.write_byte(0x0C, 0x3E)# Read data back, 1 byte# Status byte
    data = bus.read_byte(0x0C)
    time.sleep(0.5)# MLX90393 address, 0x0C(12)# Read data back from 0x4E(78), 7 bytes# Status, xMag msb, xMag lsb, yMag msb, yMag lsb, zMag msb, zMag lsb
    data = bus.read_i2c_block_data(0x0C, 0x4E, 7)# Convert the data
    xMag = data[1] * 256 + data[2]
    if xMag > 32767 :
        xMag -= 65536
    yMag = data[3] * 256 + data[4]
    if yMag > 32767 :
        yMag -= 65536
    zMag = data[5] * 256 + data[6]
    if zMag > 32767 :
        zMag -= 65536# Output data to screen
    print("Magnetic Field in X-Axis : %d" %xMag)
    print("Magnetic Field in Y-Axis : %d" %yMag)
    print("Magnetic Field in Z-Axis : %d" %zMag)
    #time.sleep(20)

    #lists
    data_lst = []
    
        
    alt = (44330*(1-math.pow((pressure/1013.25),(1/5.255)))) + 108

    temp = cTemp

    press = pressure

    bearings = math.acos(zMag/(math.sqrt(math.pow(xMag,2)+math.pow(yMag,2)+math.pow(zMag,2))))
    
    data_lst.extend(('time', str(datetime.datetime.now()), 'altitude', alt, 'temperature', temp, 'pressure', press, 'bearings', bearings))
    
    res_dct = Convert(data_lst)
    big_dictionary = res_dct

    warnings(alt, temp, press)
    changes(alt, press, temp)

    json_str = json.dumps(big_dictionary)
    client.publish("IC.embedded/symbiotic/data",json_str)
    print(json_str)
    time.sleep(4)
    

    

