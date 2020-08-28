#!/usr/bin/env bash

case "$1" in
  update)
    SERVICE=$2

    if [ -z "$SERVICE" ]; then
      echo "Updating modeling stack"
      SERVICE="modeling"
    fi

    git pull
    sudo docker-compose -f prod-docker-compose.yml build $SERVICE
    sudo docker-compose -f prod-docker-compose.yml up -d $SERVICE
    ;;
  *)
    echo $"Usage: $0 update <stack>"
    exit 1
esac
