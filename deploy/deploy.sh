#!/bin/bash
set -e

apt install nodejs -y > /dev/null

# generate json files and apply
node generate-json.js
kubectl apply -f 1.json
kubectl apply -f 2.json
kubectl apply -f 3.yaml

# change the namespace
kubectl config set-context --current --namespace=social-network
