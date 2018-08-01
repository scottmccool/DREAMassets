# D.R.E.A.M.

## Raspberry Pi Setup

Here are some basic steps for setting up a Raspberry Pi from the CanaKit box.

## Initialize the RPi:
1. put the SD card in
1. hook up a monitor, keyboard and mouse
1. Follow the steps to install Raspberrian
  _This is going to take a while, so grab a :coffee: or whatnot_

## Get the RPi ready for remote usage
1. run `raspi-config` to hook the Pi up to the wireless network
1. run `raspi-config` to change the hostname to something unique that is not `raspberryPi`
1. run `raspi-config` to set the timezone and WiFi country for the machine (under Localisation Options)
1. update the password for the Pi account

At this point you should be able to disconnect the Pi from everything except power and it should be accessible.
Make sure you are on the **same wireless network** as it will only be availble within that subnet.

1. SSH into the RPi from your laptop's terminal so you no longer need to use a separate monitor:
`ssh pi@raspberryPi.local` where `raspberryPi` is replaced by your unique hostname.
*if this doesn't work, verify that both your laptop and RPi are on the same network.*
1. Disconnect your RPi from the monitor, keyboard and mouse and put it in whatever location is most convenient for you.

## Get the RPi ready for Bluetooth Low Energy (BLE)
We need a few extra packages for the Pi to be a BLE scanner.

```
# Get the machine the latest list of software and the latest software
sudo apt-get update
sudo apt-get upgrade -y
```

Then get Bluez itself:

```
sudo apt-get install bluez bluez-hcidump -y
```

For remote usage we should also probably get `screen`
```
sudo apt-get install screen -y
```

For the configurator machine only, you'll also need the `curses` library
```
sudo apt-get install libncurses5-dev libncursesw5-dev ruby-dev -y
```

### Soracom Setup

If you're planning to hook up to Soracom, you'll need a few more bits.

Make sure you have the latest `network-manager` software

```
sudo apt-get update && sudo apt-get install network-manager

```

Setup an APN (Access Point Name) for the SORACOM SIM to connect to the SORACOM mobile network

```
sudo nmcli con add type gsm ifname "*" con-name soracom apn soracom.io user sora password sora
```

This should give you a response like `Connection 'soracom' (3cbecb73-2f6c-48f9-819a-3e233408d4a0) successfully added.`

Restart your Pi

```
sudo shutdown -r now
```

Plugin the SORACOM USB dongle.

SSH back into the Pi.

Once the light on the SORACOM goes blue, you should see `ppp0` in your `ifconfig` output.

```
$ ifconfig
eth0: flags=4099<UP,BROADCAST,MULTICAST>  mtu 1500
        ether b8:27:eb:66:1e:ca  txqueuelen 1000  (Ethernet)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1  (Local Loopback)
        RX packets 4  bytes 156 (156.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 4  bytes 156 (156.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

ppp0: flags=4305<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>  mtu 1500
        inet 10.146.106.124  netmask 255.255.255.255  destination 0.0.0.0
        ppp  txqueuelen 3  (Point-to-Point Protocol)
        RX packets 254  bytes 58898 (57.5 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 264  bytes 33553 (32.7 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

wlan0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 10.4.8.68  netmask 255.255.0.0  broadcast 10.4.255.255
        inet6 fe80::e0f6:75a0:5734:b6aa  prefixlen 64  scopeid 0x20<link>
        ether ba:0e:ee:34:f8:e6  txqueuelen 1000  (Ethernet)
        RX packets 5527  bytes 357676 (349.2 KiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 4437  bytes 847429 (827.5 KiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

We want the `ppp0` (which is the cell networking interface) to be our default.  We can acheive this by grabbing a helper script from SORACOM and running it.

```
# grab the ppp_route_metric script
sudo curl -o /etc/NetworkManager/dispatcher.d/90.set_ppp_route_metric https://soracom-files.s3.amazonaws.com/handson/90.set_ppp_route_metric
# Put it in the set of network startup scripts on the Pi
sudo chmod +x /etc/NetworkManager/dispatcher.d/90.set_ppp_route_metric
# run it
sudo /etc/NetworkManager/dispatcher.d/90.set_ppp_route_metric ppp0 up
```

This step will also set things up so that when the machine starts up again, it will prefer the cell network over the wifi.

To confirm, check that the `ppp0` is listed first in your routing table.

```
route -n

Kernel IP routing table
Destination     Gateway         Genmask         Flags Metric Ref    Use Iface
0.0.0.0         0.0.0.0         0.0.0.0         U     700    0        0 ppp0
10.4.0.0        0.0.0.0         255.255.0.0     U     303    0        0 wlan0
```

At this point you should be on the network via SORACOM.  You can also check using `traceroute`.  The first hop for SORACOM (during
our testing phase) was an Amazon system.  Notice the high latency... more proof that you're on a cell network.

```
traceroute www.whatsmyip.com

