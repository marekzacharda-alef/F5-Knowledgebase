## on mgmt linux 
1. Login to docker.io  ```sudo docker login -u 654561518131654```
2. Create repository in docker.io    
3. Build new image ```sudo docker build . -t 654561518131654/nginx811``` 
   note > Dockerfile must be created before.
4. Push to public repository ```sudo docker push 654561518131654/nginx811:latest```



## on Volterra Cluster add your docker.io login credential to your namespace  
Metadata
Name:docker-io
Labels
Server FQDN:docker.io
User Name:654561518131654
Password

