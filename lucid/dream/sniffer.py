# Data terminology:
#   BLE Advertisement --> Bluepy snatches these out of the air, like magic!
#   packet --> A python dictionary containing data extracted from the advertisement and metadata added by the lucid frameowrk

# Data flow
## <BLE Advertisement> !! -> sniffer -> <sniffed_packets queue>
##  <sniffed_packets_queue> -> publisher -> <google cloud function>

# Sniffer runs a thread per HCI detected, forever.  Assume systemd will restart on error.
# Publisher has basic filtering and batching logic.

# Honestly we're just copying this from sobun, it should really dyanmically detect the number of BLE interfaces
# and do the right thing so that ansible configs don't have to to be weird.

from bluepy.btle import Scanner, DefaultDelegate
import dreamconfig

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            print("Discovered device: %s" % dev.addr)
        elif isNewData:
            print("Received new data from: %s" % dev.addr)

scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(float(dreamconfig.BTLE_TIMEOUT))

for dev in devices:
    print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
    for (adtype, desc, value) in dev.getScanData():
        print("  %s = %s" % (desc, value))
