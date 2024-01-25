# BIG-IP Configuration utility  CVE-2023-46747 a  CVE-2023-46748

Odporúčame fixnúť zraniteľnosti, ktoré vyšli na konci minulého roka. 
Cez zraniteľnosť CVE-2023-46747 dokážu neautentifikovaný útočníci so sieťovým prístupom k manažmentu BIGIP systému spustiť ľubovoľné systémové príkazy. Následne cez zraniteľnosť CVE-2023-46748 dokážu vykonávať aj SQL injekcie. 
týmto zraniteľnostiam nepodlieha dátová časť, iba manažment. 
```
Zraniteľné sú tieto verzie BIGIP. 
17.1.0 - 17.1.1	
16.1.0 - 16.1.4	
15.1.0 - 15.1.10	
14.1.0 - 14.1.5	
13.1.0 - 13.1.5
```
Odporúčame  upgradovať na verzie kde je zraniteľnosť už fixovaná podľa tabuľky v  https://my.f5.com/manage/s/article/K000137353. alebo aplikovať fix podľa odporúčania F5. 

Ak by ste potrebovali pomocť, sme vám k dispozicií. 


