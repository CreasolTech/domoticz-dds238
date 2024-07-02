#!/usr/bin/env python
"""
domoticz-dds238 energy meter plugin for Domoticz.
Works with single-phase DDS238-1 ZN/S, DDS238-2 ZN/S (Modbus version)
Author: Paolo Subiaco https://github.com/CreasolTech

Requirements:
    1.python module minimalmodbus -> http://minimalmodbus.readthedocs.io/en/master/
        (pi@raspberrypi:~$ sudo pip3 install minimalmodbus)
    2.USB to RS485 adapter/converter 
    3.Domoticz 2022.1 or later

Words to translate in other languages (in double quotes):
English (en)            Italian (it)                    YourLanguage (??)
"Power/Energy total"    "Potenza/Energia totale         ""
"Power/Energy imported" "Potenza/Energia importata"     ""
"Power/Energy exported" "Potenza/Energia esportata"     ""
"Voltage"               "Tensione"                      ""
"Current"               "Corrente"                      ""
"Frequency"             "Frequenza"                     ""
"Power Factor"          "Fattore di Potenza"            ""

"""

"""
<plugin key="dds238" name="DDS238 ZN/S energy meters, connected by serial port"  version="2.0" author="CreasolTech" externallink="https://github.com/CreasolTech/domoticz-dds238">
    <description>
        <h2>Domoticz plugin for DDS238 ZN/S energy meters (with Modbus port) - Version 2.0 </h2>
        <b>More than one meter can be connected to the same bus</b>, specifying their addresses separated by comma, for example <tt>2,3,124</tt>  to read energy meters with slave address 1, 2, 3, 124.<br/><u>DO NOT CHANGE THE EXISTING SEQUENCE</u> by adding new devices between inside, but just add new device in the end of the sequence, e.g. <tt>2,3,124,6,4,5</tt><br/>
        It's possible to reprogram a meter slave address by editing the corresponding Power Factor device Description field, changing ADDR=x to ADDR=y (y between 1 and 247), then clicking on Update button<br/>
        When the first meter is connected, <b>it's strongly recommended to immediately change default address from 1 to 2 (or more)</b> to permit, in the future, to add new meters.<br/>
        For more info please check the  <a href="https://github.com/CreasolTech/domoticz-dds238">GitHub plugin page</a>
    </description>
    <params>
        <param field="SerialPort" label="Modbus Port" width="200px" required="true" default="/dev/ttyUSB0" />
        <param field="Mode1" label="Baud rate" width="40px" required="true" default="9600"  />
        <param field="Mode3" label="Poll interval">
            <options>
                <option label="2 seconds" value="2" />
                <option label="3 seconds" value="3" />
                <option label="4 seconds" value="4" />
                <option label="5 seconds" value="5" default="true" />
                <option label="10 seconds" value="10" />
                <option label="20 seconds" value="20" />
                <option label="30 seconds" value="30" />
            </options>
        </param>
        <param field="Mode2" label="Meter addresses" width="40px" required="true" default="2,3,4" />
    </params>
</plugin>

"""

import minimalmodbus    #v2.1.1
import random
import DomoticzEx as Domoticz     



LANGS=[ "en", "it" ] # list of supported languages, in DEVS dict below
DEVTYPE=0
DEVSUBTYPE=1
DEVSWITCHTYPE=2
DEVOPTIONS=3
DEVIMAGE=4
DEVLANG=5  # item in the DEVS list where the first language starts 

DEVS={ #unit:     Type,Sub,swtype, Options, Image,  "en name", "it name"  ...other languages should follow  ],
            1:  [ 243,29,0,     None,       None,   "Power/Energy total",   "Potenza/Energia totale"   ],
            2:  [ 243,29,0,     None,       None,   "Power/Energy imported","Potenza/Energia importata"   ],
            3:  [ 243,29,0,     None,       None,   "Power/Energy exported","Potenza/Energia esportata"   ],
            4:  [ 243,8,0,      None,       None,   "Voltage",          "Tensione"      ],
            5:  [ 243,23,0,     None,       None,   "Current",          "Corrente"      ],
            6:  [ 243,31,0,     {'Custom': '1;Hz'}, None,   "Frequency","Frequenza"     ],
            7:  [ 243,31,0,     None,       None,   "Power Factor",     "Fattore di Potenza"   ],
            8:  [ 243,29,0,     None,       None,   "Power/Energy net",   "Potenza/Energia netta"   ],
            # ToDo: add relay device?
}

