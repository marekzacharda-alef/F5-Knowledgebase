1. Download kubectl file
2. appl y deployment with command > 
```
kubectl apply -f alef-sk-indivdual-k8s.yaml --kubeconfig ves_default_alef-sk-indivdual-k8s.yaml
```



Add K8S sites 

1. need to assign Virtual Site to Site (physical CE) 
2. manage> virtual site  has to have == with sa same to  Selector Expression ves.io/siteName  == alef-sk

3. site > metadata  ves.io/siteName   alef-sk
