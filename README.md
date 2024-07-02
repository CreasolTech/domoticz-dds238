# domoticz-dds238 

This is a plugin for the free open-source [Domoticz home automation system](https://www.domoticz.com) that **read one or more DDS238 ZN/S energy meters by Modbus connection** (RS485 serial connection), providing the following data: 
* net active energy and power (imported - exported energy)
* total active energy (imported + exported energy)
* import active energy and power
* export active energy and power
* voltage
* current
* frequency
* power factor

![DDS238 ZN/S single phase energy meter](https://images.creasol.it/dds238_panel.webp "DDS238 ZN/S single phase energy meter shown in the Domoticz panel")


It's possible to configure:
* Bitrate, by default 9600 bps
* Meter address, for example 1 (only one meter with default slave address) or 11,12 (two devices with address 11 and 12: address should be separated by comma)
* Poll interval, in seconds: in case of a long list of devices, don't use very short poll intervals!

Please note that it's possible to easily connect many DDS238 ZN/S meters to the same RS485 bus, by using a common shielded cable within 2 wires (A and B terminal blocks) to a cheap RS485/USB adaper/converter.

![DDS238-2 ZN/S single phase energy meter](https://images.creasol.it/dds238_scheme.webp "DDS238-2 ZN/S single phase energy meter")

## Setting a different address for the meter

By default, DDS238 ZN/S meters have slave address=1: when a meter with default address is connected to the RS485 bus, only a device will be created just to permit changing its address. Telemetry from default address meter will not be read!

To change the meter address of a new meter with default address=1, select the *Change Address 1 -> 2-247* virtual device, edit the Description field writing **ADDR=2**  to change the meter address to 2. Address valid range is between 2 and 247.

In case you want to change the address of a meter that already has an address between 2 and 247, select the corresponding *Power Factor* device, edit the Description field writing ADDR=3  to change the meter address to 3. Address valid range is between 2 and 247.

Then, go to Setup -> Hardware -> DDS238 Plugin and add that address to the end of *Meter addresses* list. **NEVER CHANGE THE *Meter addresses* SEQUENCE** adding new devices in the middle, or you'll mix/loose previous telemetry!!

![Net energy and power, using DDS238 ZN/S single phase energy meter with Domoticz](https://images.creasol.it/dds238_net_energy.webp "Net energy and power, using DDS238 ZN/S single phase energy meter with Domoticz")


## Installation

This plugin can be installed from [Python Plugin Manager](https://github.com/ycahome/pp-manager) or [Python Plugins Manager](https://github.com/stas-demydiuk/domoticz-plugins-manager) which also permit to update plugin easily or automatically.

Alternatively, it's possible to give the following commands from the linux shell:

```
cd ~/domoticz/plugins
git clone https://github.com/CreasolTech/domoticz-dds238
```

Then, in the future, to update the plugin it's possible to simply type
```
cd ~/domoticz/plugins/domoticz-dds238
git pull
```

It uses the python plugin module minimalmodbus , than can be installed by
```
sudo apt install pyserial
sudo pip3 install minimalmodbus
```


Restart Domoticz, then go to Setup -> Hardware and add the DDS238 plugin, specifying a name for that hardware and the serial port.

## Upgrade
**PLEASE NOTE THAT UPDATING THE PLUGIN from version 1.x, NEW DEVICES WILL BE CREATED** because the plugin has been rewritten to use the DomoticzEx class instead of the old legacy Domoticz class: 
to recover data from the old ones, select old devices one-by-one (in the Utility panel), click on Replace button and select the name of the newly created device! 
In this way you do not loose the history.

## Translation in other languages
**Plugin can be easily translate in other languages**: just copy and translate the rows below, and open an issue on github writing the modified lines with your translations, with the language code.
```
Words to translate in other languages (in double quotes):
English (en)            Italian (it)                    YourLanguage (??)
"Power/Energy total"    "Potenza/Energia totale"        ""
"Power/Energy imported" "Potenza/Energia importata"     ""
"Power/Energy exported" "Potenza/Energia esportata"     ""
"Voltage"               "Tensione"                      ""
"Current"               "Corrente"                      ""
"Frequency"             "Frequenza"                     ""
"Power Factor"          "Fattore di Potenza"            ""
"Power/Energy net"		"Potenza/Energia netta"			""
```

## Modbus holding registers:

| Register(s) | Meaning         | Scale Unit | Data format    | R/W |
|-------------|-----------------|------------|----------------|:---:|
| 0000h-0001h | total energy    | 1/100 kWh  | unsigned dword |  R¹ |
| 0002h-0003h | reserved        |            | unsigned dword |     |
| 0004h-0005h | reserved        |            | unsigned dword |     |
| 0006h-0007h | reserved        |            | unsigned dword |     |
| 0008h-0009h | export energy   | 1/100 kWh  | unsigned dword |  R¹ |
| 000Ah-000Bh | import energy   | 1/100 kWh  | unsigned dword |  R¹ |
| 000Ch       | voltage         | 1/10 V     | unsigned word  |  R  |
| 000Dh       | current         | 1/100 A    | unsigned word  |  R  |
| 000Eh       | active power    | 1 W        | signed   word  |  R  |
| 000Fh       | reactive power  | 1 VAr      | unsigned word  |  R  |
| 0010h       | power factor    | 1/1000     | unsigned word  |  R  |
| 0011h       | frequency       | 1/100 Hz   | unsigned word  |  R  |
| 0012h       | reserved        |            | unsigned word  |     |
| 0013h       | reserved        |            | unsigned word  |     |
| 0014h       | reserved        |            | unsigned word  |     |
| 0015h:high  | station address | 1-247      | unsigned char  | R/W |
| 0015h:low   | baud rate       | 1-4²       | unsigned char  | R/W |
| 001Ah       | relay³          |            | unsigned word  | R/W |

### Notes:

#### Note 1:

Total, export and import energy counters can erased writing 0 in total energy
registers.

#### Note 2:

Value mapping, default 1.

| Value | Baud rate |
|:-----:|:---------:|
| 1     | 9600 Bd   |
| 2     | 4800 Bd   |
| 3     | 2400 Bd   |
| 4     | 1200 Bd   |

#### Note 3:

In DDS238-2 ZN/SR model the relay can be switched by 0x001A register.

| Value | Relay |
|:-----:|:-----:|
|   0   |  Off  |
|   1   |  On   |

#### Data formats

| Data format | Lenght  | Byte order |
|-------------|--------:|------------|
| char        |  8 bits |            |
| word        | 16 bits | Big endian |
| dword       | 32 bits | Big endian |


### Writing registers

The meter does not understand the 'write sigle register' function code (06h),
only the 'write multiple registers' function code (10h).


## Credits
Many thanks to:
* Fernando Herrero, where I found the DDS238 information above. https://gist.github.com/alphp

***

Below a list of modules, produced in Europe by Creasol, designed for Domoticz to be reliable and optimized for very very low power consumption.

## Creasol DomBus modules
Our industrial and home automation modules are designed to be
* very low power (**around 10mW with relays OFF**)
* reliable (**no disconnections**)
* bus connected (**no radiofrequency interference, no battery to replace**).

Modules are available in two version:
1. with **DomBus proprietary protocol**, working with [Domoticz](https://www.domoticz.com) only
2. with **Modbus standard protocol**, working with [Home Assistant](https://www.home-assistant.io), [OpenHAB](https://www.openhab.org), [Node-RED](https://nodered.org)

[Store website](https://store.creasol.it/domotics) - [Information website](https://www.creasol.it/domotics)

### Youtube video showing DomBus modules 
[![Creasol DomBus modules video](https://images.creasol.it/intro01_video.png)](https://www.creasol.it/DomBusVideo)

### DomBusEVSE - EVSE module to build a Smart Wallbox / EV charging station
<a href="https://store.creasol.it/DomBusEVSE"><img src="https://images.creasol.it/creDomBusEVSE_200.png" alt="DomBusEVSE smart EVSE module to make a Smart Wallbox EV Charging station" style="float: left; margin-right: 2em;" align="left" /></a>
Complete solution to make a Smart EVSE, **charging the electric vehicle using only energy from renewable source (photovoltaic, wind, ...), or adding 25-50-75-100% of available power from the grid**.

* Single-phase and three-phases, up to 36A (8kW or 22kW)
* Needs external contactor, RCCB (protection) and EV cable
* Optional power meter to measure charging power, energy, voltage and power factor
* Optional power meter to measure the power usage from the grid (not needed if already exists)
* **Two max grid power thresholds** can be programmed: for example, in Italy who have 6kW contractual power can drain from the grid Max (6* 1.27)=7.6kW for max 90 minutes followed by (6* 1.1)=6.6kW for another 90 minutes. **The module can use ALL available power** when programmed to charge at 100%.
* **Works without the domotic controller** (stand-alone mode), and **can also work with charging current set by the domotic controller (managed mode)**

<br clear="all"/>

### DomBusTH - Compact board to be placed on a blank cover, with temperature and humidity sensor and RGW LEDs
<a href="https://store.creasol.it/DomBusTH"><img src="https://images.creasol.it/creDomBusTH6_200.png" alt="DomBusTH domotic board with temperature and humidity sensor, 3 LEDs, 6 I/O" style="float: left; margin-right: 2em;" align="left" /></a>
Compact board, 32x17mm, to be installed on blank cover with a 4mm hole in the middle, to exchange air for the relative humidity sensor. It can be **installed in every room to monitor temperature and humidity, check alarm sensors, control blind motor UP/DOWN**, send notifications (using red and green leds) and activate **white led in case of power outage**.

Includes:
* temperature and relative humidity sensor
* red, green and white LEDs
* 4 I/Os configurable as analog or digital inputs, pushbuttons, counters (water, gas, S0 energy, ...), NTC temperature and ultrasonic distance sensors
* 2 ports are configured by default as open-drain output and can drive up to 200mA led strip (with dimming function) or can be connected to the external module DomRelay2 to control 2 relays; they can also be configured as analog/digital inputs, pushbuttons and distance sensors.
<br clear="all"/>

### DomBus12 - Compact domotic module with 9 I/Os
<a href="https://store.creasol.it/DomBus12"><img src="https://images.creasol.it/creDomBus12_400.webp" alt="DomBus12 domotic module with 9 I/O" style="float: left; margin-right: 2em;" align="left" /></a>
**Very compact, versatile and cost-effective module with 9 ports**. Each port can be configured by software as:
* analog/digital inputs
* pushbutton and UP/DOWN pushbutton
* counters (water, gas, S0 energy, ...)
* NTC temperature and ultrasonic distance sensors
* 2 ports are configured by default as open-drain output and can drive up to 200mA led strip (with dimming function) or can be connected to the external module DomRelay2 to control 2 relays.
<br clear="all"/>

### DomBus23 - Domotic module with many functions
<a href="https://store.creasol.it/DomBus23"><img src="https://images.creasol.it/creDomBus23_400.webp" alt="DomBus23 domotic module with many functions" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
Versatile module designed to control **gate or garage door**.
* 2x relays SPST 5A
* 1x 10A 30V mosfet (led stripe dimming)
* 2x 0-10V analog output: each one can be configured as open-drain output to control external relay
* 2x I/O lines, configurable as analog/digital inputs, temperature/distance sensor, counter, ...
* 2x low voltage AC/DC opto-isolated inputs, 9-40V
* 1x 230V AC opto-isolated input
<br clear="all"/>

### DomBus31 - Domotic module with 8 relays
<a href="https://store.creasol.it/DomBus31"><img src="https://images.creasol.it/creDomBus31_400.webp" alt="DomBus31 domotic module with 8 relay outputs" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
DIN rail low profile module, with **8 relays and very low power consumption**:
* 6x relays SPST 5A
* 2x relays STDT 10A
* Only 10mW power consumption with all relays OFF
* Only 500mW power consumption with all 8 relays ON !!
<br clear="all"/>

### DomBus32 - Domotic module with 3 relays
<a href="https://store.creasol.it/DomBus32"><img src="https://images.creasol.it/creDomBus32_200.webp" alt="DomBus32 domotic module with 3 relay outputs" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
Versatile module with 230V inputs and outputs, and 5 low voltage I/Os.
* 3x relays SPST 5A
* 3x 115/230Vac optoisolated inputs
* Single common for relays and AC inputs
* 5x general purpose I/O, each one configurable as analog/digital inputs, pushbutton, counter, temperature and distance sensor.
<br clear="all"/>

### DomBus33 - Module to domotize a light system using step relays
<a href="https://store.creasol.it/DomBus33"><img src="https://images.creasol.it/creDomBus32_200.webp" alt="DomBus33 domotic module with 3 relay outputs that can control 3 lights" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
Module designed to **control 3 lights already existing and actually controlled by 230V pushbuttons and step-by-step relays**. In this way each light can be activated by existing pushbuttons, and by the domotic controller.
* 3x relays SPST 5A
* 3x 115/230Vac optoisolated inputs
* Single common for relays and AC inputs
* 5x general purpose I/O, each one configurable as analog/digital inputs, pushbutton, counter, temperature and distance sensor.

Each relay can toggle the existing step-relay, switching the light On/Off. The optoisolator monitors the light status. The 5 I/Os can be connected to pushbuttons to activate or deactivate one or all lights.
<br clear="all"/>

### DomBus36 - Domotic module with 12 relays
<a href="https://store.creasol.it/DomBus36"><img src="https://images.creasol.it/creDomBus36_400.webp" alt="DomBus36 domotic module with 12 relay outputs" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
DIN rail module, low profile, with **12 relays outputs and very low power consumption**.
* 12x relays SPST 5A
* Relays are grouped in 3 blocks, with a single common per block, for easier wiring
* Only 12mW power consumption with all relays OFF
* Only 750mW power consumption with all 12 relays ON !!
<br clear="all"/>

### DomBus37 - 12 inputs, 3 115/230Vac inputs, 3 relay outputs
<a href="https://store.creasol.it/DomBus37"><img src="https://images.creasol.it/creDomBus37_400.webp" alt="DomBus37 domotic module with 12 inputs, 3 AC inputs, 3 relay outputs" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
Module designed to be connected to alarm sensors (magnetc contact sensors, PIRs, tampers): it's able to monitor mains power supply (power outage / blackout) and also have 3 relays outputs.
* 12x low voltage inputs (analog/digital inputs, buttons, alarm sensors, counters, temperature and distance sensors, ...)
* 3x 115/230Vac optoisolated inputs
* 2x relays SPST 5A
* 1x relay SPST 10A
* In12 port can be used to send power supply to an external siren, monitoring current consumption
<br clear="all"/>

### DomRelay2 - 2x relays board
<a href="https://store.creasol.it/DomRelay2"><img src="https://images.creasol.it/creDomRelay22_200.png" alt="Relay board with 2 relays, to be used with DomBus domotic modules" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
Simple module with 2 relays, to be used with DomBus modules or other electronic boards with open-collector or open-drain outputs
* 2x 5A 12V SPST relays (Normally Open contact)
* Overvoltage protection (for inductive loads, like motors)
* Overcurrent protection (for capacitive laods, like AC/DC power supply, LED bulbs, ...)
<br clear="all"/>

### DomESP1 / DomESP2 - Board with relays and more for ESP8266 NodeMCU WiFi module
<a href="https://store.creasol.it/DomESP1"><img src="https://images.creasol.it/creDomESP2_400.webp" alt="Relay board for ESP8266 NodeMCU module" style="float: left; margin-right: 2em; vertical-align: middle;" align="left" /></a>
IoT board designed for NodeMCU v3 board using ESP8266 WiFi microcontroller
* 9-24V input voltage, with high efficiency DC/DC regulator with 5V output
* 4x SPST relays 5V with overvoltage protection
* 1x SSR output (max 40V output)
* 2x mosfet output (max 30V, 10A) for LED dimming or other DC loads
* 1x I²C interface for sensors, extended I/Os and more)
* 1x OneWire interface (DS18B20 or other 1wire sensors/devices)
<br clear="all"/>


