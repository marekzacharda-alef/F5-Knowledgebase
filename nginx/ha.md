## installation & config  of HA nginxs 

#install

```
apt-get install nginx-ha-keepalived
```

```
apt-get install nginx-sync
```
#config
run one by one 
```
nginx-ha-setup
```

config in /etc/keepalived/keepalived.conf 
#check in which state is node
```
cat /var/run/nginx-ha-keepalived.state
STATE=MASTER
```
#source
https://docs.nginx.com/nginx/admin-guide/high-availability/ha-keepalived/
https://docs.nginx.com/nginx/admin-guide/high-availability/configuration-sharing/
