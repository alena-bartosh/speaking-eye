# Speaking Eye

![](https://github.com/alena-bartosh/speaking-eye/workflows/Lint%20&%20Tests/badge.svg)

### :eyes: Looking at
- [x] your working hours/breaks
- [x] activity in any apps (IDE, browser tabs, terminal, etc.)
- [ ] distracting activity (custom list of apps/time limits)

### :postal_horn: Speaking about
- [x] your activity on the computer
- [x] overtime
- [x] time to take a break
- [ ] distracting apps if you spend a lot of time there

### System dependencies
```sh
sudo apt-get install \
    python3-dev \
    python3-venv \
    libcairo2-dev \
    libgirepository1.0-dev \
    python3-gi \
    gir1.2-gtk-3.0 \
    gir1.2-wnck-3.0 \
    gir1.2-appindicator3-0.1 \
    gir1.2-notify-0.7
```

### Setup
```sh
git clone https://github.com/alena-bartosh/speaking-eye.git && \
cd speaking-eye && \
python3 -m venv .env && \
source .env/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt
```

### Usage
```
python3 speaking_eye.py --help
usage: speaking_eye.py [-h] [--log-level] [-c]

[speaking-eye] Track & analyze your computer activity

optional arguments:
  -h, --help      show this help message and exit
  --log-level     debug/info/warning/error
  -c , --config   config path
```

### One-time start
```
./start.sh
```

### Set auto start
Speaking Eye will automatically turn on after system startup
```
 ./install_systemd.sh 
```

### Run unittests
```
./run_unittests.sh
```

### Code conduction
* Use [Gitmoji](https://gitmoji.carloscuesta.me) for commit messages
