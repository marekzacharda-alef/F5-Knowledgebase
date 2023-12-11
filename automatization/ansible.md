## Setting virtaul environment 
link https://www.freecodecamp.org/news/virtualenv-with-virtualenvwrapper-on-ubuntu-18-04/ 
# vytvorit virtualni prostredi
mkvirtualenv -p /usr/bin/python3 ansible
 
# upgradovat pip
pip install --upgrade pip
 
# instalace ansible
pip install ansible
 
# instalace F5 collection
ansible-galaxy collection install f5networks.f5_modules
 
 
# pri kazdem prihlaseni se na server je potreba virtualni prostredi aktivovat
workon ansible
 
# pokud uzivatel potrebuje virtualni prostredi deaktivovat
deactivate

