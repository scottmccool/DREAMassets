Deploys google cloud services to receive sensor data from hubs

This should really be some terraform modules.

Instead, make sure you set up a google cloud project.

Log into it:
$  gcloud auth login --project "<your project>"

And run 
$ ./bootstrap.sh

It will spit out credentials you will now pass to ansible for hub configuration (by copying a secrets/ file over and by specifying topic and project name variables; it'll tell you what to do)
