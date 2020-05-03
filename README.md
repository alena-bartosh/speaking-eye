# Speaking Eye

### :eyes: Looking at
* your working hours/breaks
* activity in any apps (IDE, browser tabs, terminal, etc.)
* distracting activity (custom list of apps/time limits)

### :postal_horn: Speaking about
* your activity on the computer
* time to take a break
* overtime
* distracting apps if you spend a lot of time there

### System dependencies
```sh
sudo apt-get install \
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

### Code conduction
* Use [Gitmoji](https://gitmoji.carloscuesta.me) for commit messages
