# Speaking Eye

### System dependencies
```sh
sudo apt-get install \
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
