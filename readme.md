# DJI Tello - Python

![DJI Tello Drone](./img/dji_tello_drone.jpg)

This software makes use of: [DJI Tello Python API](https://djitellopy.readthedocs.io/en/latest/tello/)

## Important

The owner of this project assumes no responsibility for any damage, issues, or legal consequences resulting from the use of this software. Use it at your own risk and ensure compliance with all applicable laws and regulations.

## Installation

### Minimum requirements

The code is written and tested with following requirements:

| OS            | Python                                                                                                         |
|---------------|----------------------------------------------------------------------------------------------------------------|
| macOS Sequoia | [![Static](https://img.shields.io/badge/python-==3.12.2-green)](https://python.org)                            | 
| macOS Sequoia | [![Static](https://img.shields.io/badge/hidapi-==0.14.0-green)](https://github.com/trezor/cython-hidapi)       |
| macOS Sequoia | [![Static](https://img.shields.io/badge/djitellopy-==2.5.0-green)](https://github.com/damiafuentes/DJITelloPy) |
| macOS Sequoia | [![Static](https://img.shields.io/badge/opencv-==4.11.0.86-green)](https://github.com/opencv/opencv-python)    |
| macOS Sequoia | [![Static](https://img.shields.io/badge/numpy-==2.2.4-green)](https://numpy.org)                               |
| Debian 12     | [![Static](https://img.shields.io/badge/python-==3.11.12-green)](https://python.org)                           | 
| Debian 12     | [![Static](https://img.shields.io/badge/evdev-==1.9.1-green)](https://github.com/gvalkov/python-evdev)         |
| Debian 12     | [![Static](https://img.shields.io/badge/djitellopy-==2.5.0-green)](https://github.com/damiafuentes/DJITelloPy) |
| Debian 12     | [![Static](https://img.shields.io/badge/opencv-==4.11.0.86-green)](https://github.com/opencv/opencv-python)    |
| Debian 12     | [![Static](https://img.shields.io/badge/numpy-==2.2.4-green)](https://numpy.org)                               |

### Prepare Python project

### macOS

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
(venv) $ pip3 install -r macos-requirements.txt

# show packages (optional)
(venv) $ pip3 freeze
```

### Linux

**root**

The root user should install required system-wide Python packages and allow permissions to `/dev/input/*`.

```shell
# update packages (optional)
$ apt update && apt upgrade -y

# install required packages
$ apt install -y apt install python3-venv python3-pip libgl1

# provide user permissions to /dev/input/*
$ usermod -aG input [USERNAME]
```

**user**

The user should install required project Python packages via virtualenv.

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
(venv) $ pip3 install -r linux-requirements.txt

# show packages (optional)
(venv) $ pip3 freeze
```

## Usage

### Run application and fly

1. **Mandatory:** Connect controller by USB or Bluetooth (_verify mapping in file `config/configuration.ini`_).
2. **Mandatory:** Turn on Tello Drone (_in best case the drone is 100% charged_).
3. **Mandatory:** Connect WLAN of your computer to the Tello Drone AP (_Default is: TELLO-??????_).
4. **Optional:** Decide whether you want to enable or disable the HUD (_for video streaming_).
5. **Optional:** Check your surroundings to see if you can fly the drone safely.
6. **Mandatory:** Run the Python application (_use file `main.py`_).

```shell
# run application
(venv) $ python3 main.py
```

> After takeoff, the Tello sensors require a few seconds to calibrate. During this time, the drone will not respond to controller inputs.

## Configuration

### Predefined controllers

- **Google:** Stadia-Controller
- **Sony:** DualSense Wireless Controller

> You also can add and use other controllers. Please note that the controller must have at least 2 analog sticks! Simply create another section in the `config/configuration.ini` file with the necessary information. Then specify the name of the section in the `main.py` file by adapting the constant: CONTROLLER value.

- **Stadia [Y] - DualSense [&#x25B2;]:** for drone takeoff.
- **Stadia [A] - DualSense [X]:** for drone landing.
- **Stadia [X] - DualSense [&#x25FC;]:** for capture a photo (_picture will be saved as PNG into directory "photos"_).
- **Left analog stick:** move up, move down, rotation clockwise and rotation counterclockwise.
- **Right analog stick:** move forward, move backward, move left and move right.

> The photos are created as PNG files (_with timestamp in name_) during the live stream. The resolution and quality therefore depend on the live stream. The `photos` folder will be created automatically if it doesn't already exist. If you turn off the stream, you cannot save pictures!

### Own configuration

Inside file `main.py` you can modify following constants:

- **CONTROLLER:** name of section inside file `config/configuration.ini` (_which controller you use to fly_).
- **SPEED:** integer value between 1 and 100 (_the higher the value, the faster the drone flies_).
- **STREAM:** True to fly with HUD (_video stream on_) or False for no HUD (_video stream off_).
- **WINDOW_NAME:** Title of HUD (_video stream_) window.

> You should not change the values of the constants DELAY and SHUTDOWN. This can cause problems if you don't know 100% what you are changing.

## Notes

### Compatibility

Currently, this project is only fully supported on macOS. Users on other operating systems might encounter compatibility issues or limitations when running the project. Please ensure you are using macOS for the best experience.

### Open items

- Linux compatibility (_via Python evdev_) -> in development
- Record video by controller buttons
- Add drone actions (_like flip_) by controller buttons
