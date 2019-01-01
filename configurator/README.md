# Automatic hub configuration (woker)

### Prerequisites
* <Provisioning workstation only> Install ansible on your workstation (one time only, assumes ubuntu 18.04)
  ** 
  ```
  $ sudo apt-get install python3-pip
  $ pip3 install --user ansible
  $ grep -q -F 'PATH=\$PATH:~/.local/bin' ~/.bashrc || echo 'PATH=$PATH:~/.local/bin' >> ~/.bashrc
  ```

### Hub provisioning
* Hub provisioning is a two stage process.  First, set up an sd card with a minimal Raspian stretch image.  It should connect to wifi and you should know it's default password (as of Stretch, it's pi/password).  Use raspbian_minimal to burn this very tiny base Raspbian.
```
cd raspbian_minimal && ./flash_sdcard.sh
```

Will generate a fresh one for you, including prompting you for wifi information.

* Second, provision the DREAM framework to the hub (use Ansible to configure the hub as we'd like it, including starting up dream-sniffer, dream-batcher, and dream-syncer.  The project ships with a sample inventory in hub_inventories which you should copy to another file and list all your hosts (then specify on the command line below):

```
$ ansible-playbook -i hub_inventories/single_development_hub.ini plays/provision_hub.yml 
```

This will log into an empty raspbi at 192.168.0.19 as username pi.  On the first run you may need to add -k to the ansible command in order to be prompted for a password before the key is installed.  It's however you froze the base OS image.  Once it logs in, it will add an ssh key you specified above (by using the development hub profile, which has an insecure SSH key checked in).

In the future this will support multiple hubs at once, and let you define sets of hubs to be provisioned and their secrets/variables.  For now we're just doing this one at a time.

### Clear data from hub and restart services
```
$ ansible-playbook -i hub_inventories/single_development_hub.ini plays/clear_hub_data.yml
```


### Logging into a configured pi
```
ssh-add secrets/hub_credentials/hub_default
ssh dreamer@<ip>
```


### From the pi itself
Everything runs as "dreamer" as configured in provision_hub play.
Code runs from /usr/local/sobun.
Config is in /usr/local/sobun/config
Logs for all dream-* services are in /usr/local/sobun/log/

To manage services:
```
systemctl restart dream-sniffer 0
systemctl restart dream-sniffer 1
systemctl restart dream-sniffer 2
systemctl restart dream-batcher
systemctl restart dream-syncer
```

### Developers guide
* Change python code in dream/ all you want.
* Reprovision hub (or come up with a play to just restart services, or just remember you can always)
``` 
sudo systemctl restart dream-sniffer@{0..3}
```
* Want to see remote hubs facts for troubleshooting ansible provisioning?
```
$ ansible all -i '192.168.0.19,' -u pi -m setup
```

### Todo
* Manage the celluar radio config!  Sorry, this just runs on wifi hubs for now.
* Add a play (or script) to automatically burn a base raspbian immage
* Set systemd service configs to run as hub_user instead of hard coded pi
* Wrap this in docker so people don't need ansible and ssh configuration
* Use dynamic inventory to discover all hubs on a lcoal network 
* Implement systemd timers (this really needs to be dynamic and I don't know enough about the requirement so I'm not going to hard coded the 8am-6pm schedule in the first go!)
* Switch the hub_code role over and deploy the output of a python build process (at least freeze the code from arm and copy binaries
