# DJI Tello - Python

## Important

The owner of this project assumes no responsibility for any damage, issues, or legal consequences resulting from the use of this software. Use it at your own risk and ensure compliance with all applicable laws and regulations.

**Compatibility notes**

Currently, this project is only fully supported on macOS. Users on other operating systems might encounter compatibility issues or limitations when running the project. Please ensure you are using macOS for the best experience.

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

# install required dependencies
(venv) $ pip3 install -r requirements.txt
```

## Run application

1. Connect controller 
2. Turn on Tello Drone
3. Connect WLAN to Tello Drone AP
4. Run application (_main.py)

```shell
# run application
(venv) $ python3 main.py
```
