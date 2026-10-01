ACME articel on devcentral. 

https://community.f5.com/t/automatic-certificate-management-with-acmev2-in-f5-big-ip/77193

Automatic Certificate Management with ACMEv2 in F5 BIG-IP
Articles
F5 Technical Articles
application-delivery
,
security
,
management
,
certificate
,
lets-encrypt

mendes
post by mendes na jún 12
One of the most anticipated features of F5 BIG-IP is integration with ACMEv2.

With the General Availability of BIG-IP 21.1.0 on May/26, this feature came into being.

image_346795.png
image_346795.png
2014×790 121 KB
In this tutorial, we are going to configure it, using Let’s Encrypt as the CA. The domain for which we are generating/renewing certificates is carlosf5lab.lat.

The official docs for this feature are located in SSL Certificate Management | BIG-IP Documentation.

Pre-requisite 1: DNS Resolver that can reach the internet (at least the CA endpoints).

In this case, we are using the native DNS Resolver that comes with BIG-IP.

image_346795.png
image_346795.png
842×532 33.6 KB
Pre-requisite 2: The internal proxy that will make the connection with the CA.

image_346795.png
image_346795.png
1126×754 41.9 KB
image_346795.png
image_346795.png
3155×556 63.9 KB
Pre-requisite 3: a self signed SSL certificate that the ACMEv2 protocol uses as the identifier for a device account. You don’t have to fill the Subject Alternative Name. For the Common Name, an e-mail contact is advised.

image_346795.png
1756×1736 142 KB
image_346795.png
image_346795.png
2137×1542 172 KB
Now, we are going to create the ACME Provider object. Give it a name, and select the internal proxy previously created. For the CA Certificate to enable the secure connection with the Directory URL, you can use the default ca-bundle.crt.

The Directory URL is the endpoint for the ACMEv2 protocol. In Let’s Encrypt case, it is https://acme-v02.api.letsencrypt.org/directory

For the Account Key, choose the previously created self-signed certificate. For the trickier part of all, the field “Contacts” is mandatory, and it must be an URL. That’s why you must use the format mailto:email_address. Check the Terms and Conditions, and the Create Account boxes.

image_346795.png
1751×1887 182 KB
After a while, the Account Status must read as “Valid”.

image_346795.png
image_346795.png
3150×505 78.1 KB
To prove you own the domain whose certificate Let’s Encrypt is going to create/renew, it must be pointing to an IP (A Record) where you must have your Virtual Server listening on Port 80 configured to respond to the ACMEv2 Challenge. (In this specific lab, the domain carlosf5lab.lat points to a Public IP mapped to an internal IP).

image_346795.png
1626×2393 214 KB
Now you can order your first certificate via ACMEv2 on BIG-IP:

image_346795.png
1636×2346 196 KB
After a while, the Key tab should read something like:

image_346795.png
image_346795.png
1876×1208 131 KB
Which means your certificate was generated:

image_346795.png
image_346795.png
2089×1968 217 KB
To track the ACME Provider, you can check its statistics:

image_346795.png
image_346795.png
3239×1287 186 KB
