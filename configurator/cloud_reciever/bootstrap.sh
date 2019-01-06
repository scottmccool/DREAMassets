#!/bin/sh


echo
echo "======="
echo <<'EOF'
This script sets up a minimal framework for the DREAM hubs to send data to.
It assumes you have configured a gcloud project and logged into it, setting it's config
with 
  $ gcloud auth login --project "<your project>"
in this session.  From there on we will create:
* Pubsub topic
* Hub service account and key with permission to publish to the topic
* Cloud function to pull from pubsub and persist the observation

It is likely this script can be run repeatedly, but you will see errors.

For any serious usage, this should be refactored into terraform or something more flexible.
EOF
echo "======="
echo

PROJECT=`gcloud config get-value project`

echo "Working in project: ${PROJECT}"
echo

mkdir -p secrets > /dev/null 2>&1

echo
echo "-----"
echo "Creating pubsub topic"
echo "----"
echo

echo "Enter topic name to create: "
read -p "Enter topic name for hubs to publish to: " TOPIC

gcloud pubsub topics create ${TOPIC}

echo
echo "-----"
echo "Creating hub service account"
echo "----"
echo

gcloud iam service-accounts create dream-hub --display-name dream-hub

echo
echo "-----"
echo "Creating hub key and authorizing to publish to hub_observations"
echo "----"
echo

if [ -f secrets/hub-${TOPIC}-publisher.json ]
then
  echo "Found existing hub credential file.  Skipping key creatoin."
else
  gcloud iam service-accounts keys create secrets/hub-${TOPIC}-publisher.json --iam-account dream-hub@${PROJECT}.iam.gserviceaccount.com
fi

gcloud beta pubsub topics add-iam-policy-binding ${TOPIC} --member=serviceAccount:dream-hub@${PROJECT}.iam.gserviceaccount.com --role roles/pubsub.publisher

echo
echo "-----"
echo "Creating cloud function to persist data from pubsub"
echo "-----"





echo "That's all I know how to do.  You should ship secrets/hub-publisher.json to the Raspberry pi's via the configurator code."
echo "The project name is: ${PROJECT}"
echo "The topic name is: ${TOPIC}"

echo "To provision a hub to use this:"
echo
echo "cp secrets/hub-${TOPIC}-publisher.json ../../secrets/hub_credentials/"
echo "cd ../ansible"
echo "ansible-playbook plays/provision_hub.yml -i hub_inventories/single_development_hub.ini --extra-vars=\"hub_google_project_id=${PROJECT} hub_google_pubsub_topic=${TOPIC} hub_google_application_credentials=hub-${TOPIC}-publisher.json\""
echo
echo "You will want to keep those details and subscriptions!"