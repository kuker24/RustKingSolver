---
name: ctf-ics
description: "CTF ICS/OT checklist — PLC program analysis, conveyor/setpoint logic, Modbus/OPC-UA traffic, ladder-logic reading, SCADA HMI challenge, industrial protocol pcap, solder/flashback-class hardware challenges. Trigger: ics challenge, ot ctf, plc, modbus, scada, conveyor, setpoint, ladder logic, industrial, hmi, ot protocol."
---

# CTF ICS/OT — checklist

CTV scored 6/8 here. The two losses (`solder`, `flashback`) had no written
hypothesis — this pack exists so the next pass has one. MITRE ATT&CK-for-ICS
mapping tables do **not** solve these; reading the controller does.

## 1. Identify the layer

| Artifact | Layer | First move |
|---|---|---|
| `.pcap` on port 502 | Modbus/TCP | decode registers, watch writes |
| `.pcap` on 4840 | OPC-UA | decode node IDs, browse requests |
| `.ladder`/`.lad`/`.rss`/text mnemonic | PLC logic | read the rung chain |
| `.st` / SCL / STL | structured text | trace variable writes |
| HMI screenshot / `.svg` mimic | SCADA UI | map tag → value → alarm |
| schematic + firmware | hardware (solder/flashback) | read chip marking, then dump |

## 2. PLC logic

1. Extract the program (`binwalk`, or the vendor tool's export).
2. List **tags** and find the one that gates the output (a coil, a lamp, a valve).
3. Trace **inputs** to that gate: which register/coil must be true.
4. `conveyor`/`setpoint` shape: the flag is the value that makes the simulation
   reach a state, or the sequence of writes that flips the gate.

```bash
tshark -r ics.pcap -Y 'modbus' -T fields \
  -e modbus.func_code -e modbus.reference_num -e modbus.word_cnt -e modbus.regval_uint16
```

`setpoint`: a write of value **V** to register **N** is the answer. Emit the exact
write frame, do not describe it.

## 3. Ledger discipline for ICS

ICS challenges are usually multi-step state machines, so keep a table:

| t | direction | func | addr | value | effect |
|---|---|---|---|---|---|

Missing a step silently desynchronises the sim → looks like a dead end.

## 4. Hardware (solder / flashback)

Both failed in CTV without notes. Concrete first moves for next time:

- Read the chip marking, then find the datasheet and its **programming interface**
  (SWD/JTAG/ISP/SPI).
- Dump the EEPROM/SPI flash (`flashrom`, `openocd`, `minipro`).
- `binwalk` the dump for a filesystem, then `strings` for config/credentials.
- `solder`: jumper/pad changes define the boot mode — read the schematic for the
  boot strap, not the firmware.
- `flashback`: the answer is usually a value in the **previous** firmware image, so
  diff old vs new rather than analyse one.

## Output contract

```
LAYER:    modbus | opcua | ladder | scada | hardware
STATE:    <tag/register → required value>
PAYLOAD:  <exact frame or value>
FLAG:     <flag>
NEGATIVE: <dead-end probes, if unsolved>
```