traceroute to www.whatsmyip.com (104.25.36.116), 30 hops max, 60 byte packets
 1  ec2-54-93-0-44.eu-central-1.compute.amazonaws.com (54.93.0.44)  858.717 ms  898.895 ms ec2-54-93-0-42.eu-central-1.compute.amazonaws.com (54.93.0.42)  838.623 ms
 2  100.66.0.214 (100.66.0.214)  918.328 ms 100.66.0.218 (100.66.0.218)  958.384 ms 100.66.0.210 (100.66.0.210)  1028.293 ms
 3  100.66.0.107 (100.66.0.107)  1058.564 ms 100.66.0.41 (100.66.0.41)

 ...
```

### Bluez and Bluetooth libraries

Bluez provides the commands `hcitool` and `hcidump` which are the main tools we (probably) will be using to interact with Bluetooth.

To start sniffing, open 2 consoles on the Pi.  In the first console, start up a scanner

```
sudo hciconfig hc0 up
sudo hcitool lescan
```
those commands return a list of hexadecimal BLE hardware addresses and device names, which by default are `unknown`:
```
D5:BB:5C:B3:0C:1C (unknown)
7C:64:56:36:1F:D9 (unknown)
7C:64:56:36:1F:D9 [TV] Samsung 6 Series (55)
4C:0C:F7:63:33:CB (unknown)
8C:85:90:63:A9:29 (unknown)
18:B4:30:E3:A5:89 Nest Cam
DC:56:E7:3C:F6:5F (unknown)
...
```

While the first console continues to output BLE addresses, go to the second console and start up the data dumper:
```
sudo hcidump --raw
```
this command returns a spew of data coming out of the `hcidump` terminal:
```
> 04 3E 23 02 01 00 01 90 2D A5 6C 18 55 17 02 01 06 13 FF 4C 00 0C 0E 00 5F 36 E2 C9 5C 2D 08 B1 72 A7 09 E3 AD CB
> 04 3E 0C 02 01 04 01 90 2D A5 6C 18 55 00 CC
> 04 3E 2B 02 01 00 01 89 A5 E3 30 B4 18 1F 11 07 6C 32 44 5D C8 91 B3 A2 9C 4D 99 9C EF F8 D3 D2 0C FF 18 B4 30 E3 A5 89
> 04 3E 19 02 01 04 01 89 A5 E3 30 B4 18 0D 02 01 06 09 08 4E 65 73 74 20 43 61 6D A5
> 04 3E 17 02 01 00 00 29 A9 63 90 85 8C 0B 02 01 06 07 FF 4C 00 10 02 0B 00 9F
> 04 3E 1A 02 01 00 00 5F F6 3C E7 56 DC 0E 02 01 1A 0A FF 4C 00 10 05 01 10 20 F6 71 9D
> 04 3E 23 02 01 00 01 01 3B F3 FD E1 4B 17 02 01 06 13 FF 4C 00 0C 0E 00 A0 1D 96 2C F6 98 2C 3B A2 97 3A EB F9 AA
> 04 3E 0C 02 01 04 01 01 3B F3 FD E1 4B 00 AA
< 01 0C 20 02 00 01
> 04 0E 04 01 0C 20 00
...
```
Congrats :tada: -- you're sniffing data from the BLE devices near your RPi.
Of course, raw data spewing into your terminal isn't especially useful, so now let's create some scripts to gather and parse the data.

## Pulling the github repo to the Raspberry Pi

Clone the repository like so

```
git clone https://github.com/DREAMassets/DREAMassets.git
```

At this point you'll have a directory called `DREAMassets` with the contents of the github repo.  Follow
the instructions below on using the scanner and parser scripts.

## Scanner

A small bash script can be used to sniff/scan BLE packets that match our desired packets from the Fujitsu tags.

From the root project directory, you can run

```bash
bin/tag_scanner.sh
```

This will report a list of packets that it has collected.   Each packet is written out in the following format

```
[1531866884] 043E2102010301DFCE793166C41502010411FF5900010003000300640486FF6E0025F8C2
```
which include the timestamp (in seconds since the [Epoch](https://www.epochconverter.com/)) in brackets followed by the packet data.

To get all this in a file you can read later

```bash
bin/tag_scanner.sh > sniffed_packets.txt
```

Logic to unpack that is in the parser.

## Parser

Using a short ruby script, you can parse the data from the scanner.


Since we're using ruby, you'll need to make sure you have `bundler` available to ruby.  This is a one time setup.  On your Pi simply run
```
sudo gem install bundler
```

Assuming you've saved the scanner data in a file called `packets.txt`, you'd run

```
cat packets.txt | bin/packet_parser.rb
```

and you should get an output like
```
71BF99DC8CF7,77.27 degF,0.071,0.072,-1.019,219
1C0CB35CBBD5,77.13 degF,0.055,0.000,1.050,184
DFCE793166C4,76.98 degF,0.054,-0.009,1.018,210
71BF99DC8CF7,76.92 degF,0.054,0.081,-1.017,212
1C0CB35CBBD5,77.73 degF,0.056,-0.003,1.056,188
F2461FBDA1D4,77.28 degF,0.029,0.029,-1.026,194
```

which is a CSV format with columns "Device ID (UUID), Temperature (degF), x acceleration, y acceleration, z_acceleration, rssi".
Acceleration is measured in g's.  Rssi units are currently unknown but run from 0 to 255.

## Google Cloud  as remote storage

Because we're hooking up to Google, we need to setup the following variables in our environment
which will allow us to authenticate properly and use the google services through our scripts

```
GOOGLE_PROJECT_ID=<your google project id>
GOOGLE_BUCKET=dream-assets-orange  (or a custom bucket name)
GOOGLE_DIRECTORY=measurements
GOOGLE_CREDENTIALS_JSON_FILE="./secrets/your google credentials.json"
```

These are often bundled in a `env.sh` file which we can store on the hub (not in Github since it has sensitive information).
Also, make sure you actually have a secrets file in place.
Before running the scripts, we can `source env.sh` to set all those variables in our running bash environment.

Once these are set, you can start collecting data with
```bash
source env.sh
bin/tag_scanner.sh | bin/packet_parser.rb

