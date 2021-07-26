### 2021-07-26:
___

The best option for SE users - custom deb package and installation with ```sudo apt```.
It allows adding system dependencies and reduce the number of commands needed to install.

For creating executable file [PyInstaller](https://github.com/pyinstaller/pyinstaller) can be used.
It collects apps dependencies (requirements) into a single package including the active Python interpreter.

###### NOTES:
___

***Q:*** Why we can not use Docker?  
***A:*** Because SE uses x11 window manager & xprop utility. And the Docker container has its own system, so no windows will change.

#### Commands for pyinstaller in virtual env:

```sh
$ pip install pyinstaller
$ pyinstaller --clean \
      --onefile \
      --strip \
      --add-data="config:config" \
      --add-data="icon:icon" \
      --add-data="dest:dest" \
      --add-data="i18n:i18n" \
      --add-data="README.md:." \
      ./src/speaking_eye.py
```
Executable file will be built in ```speaking-eye/dist``` folder.

#### BACKLOG 
___

- [ ] Fix bug with favicon (it was added with changes in current branch)
- [ ] Close TODOs related to config, raw data files
- [ ] Update code for working with files (we can get paths not only from current working dir (src) like now)
- [ ] Create speaking-eye file with pyinstaller
- [ ] Make sure everything works as expected with pyinstaller file
- [ ] CI related step: Automate pyinstaller SE building and putting it into repo. 
    It can be done in docker for less file size (run pyinstaller command from docker)
- [ ] Create [github release](https://github.com/alena-bartosh/speaking-eye/releases) with the newest SE version
- [ ] Add link to releases into README
- [ ] Build the deb package
- [ ] Update the way to work with systemd
- [ ] Revise Makefile
