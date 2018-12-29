# Automatic hub configuration (woker)

### Preparation
* Do a fresh install of noobs, set up a username (probably pi) and password, and configure the network if required
* Install ansible on your workstation (one time only, assumes ubuntu 18.04)
  ** ```
  $ sudo apt-get install python3-pip
  $ pip3 install --user ansible
  $ grep -q -F 'PATH=\$PATH:~/.local/bin' ~/.bashrc || echo 'PATH=$PATH:~/.local/bin' >> ~/.bashrc
  ```
* Set up default hub credentials
   ** ```
$ ssh-keygen -t ed25519 -f secrets/hub_default -o -a 100 -C "default_configurator_user_from_secrets@configurator_host"
$ ssh-add secrets/hub_credentials/hub_default
```


### Configure a single hub
```
$ ansible-playbook plays/provision_hub.yml -i 192.168.0.19, -u pi --become --extra-vars "hub_hostname=mccool_hub_01 hub_google_pubsub_topic=mccool_test_topic hub_google_project_id=mccool_gcp_project hub_google_application_credentials=REDACTED"
```

This will log into an empty raspbi at 192.168.0.19 as usrename pi.  On the first run you may need to add -k to the ansible command in order to be prompted for a password before the key is installed.  It's however you froze the base OS image.  Once it logs in, it will add an ssh key as generated above and future runs won't need interaction. It will configure it to be a receiver hub named mccool_hub_01, using a pubsub topic of mccool_test_topic, a project id of mccool_gcp_project, and... Well you get the point, replace anything after hub.yml with what you want to change.

In the future this will support multiple hubs at once, and let you define sets of hubs to be provisioned and their secrets/variables.  For now we're just doing this one at a time.


### From the pi itself
Code runs from /usr/local/sobun.
Config is in /usr/local/sobun/config

```
systemctl restart dream-sniffer 0
systemctl restart dream-sniffer 1
systemctl restart dream-sniffer 2
systemctl restart dream-sniffer 3
systemctl restart dream-batcher
systemctl restart dream-syncer
```

### Developers guide
* Change python code in dream/ all you want.
* Reprovision hub (or come up with a play to just restart services, or just remember you can always)
``` 
sudo rsystemctl restartstart dream-sniffer@{0..3}
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