DEVSMAX=10;
DEVICEIDPREFIX="DDS238"

class BasePlugin:
    def __init__(self):
        self.rs485 = ""
        self.slaves = [1]
        self.prefix = ""
        return

    def modbusInit(self, slave):
        self.rs485 = minimalmodbus.Instrument(Parameters["SerialPort"], int(slave))
        self.rs485.serial.baudrate = Parameters["Mode1"]
        self.rs485.serial.bytesize = 8
        self.rs485.serial.parity = minimalmodbus.serial.PARITY_NONE
        self.rs485.serial.stopbits = 1
        self.rs485.serial.timeout = 0.5
        self.rs485.serial.exclusive = True 
        self.rs485.debug = True
        self.rs485.mode = minimalmodbus.MODE_RTU
        self.rs485.close_port_after_each_call = True

    def onStart(self):
        Domoticz.Log("Starting DDS238 plugin")
        self.pollTime=30 if Parameters['Mode3']=="" else int(Parameters['Mode3'])
        self.heartbeatNow=self.pollTime     # this is used to increase heartbeat in case of collisions
        Domoticz.Heartbeat(self.pollTime)
        self.runInterval = 1
        self.prefix = f"{DEVICEIDPREFIX}_{Parameters['HardwareID']}"
        self._lang=Settings["Language"]
        # check if language set in domoticz exists
        if self._lang in LANGS:
            self.lang=DEVLANG+LANGS.index(self._lang)
        else:
            Domoticz.Error(f"Language {self._lang} does not exist in dict DEVS, inside the domoticz-emmeti-mirai plugin, but you can contribute adding it ;-) Thanks!")
            self._lang="en"
            self.lang=DEVLANG # default: english text

        for ss in Parameters["Mode2"].split(','):
            s=int(ss)
            if s>=2 and s<=247:
                self.slaves.append(s)

        # Check that device used to change default address for slave=1 exists
        devID=f"{self.prefix}_1"
        if devID not in Devices or 7 not in Devices[devID].Units:
            Domoticz.Log("Create virtual device to change DDS238 address for meters with default address=1")
            Domoticz.Unit(DeviceID=devID, Name="Change address 1 -> 2-247", Description=f"Meter Addr=1, ADDR=1", Unit=7, Type=243, Subtype=19, Used=1).Create()
        # Check that all devices exist, or create them
        for slave in self.slaves:
            if slave>1 and slave<=247:  # DeviceID=slave address, Unit=1..8
                devID=f"{self.prefix}_{slave}"
                for i in DEVS:
                    unit=i
                    if devID not in Devices or unit not in Devices[devID].Units:
                        Options=DEVS[i][DEVOPTIONS] if DEVS[i][DEVOPTIONS] else {}
                        Image=DEVS[i][DEVIMAGE] if DEVS[i][DEVIMAGE] else 0
                        Description=""
                        if i==1:
                            Description=f"Meter Addr={slave}, Total power = imported + exported"
                        elif i==7:
                            Description=f"Meter Addr={slave}, Power Factor, ADDR={slave}"
                        elif i==8:
                            Description=f"Meter Addr={slave}, Net power = imported - exported"
                        else:
                            Description=f"Meter Addr={slave}"
                        Domoticz.Log(f"Creating device DeviceID={devID}, Name='{DEVS[i][self.lang]}', Description='{Description}', Unit={unit}, Type={DEVS[i][DEVTYPE]}, Subtype={DEVS[i][DEVSUBTYPE]}, Switchtype={DEVS[i][DEVSWITCHTYPE]}, Options={Options}, Image={Image}")
                        Domoticz.Unit(DeviceID=devID, Name=DEVS[i][self.lang], Description=Description, Unit=unit, Type=DEVS[i][DEVTYPE], Subtype=DEVS[i][DEVSUBTYPE], Switchtype=DEVS[i][DEVSWITCHTYPE], Options=Options, Image=Image, Used=1).Create()
                s+=DEVSMAX


    def onStop(self):
        Domoticz.Log("Stopping DDS238 plugin")

    def onHeartbeat(self):
        for slave in self.slaves:
            # read all registers in one shot
            if slave>1 and slave<=247:
                try:
                    self.modbusInit(slave)
                    # Read data from energy meter
                    registerEnergy=self.rs485.read_registers(0, 2, 3) # Read  registers from 0 to 8, using function code 3
                    register=self.rs485.read_registers(8, 10, 3) # Read  registers from 8 to 0x11, using function code 3
                    self.rs485.serial.close()  #  Close that door !
                except:
                    Domoticz.Error(f"Error reading Modbus registers from device {slave}")
                    self.heartbeatNow+=random.randint(1,5)    # manage collisions, increasing heartbeat once
                    Domoticz.Heartbeat(self.heartbeatNow)
                else:
                    if self.heartbeatNow!=self.pollTime:
                        self.heartbeatNow=self.pollTime     # restore normal heartbeat time, as defined in the plugin configuration
                        Domoticz.Heartbeat(self.heartbeatNow)
                    voltage=register[4]/10                          # V
                    current=register[5]/100                         # A
                    power=register[6]                               # W signed
                    if (power>=32768):
                        power=power-65536
                        powerImp=0
                        powerExp=0-power
                    else:
                        powerImp=power
                        powerExp=0
                    energy=(registerEnergy[1] + (registerEnergy[0]<<16))*10 # Wh
                    energyImp=(register[3] + (register[2]<<16))*10     # Wh
                    energyExp=(register[1] + (register[0]<<16))*10     # Wh
                    energyNet=energyImp-energyExp
                    frequency=register[9]/100                       # Hz
                    pf=register[8]/10                               # %

                    Domoticz.Status(f"Slave={slave}, P={power}W E={energy/1000}kWh Imp={energyImp/1000}kWh Exp={energyExp/1000}kWh V={voltage}V I={current}A, f={frequency}Hz PF={pf}%")
                    devID=f"{self.prefix}_{slave}"
                    Devices[devID].Units[1].sValue=f"{power};{energy}"
                    Devices[devID].Units[1].Update()
                    Devices[devID].Units[2].sValue=f"{powerImp};{energyImp}"      # imported power/energy
                    Devices[devID].Units[2].Update()
                    Devices[devID].Units[3].sValue=f"{powerExp};{energyExp}"      # exported power/energy
                    Devices[devID].Units[3].Update()
                    Devices[devID].Units[4].sValue=str(voltage)
                    Devices[devID].Units[4].Update()
                    Devices[devID].Units[5].sValue=str(current)
                    Devices[devID].Units[5].Update()
                    Devices[devID].Units[6].sValue=str(frequency)
                    Devices[devID].Units[6].Update()
                    Devices[devID].Units[7].sValue=str(pf)
                    Devices[devID].Units[7].Update()
                    Devices[devID].Units[8].sValue=f"{power};{energyNet}"      # Net energy = imported energy - exported energy.  power=signed energy (negative if exported)
                    Devices[devID].Units[8].Update()

    def onCommand(self, DeviceID, Unit, Command, Level, Color):
        Domoticz.Status(f"Command for {Devices[Unit].Name}: Unit={Unit}, Command={Command}, Level={Level}")

    def onDeviceModified(self, DeviceID, Unit): #called when device is modified by the domoticz frontend (e.g. when description or name was changed by the user)
        Domoticz.Status(f"Modified DDS238 device with DeviceID={DeviceID} and Unit={Unit}: Description="+Devices[DeviceID].Units[Unit].Description)
        if Unit==7:   # Power Factor device: check if Description contains ADDR=1..247
            opts=Devices[DeviceID].Units[Unit].Description.split(',')
            for opt in opts:
                opt=opt.strip().upper()
                if (opt[:5]=="ADDR="):
                    par=int(float(opt[5:]))
                    slave=self.slaves[int(Unit/DEVSMAX)]
                    if par>=1 and par<=247 and par!=slave:
                        # Change Modbus slave address to this device
                        baudValue=1
                        if Parameters["Mode1"]==4800:
                            baudValue=2
                        elif Parameters["Mode1"]==2400:
                            baudValue=3
                        elif Parameters["Mode1"]==1200:
                            baudValue=4

                        try: 
                            self.modbusInit(slave)
                            self.rs485.write_registers(0x15, [ par*256+baudValue ])   # Write register 0x15 with (par<<8 | 1) where par=slave address, 1=9600bps
                            self.rs485.serial.close()  #  Close that door !
                        except:
                            Domoticz.Error(f"Error writing Modbus register 0x15 (to change slave address) to device {slave}")
                        else:
                            Domoticz.Log(f"Device with slave address {slave} successfully reprogrammed with new slave address {par}")
                            Devices[DeviceID].Units[Unit].Description=f"Power Factor,ADDR={slave}"
                            Devices[DeviceID].Units[Unit].Update(Log=True)


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onDeviceModified(Unit):
    global _plugin
    _plugin.onDeviceModified(Unit)

