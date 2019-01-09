# Contains logic to perform a bluepy ble scan 
# To change pre-filter logic, implement a new ScanDelegate

# Accepts scanner config arguments
# Calls publisher.publish task for all packets that match pre-filter

# Sniffer utilities
from bluepy.btle import Scanner, DefaultDelegate
import signal
import re
import time
from dreamhub.publisher.tasks import publish_observation

# Possible scanning mode, called by sniffer task
def sniffForever(hci):
    """ Start a ble scanner and run forever """
        # Configure our delegate called on each advertisement
    preFilterDelegate = PublishOnlyFujitsu(hci)
        # Configured a scanner with that delegate
    scanner = Scanner(hci).withDelegate(preFilterDelegate)
    scanner.clear()
    scanner.start()
        # Do a bunch of signal handling so we can safely run scanner.process() forever
    def stop_scan(signum, frame):
        scanner.stop()
        return

    while True:
        # define how to stop the scan on an interrupt
        signal.signal(signal.SIGHUP, stop_scan)
        signal.signal(signal.SIGINT, stop_scan)
        signal.signal(signal.SIGTERM, stop_scan)
        signal.signal(signal.SIGTSTP, stop_scan)
        scanner.clear()
        scanner.start()
        while True:
            scanner.process()

class PublishOnlyFujitsu(DefaultDelegate):
    FUJITSU_PACKET_REGEX = re.compile(r'010003000300')
    def __init__(self,hci=0):
        DefaultDelegate.__init__(self)
        self.hci = hci

    def handleDiscovery(self, bleAdvertisement, isNewDev, isNewData):
        packet = buildPacketFromBle(bleAdvertisement,self.hci)
        if packet == None:
            return
        if re.search(self.FUJITSU_PACKET_REGEX, packet['mfr_data']):
            packet['hci'] = self.hci
            publish_observation.app.send_task('dreamhub.publisher.tasks.publish_observation', [packet], queue='publisher')
        return # Default implementation does nothing!

class PublishAll(DefaultDelegate):
    def __init__(self,hci=0):
        DefaultDelegate.__init__(self)
        self.hci = hci

    def handleDiscovery(self, bleAdvertisement, isNewDev, isNewData):
        packet = buildPacketFromBle(bleAdvertisement,self.hci)
        if packet != None:
            publish.app.send_task('dreamhub.publisher.tasks.publish', [packet], queue='publisher')

def buildPacketFromBle(bleAdvertisement,hci):
    packet = None
    try:
        # get the tag_id (MAC address) and rssi from the BLE advertisement
        # since the MAC address comes with colons, remove them.
        tag_id = bleAdvertisement.addr.replace(':', '')
        rssi = bleAdvertisement.rssi

        # getScanData returns a tripple from the ScanEntry object
        # the tripple has the advertising type, description and value (adtype, desc, value)
        triples = bleAdvertisement.getScanData()

        # Bluetooth defines AD types https://ianharvey.github.io/bluepy-doc/scanentry.html
        # DREAM only wants adtype = 0xff (0d255) for manufacturer data
        # values is a list where the last element is the manufacturer data
        values = [value for (adtype, desc, value) in triples if adtype == 255]
        if len(values):
            packet = {
                "tag_id": tag_id,
                "rssi": rssi,
                "timestamp": int(time.time()),
                "mfr_data": values[-1]
            }
    except (UnicodeEncodeError, UnicodeDecodeError):
        # If there's a unicode error, disregard it since it isn't a Fujitsu Tag
        print("Discarding on Unicode error (non Fujitsu)")
        return None
    return packet
    
