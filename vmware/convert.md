## Convert vmdk format to flat vmdk to be eble to run in VMWARE on your local ntb. 

"c:\Program Files\Oracle\VirtualBox\VBoxManage.exe"  clonehd Docker_Host-disk1.vmdk out.vmdk -format VMDK -variant Fixed,ESX

## Convert vmdk format to flat vmdk to be eble to run in VMWARE on VMWARE ESX. 


vmkfstools -i /vmfs/volumes/datastore/...../disk.vmdk  /vmfs/volumes/datastore/...../disk-ok.vmdk



