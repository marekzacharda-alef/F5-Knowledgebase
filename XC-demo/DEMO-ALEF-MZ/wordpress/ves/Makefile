#all: namespace, pool, lb

namespace:
	vesctl configuration create namespace alef-sk

pool:
	vesctl configuration apply origin_pool -i ./alef-sk-pool.yml

lb:
	vesctl configuration apply http_loadbalancer -i ./alef-sk-lb.yml

tcp-lk:
	vesctl configuration apply tcp_loadbalancer -i ./alef-sk-tcp-lb.yml

delete:
	vesctl configuration delete http_loadbalancer alef-sk -n alef-sk
	vesctl configuration delete origin_pool alef-sk-pool -n alef-sk
