# Factory refresh

Intended to run on a management node (your workstation), not the hub.

Use the script in this directory to:
  * Downlaod Raspbian minimal and burn to a mounted SD card
  * Copy a wpa_supplicant file over so that the hub works on wifi
  * Set a default root user and password
  * Eject the mounted SD card; you are now ready to run the ansible scripts to configure the hub

  In the future, this should be expanded so that we are burning fully configured images (already having had ansible run for a release) and utilities to update that image as well as helper scripts to push newer versions of code for our actual services.


  ## Todo
  * Read defaults from command line and allow non-interactive mode (for fastest reprovisioning of single hosts or at least for easy for looping