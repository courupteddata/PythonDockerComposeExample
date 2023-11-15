## K3S

Create namespace
```shell
cat ../common/manifest/namespace.yaml |  docker exec -i k3s-server-1 kubectl apply -f -
```

Create Rabbitmq instance
```shell
cat ../rabbitmq-deployment.yaml |  docker exec -i k3s-server-1 kubectl apply -f -
```

Deploy service
```shell
cat ../external_file_in_out/manifest/deployment.yaml| docker exec -i k3s-server-1 kubectl apply -f -
```

### Troubleshooting

```shell
kubectl get svc -n compose-example
kubectl get pods -n compose-example
kubectl logs -n compose-example <pod-name>
```

FQDN for pods in this example would be something like: `rabbitmq.compose-example.svc.cluster.local`
