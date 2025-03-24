# DJI Tello - Python

![DJI Tello Drone](./img/dji_tello_drone.jpg)

This software makes use of: [DJI Tello Python API](https://djitellopy.readthedocs.io/en/latest/tello/)

## Important

The owner of this project assumes no responsibility for any damage, issues, or legal consequences resulting from the use of this software. Use it at your own risk and ensure compliance with all applicable laws and regulations.

**Compatibility notes**

Currently, this project is only fully supported on macOS. Users on other operating systems might encounter compatibility issues or limitations when running the project. Please ensure you are using macOS for the best experience.

## Minimum requirements

The code is writen and tested with following requirements:

[![Static](https://img.shields.io/badge/python->=3.12.x-green)](https://python.org)
[![Static](https://img.shields.io/badge/hidapi-==0.14.0-green)](https://github.com/trezor/cython-hidapi)
[![Static](https://img.shields.io/badge/djitellopy-==2.5.0-green)](https://github.com/damiafuentes/DJITelloPy)
[![Static](https://img.shields.io/badge/opencv-==4.11.0.86-green)](https://github.com/opencv/opencv-python)
[![Static](https://img.shields.io/badge/numpy-==2.2.4-green)](https://numpy.org)

## Installation

```shell
# clone repository
$ git clone https://github.com/Lupin3000/Tello-Python.git

# change into cloned root directory
$ cd Tello-Python/

# create Python virtualenv (optional but recommended)
$ python3 -m venv venv

# activate Python virtualenv
$ source venv/bin/activate

# update pip (optional)
(venv) $ pip3 install -U pip

# install required dependencies
(venv) $ pip3 install -r requirements.txt
```

## Predefined controllers

- Google Stadia-Controller

## Run application

1. Connect controller (_verify mapping in file `config/configuration.ini`_)
2. Turn on Tello Drone (_in best case the drone is 100% charged_)
3. Connect WLAN to Tello Drone AP
4. Run application (_use file `main.py`_)

```shell
# run application
(venv) $ python3 main.py
```

## Configuration

Inside file `main.py` you can modify following constants:

- CONTROLLER: name of section inside file `config/configuration.ini`
- SPEED: integer value between 0 and 100
- STREAM: True (_video stream on_) or False (_video stream off_)
- WINDOW_NAME: Title of video stream window

## Open items

- Take picture or record video by controller buttons
- Linux compatibility (_via Python evdev_)
- Add drone actions (_like flip_) by controller buttons
- Add basic configurations for other controllers then Stadia
