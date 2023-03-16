## Deployment

- when using with regular K8s, I need to create the `namespace` and then create objects in that `namespace`
```shell
kubectl apply -f ./yml/00-namespace.yml
kubectl apply -f ./yml/01-secret.yml -n alef-sk
kubectl apply -f ./yml/02-mysql-statefullset.yml -n alef-sk
```
#apply arkadia in k8s v namespace alef-sk
kubectl apply -f arkadia.yaml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml


- scaling works only via editing `05-wordpress-deployment.yml` -> `replicas: X`

```shell
kubectl apply -f ./yml/05-wordpress-deployment.yml
```

```marek shell notes
kubectl apply -f 00-namespace.yml --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f 01-secret.yml --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f 02-mysql-statefullset.yml --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f 03-mysql-service.yml --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f 04-wordpress-pvc.yml --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f 05-wordpress-deployment.yml --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml