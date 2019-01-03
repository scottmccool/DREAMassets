
Intended to turn the rest of sobun/ directory into frozen binaries for distribution to a hub (probably by ansible provisioning scripts)

Version 0.1
==
* Build:
# Edit version # in setup.py
# Build package
```
$ cd ../ && python3 setup.py sdist 
```
# Point ../configurator/ansible/hub_inventories env variable at your new version
# Deploy it to a hub
*** THIS MAY WIPE OUT ANY DATA CACHED ON THE HUB ***
```
$ cd ../configurator/ansible
$ ansible-playbook -i hub_inventories/single_development_hub.ini plays/update_dream_code.yml
```

* Test:
*** We dont need^H^H^H^Hhave no stinking tests! ***