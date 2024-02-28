#!/bin/bash
set -e

# remove the namespace
kubectl config set-context --current --namespace=default

# remove the resources
kubectl delete -f 3.yaml
kubectl delete -f 2.json
kubectl delete -f 1.json
