# Control side
Messages from the control code will be in a more user-readable format. Here are the available commads:

<br>**Motion commands:**
| Message | Responses | Description |
| :-----: | --------- | ----------- |
| F{*distance*} | None  | Move forward by {distance}"               |
| B{*distance*} | None  | Move backwards by {distance}"             |
| L{*distance*} | None  | Move left by {distance}"                  |
| R{*distance*} | None  | Move right by {distance}"                 |
| SL{*angle*}   | None  | Rotate left by {angle}&deg;               |
| SR{*angle*}   | None  | Rotate right by {angle}&deg;              |
| M             | bool  | Check if value is in motion               |
| H             | None  | Stop current movement                     |
| P             | float | Fetch the % along latest movement command |

<br>**Sensor commands:**
| Message | Responses | Description |
| :-----: | --------- | ----------- |
| US-ALL      | dict  | Fetch a dictionary of all ultrasonic sensor readings  |
| US{*id*}    | float | Fetch the sensor reading of an ultrasonic by its {id} |
| SENSORS     | dict  | Fetch all sensor readings (not just ultrasonics)      |
| G           | float | Fetch gyroscope reading                               |
| C           | float | Fetch compass reading                                 |

# Robot side
To make it easier to code, all command messages will start with 1 byte indicating message length, 1 bytes indicating the "target" of the message, then any additional values required. The following table(s) excludes the length byte. All values (stuff in {...}) are sent after the 2 first bytes.

<br>**Motion commands:**
| Message       | Translation (byte 2) |
| :-----:       | -------------------- |
| F{*distance*} |  0x01                |
| B{*distance*} |  0x02                |
| L{*distance*} |  0x03                |
| R{*distance*} |  0x04                |
| SL{*angle*}   |  0x05                |
| SR{*angle*}   |  0x06                |
| M             |  0x07                |
| H             |  0x08                |
| P             |  0x09                |

<br>**Motion commands:**
| Message       | Translation (byte 2) |
| :-----:       | -------------------- |
| SENSORS       |  0x10                |
| US-ALL        |  0x20                |
| G             |  0x30                |
| C             |  0x40                |
| US-1          |  0x21 -> 2nd 4 bits for {*id*}                |
