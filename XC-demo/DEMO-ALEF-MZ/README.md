# Wordpress on F5 XC



## Deployment

- when using with regular K8s, I need to create the `namespace` and then create objects in that `namespace`
```shell
kubectl apply -f ./yml/00-namespace.yml
kubectl apply -f ./yml/01-secret.yml -n alef-sk
kubectl apply -f ./yml/02-mysql-statefullset.yml -n alef-sk
```

- scaling works only via editing `05-wordpress-deployment.yml` -> `replicas: X`

```shell
kubectl apply -f ./yml/05-wordpress-deployment.yml -n alef-sk
```





### Fixing issues

For some reason the FQDN in Wordpress is not set correctly, the updates below will fix it. First it's mandatory to run the initial setup. Go to: `https://wordpress.xc.aleflab.hu/wp-admin/install.php` to conclude the setup then follow below with the MySQL fix.

**MySQL**
https://wordpress.xc.aleflab.hu/wp-admin/install.php
```shell
# Pod terminalk
mysql -u wordpress -p wordpress
```

```sql
UPDATE wp_options SET option_value='https://wordpress-demo.xc.f5demo.app' WHERE option_name='home' LIMIT 1;
UPDATE wp_options SET option_value='https://wordpress-demo.xc.f5demo.app' WHERE option_name='siteurl' LIMIT 1;
```



### Importing a test data

1. Download the theme unit [test data](data/theme-unit-test-data.xml)
2. Go to `Tools` > `Import` > `WordPress` in order to import test data onto your WordPress website.
3. On the same page `Run Importer`
4. Choose a xml file for content import on your computer -> `Upload and import`.
5. Check the `Download and import file attachments` box and click `Submit`.



## Multisite deployment

### mysql TCP LB



**TCP Load balancer**

![CleanShot 2022-11-29 at 21.52.20](img/README/CleanShot%202022-11-29%20at%2021.52.20.png)

**Origin Pool**

![CleanShot 2022-11-29 at 21.52.52](img/README/CleanShot%202022-11-29%20at%2021.52.52.png)

**Publishing**

![CleanShot 2022-11-29 at 21.50.46](img/README/CleanShot%202022-11-29%20at%2021.50.46.png)

**App Traffic**

![CleanShot 2022-11-30 at 11.32.25](img/README/CleanShot%202022-11-30%20at%2011.32.25.png)

## Delete the LB

```bash
vesctl configuration delete http_loadbalancer alef-sk -n alef-sk
vesctl configuration delete origin_pool alef-sk-pool -n alef-sk
```

