# Speaking Eye

![](https://github.com/alena-bartosh/speaking-eye/workflows/Lint%20&%20Tests/badge.svg)
[![codecov](https://codecov.io/gh/alena-bartosh/speaking-eye/branch/master/graph/badge.svg)](https://codecov.io/gh/alena-bartosh/speaking-eye)

Please read more information in [project README](https://github.com/alena-bartosh/speaking-eye).

### 👀 Looking at

- your working hours/breaks
- activity in any apps (IDE, browser tabs, terminal, etc.)
- distracting activity (custom list of apps/time limits)

### 📯 Speaking about

- your activity on the computer
- overtime
- time to take a break
- distracting apps if you spend a lot of time there

### Installation

The simplest way of installation is

```sh
pip install speaking-eye
```

Also you will need some system dependencies.

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

After it you can run Speaking Eye with command line or using Applications Menu in your desktop environment.

```sh
$ speaking-eye
```

To install application for developing please read steps on [wiki pages](https://github.com/alena-bartosh/speaking-eye/wiki/Installation).

### Demo

[![speaking-eye demo](https://img.youtube.com/vi/0J-ZlpQaWHA/0.jpg)](https://youtu.be/0J-ZlpQaWHA)