```

Files are stored under your bucket and directory with an additional split across year/month/week where week is the numeric week of the year.

So for July 31, 2018 (which is in the 31'st week of the year) the csv's would be stored under

`your-bucket-name/your-directory-name/2018/07/31/<hub id-timestamp>.csv`

## Google Big Query as a way to get data from Google Cloud Storage

First, give your project permission to use BigQuery by enabling that API.

1. Visit this page https://cloud.google.com/bigquery/docs/quickstarts/quickstart-web-ui and click "Enable the API".
1. Choose your project from the dropdown.
1. Press Continue
1. Click on "Credentials"
1. Answer "No, I'm not using them" to the question "Are you planning to use this API with App Engine or Compute Engine?"
1. Click on "What credentials do I need?"
1. Create a new service account (I called mine 'dream-assets-big-query-api')
1. Create a service account key
1. Choose "JSON" format
1. This will download the credential files through your brower.  That downloaded json file (named something like <username>-<hex key>.json should be copied to the hub.  The file name on the hub should match whatever path is specified in your GOOGLE_CREDENTIALS_JSON_FILE .

At this point, you should be able to get to BigQuery

Go to your Google Cloud console dashboard.  Click on "BigQuery" in the left side navigation panel.

We are going to add a dataset and a table to Big Query that points to our bucket of CSVs.

1. Click on your project on the left sidebar
1. Click on "Create Dataset"
1. Choose a dataset name (like `dream_assets_dataset`)
1. Click "Create dataset"
1. You should (in a few seconds) get a success message that says something like "Dataset was created"
1. Click on your project name again.  It should expand and show you the new data set.
1. Click on that dataset.
1. Click on "Create table"
1. Choose "GoogleCloudStorage" from "Create table from:" and point it to your bucket by setting the "Select File From GSC Bucket" to something like `gs://my-dream-assets-project/my-dream-assets-bucket/measurements/*.csv`.  You can alternatively, use the file browser to pick out 1 csv from your bucket, then replace the csv filename with `*.csv`.
1. Set the file format to `CSV`
1. Set a table name in the "Destination Table" like `measurements_table`
1. Under schema, choose "Edit as text" and insert the following for the schema
```
hub_id:STRING,tag_id:STRING,temperature:FLOAT,x_accel:FLOAT,y_accel:FLOAT,z_accel:FLOAT,rssi:INTEGER,timestamp:INTEGER
```
1. Under Advanced Options, choose "Overwrite table" under "Write Preference"
1. click "Create table"
1. You should, in a few seconds, get a success message that says the table was created.
1. Click on the table and in the query editor, try test query like
```
select count(*) from dream_assets_dataset.measurements_table;
```
1. Click on Run Query
1. Your result should be the number of rows of data you have sitting in that bucket.
1. Try a more informative query like the following (you should update hub id, tag id, and timestamps to values for which you expect a match)
```
SELECT
  DATETIME(PARSE_TIMESTAMP("%s", cast(measurements.timestamp as string)), "America/Los_Angeles") as ts_datetime,
  measurements.*
FROM
  dream_assets_dataset.measurements_table measurements,
where
  measurements.timestamp > 1532538000 # 10am July 25 2018 PST
  and measurements.timestamp < 1532545200 # 12am July 25 2018 PST
  and measurements.tag_id='<tag id>'
  and measurements.hub_id='<hub id>'
order by timestamp desc
```

