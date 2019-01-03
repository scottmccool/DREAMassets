#!/bin/bash


## This essentially scripts 
# https://www.raspberrypi.org/forums/viewtopic.php?t=191252

# It's only really intended to rapidly "factory reset" a pi during active development of the configurator code.  If you're spending time on it, refactor 
# to something more scalable.

## Defaults
RASPBIAN_MINIMAL_IMG_NAME="2018-11-13-raspbian-stretch-lite"
RASPBIAN_MINIMAL_IMG_URL="http://director.downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2018-11-15/${RASPBIAN_MINIMAL_IMG_NAME}.zip"
DEFAULT_SD_DEVICE="/dev/sdc"

cwd=`pwd`

echo "\n\n=====\n\n"
echo "This is a dev helper script.  If you're provisioning more than 1 hub for your own sanity refactor this!"
echo "Remember, you only have to do this if you are making sure the ansible configurator scripts are working"
echo "If you just want to deploy the latest code, you should run a deployment playbook from ansible directory"
echo "\n\n======\n\n"
# Create cache if it isn't there, dont b fancy about it
mkdir -p cache/raspbian_lite_base > /dev/null 2>&1
mkdir -p cache/raspbian_lite_base/sd_card/{root,boot}

cd cache/raspbian_lite_base

if [ -f "${RASPBIAN_MINIMAL_IMG_NAME}.zip" ]
then
  echo "Found existing raspbian base image, not updating cache"
else
  curl $RASPBIAN_MINIMAL_IMG_URL -O
  unzip -o ${RASPBIAN_MINIMAL_IMG_NAME}.zip
fi

read -e -p "Device path to wipe out (<enter> for __${DEFAULT_SD_DEVICE}__: " -i "$DEFAULT_SD_DEVICE" SD_DEVICE

read -e -p "Type \"wipe_out_$SD_DEVICE\" to continue: " WIPEOUT_CONFIRMED
if [ "$WIPEOUT_CONFIRMED" = "wipe_out_${SD_DEVICE}" ]
then
  echo "\n\n\n================\n\nConfirmed.  Burning base image.  This will take a bit"
  #sudo dd bs=4M if="${RASPBIAN_MINIMAL_IMG_NAME}.img" of="${SD_DEVICE}" conv=fsync
  echo "\n===============\n Done! \n\nMounting burned image"
  echo
  pwd
  ls
  echo
  sudo mount "${SD_DEVICE}1" sd_card/boot
  sudo mount "${SD_DEVICE}2" sd_card/root
  echo "Customizing base image: enabling ssh"
  sudo touch sd_card/root/ssh
  sudo touch sd_card/boot/ssh
  echo "Customizing base image: Creating wifi configuration"
  read -e -p "Enter WiFi SSID: " SSID
  read -e -p "Enter WP-PSK (your wifi password): " PSK
  sudo cp ${cwd}/wpa_supplicant_base sd_card/root/etc/wpa_supplicant/wpa_supplicant.conf
  sudo sed -i "s/your_real_wifi_ssid/${SSID}/g" sd_card/root/etc/wpa_supplicant/wpa_supplicant.conf
  sudo sed -i "s/your_real_password/${PSK}/g" sd_card/root/etc/wpa_supplicant/wpa_supplicant.conf
  echo "\n\n All Done!  Ejecting sd card.  Put it in a pi and boot it up, the run the ansible configurator, you've rebuilt from base OS!\n"
  echo "Press enter to complete."
  read anykey
  sudo umount "${SD_DEVICE}1"
  sudo umount "${SD_DEVICE}2"

else
  echo "You entered $WIPEOUT_CONFIRMED, exiting"
  cd $cwd
  exit 1
fi

echo "Exiting"
cd $cwd
