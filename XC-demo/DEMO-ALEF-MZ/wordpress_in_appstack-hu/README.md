# create namespace 
kubectl apply -f ./yml/00-namespace.yml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml

# apply application into namespace 

kubectl apply -f 00-namespace.yml --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f ./yml/01-secret.yml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f ./yml/02-mysql-statefullset.yml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f ./yml/03-mysql-service.yml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f ./yml/04-wordpress-pvc.yml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f ./yml/05-wordpress-deployment.yml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml
kubectl apply -f ./yml/06-wordpress-service.yml -n alef-sk --kubeconfig ves_system_alef-sk-appstack_kubeconfig_global.yaml


# wordpress bug 
### Fixing issues

For some reason the FQDN in Wordpress is not set correctly, the updates below will fix it. First it's mandatory to run the initial setup. Go to: `https://wordpress.xc.aleflab.hu/wp-admin/install.php` to conclude the setup then follow below with the MySQL fix.

**MySQL**
https://https://wordpress.xc.aleflab.hu/wp-admin/install.php
```shell
# Pod terminalk
mysql -u wordpress -p wordpress
```

```sql
UPDATE wp_options SET option_value='https://wordpress.xc.aleflab.hu' WHERE option_name='home' LIMIT 1;
UPDATE wp_options SET option_value='https://wordpress.xc.aleflab.hu' WHERE option_name='siteurl' LIMIT 1;
```