1. If you got results, you are on your way.
1. You can click "Save As" to export the data you just queried to a CSV.  This download will truncate the data at 16000 rows.

## Required environment variables on the Hub


## Deployment on Raspberry PIs

Typical deployment, once the PI is setup, should go as follows

1. login to the pi
```
ssh pi@the_pi_name
```

1. connect to the remote screen (if it exists)
```
# try
screen -r
# if it says there is no screen to connect to then
screen
```

1. If the PI is collecting data, connecting to the screen should show you some data.  You can use Ctrl+C to kill that process and exit the screen
1. Update the code ( `cd ble_sniffing/; git pull` )
1. restart the collection process

```
source env.sh && bin/tag_scanner.sh | bin/packet_parser.rb
```

1. exit from the screen with Ctrl+A Ctrl+D
1. logout of the PI

Notes:
* Logs are stored on the PI under logs/packet_parser.log

## Configurator

The Configurator is a tool that will help us find and identify Fujitsu tags in the neighborhood.  It is expected to be run
on a dedicated Raspberry Pi.

### Setup Mode

To run it:
```
bin/configurator.rb setup -s 10
```
This will (under the hood) use `bin/tag_scanner.sh` to listen for Fujitsu tags and report back the found tag id's and their
current RSSI.  On subsequent runs, it will also include in the report, the last time setup was run and the delta in RSSI for
any tags it may have seen last time and this time.  In the case where the tag was not seen in the previous run, the
`Δ RSSI` will report `-`.

Sample Output:
```
$ bin/configurator.rb setup -s 3

Scanning for ~3 seconds...done
(#)  Tag ID               RSSI   Δ RSSI Previously Run 1532726366 secs ago
(1)  D446 77E9 62B0          -24      -
(2)  E175 6F50 EBE2          -25      -
(3)  F78C DC99 BF71          -48      -
(4)  D0D7 CA18 963F          -55      -
(5)  D5BB 5CB3 0C1C          -61      -
(6)  E294 B4AF 9313          -65      -
(7)  F991 FBD4 0C78          -74      -
(8)  C466 3179 CEDF          -79      -

$ bin/configurator.rb setup -s 3

Scanning for ~3 seconds...done
(#)  Tag ID               RSSI   Δ RSSI Previously Run 79 secs ago
(1)  D446 77E9 62B0          -24      0
(2)  F78C DC99 BF71          -40     -8
(3)  E294 B4AF 9313          -50    -15
(4)  F991 FBD4 0C78          -58    -16
(5)  D0D7 CA18 963F          -62      7
(6)  D5BB 5CB3 0C1C          -67      6
(7)  C466 3179 CEDF          -74     -5
```

### Identify Mode

To run it:
```
bin/configurator.rb identify -n 5
```

where `n` represents the number of tags you are looking for.  The configurator will pick the closest 5 tags (from the last run
of setup and sorted by RSSI) and look for only those.

This interactive application will show the activity of each tag that it's watching.  Idle shows a `.`.  When a tag is flipped
you'll see a `|`.

e.g.

For one tag that has one flip, you might see this:

```
EDA9 5A3F 8FE0	.................|......
```

Additional data is reported periodically (about every 2 or 3 seconds).  When you are finished flipping tags, hit `Ctrl+C` and you'll
get a report of the tags and that were flipped in the order they were flipped.


Sample Output:
```
bin/configurator.rb identify -n 5
Thanks for playing.

F991 FBD4 0C78	.........................
E24B 5296 F2B3	............|.............
EDA9 5A3F 8FE0	.................|......
F814 D580 FA46	....................|....
FDD5 7779 1B47	......................|..

Here are the tags you flipped.
(1) E24B 5296 F2B3
(2) EDA9 5A3F 8FE0
(3) F814 D580 FA46
(4) FDD5 7779 1B47
```

You can see from above the first one that was flipped was `E24B`, second was `EDA9` etc.  And `F991` had no flips so it does not show up in the report.

# Appendix

## Code Organization

Everything under the `bin` directory should be our executable scripts.  Examples are the `packet_parser.rb` and `tag_scanner.sh`.  Helper functions and other modules for both bash and ruby will live under the `lib` directory in their respective language named directories (e.g. `lib/ruby` holds all the ruby libraries and helper modules)
