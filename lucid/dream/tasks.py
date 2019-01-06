# Data terminology:
#   BLE Advertisement --> Bluepy snatches these out of the air, like magic!
#   packet --> A python dictionary containing data extracted from the advertisement and metadata added by the lucid frameowrk

# Data flow
## <BLE Advertisement> !! -> sniffer -> <sniffed_packets queue>
##  <sniffed_packets_queue> -> publisher -> <google cloud function>

# Sniffer runs a thread per HCI detected, forever.  Assume systemd will restart on error.
# Publisher has basic filtering and batching logic.

import dreamconfig
def sniff(hci=0):
