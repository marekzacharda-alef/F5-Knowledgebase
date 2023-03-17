# apply application into namespace 

kubectl apply -f ./yml/00-namespace.yml --kubeconfig ves_system_alef-hu-app-vmw_kubeconfig_global.yaml
kubectl apply -f ./yml/01-secret.yml -n alef-sk --kubeconfig ves_system_alef-hu-app-vmw_kubeconfig_global.yaml
kubectl apply -f ./yml/04-wordpress-pvc.yml -n alef-sk --kubeconfig ves_system_alef-hu-app-vmw_kubeconfig_global.yaml
kubectl apply -f ./yml/05-wordpress-deployment.yml -n alef-sk --kubeconfig ves_system_alef-hu-app-vmw_kubeconfig_global.yaml
kubectl apply -f ./yml/06-wordpress-service.yml -n alef-sk --kubeconfig ves_system_alef-hu-app-vmw_kubeconfig_global.yaml




