![banner](res/banner.png)

# Introduction
Small and simple GUI tool to gather your computer's information using Python.
[![Pylint](https://github.com/diamant3/SYSIG/actions/workflows/Pylint.yml/badge.svg)](https://github.com/diamant3/SYSIG/actions/workflows/Pylint.yml)

## Demo
https://github.com/diamant3/SYSIG/assets/71203851/b0454b5e-e3cb-4050-8f3c-853fb65eed16

## Run
Upgrade pip then install required modules:

```shell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

then run:

```shell
python sysig.py
```

> [!Important]
> If you see a `ModuleNotFoundError: No module named 'distutils'` error, please install
> setuptools using the command `python -m pip install setuptools`.

> [!Note]
> This is just a hobby project and all information you will see in the app is based on the Python modules's detection capabilities. Thank you for your understanding!

## Credits
- [Hardware detection in python](https://www.thepythoncode.com/article/get-hardware-system-information-python)
- [psutil](https://github.com/giampaolo/psutil)
- [DearPyGUI](https://github.com/hoffstadt/dearPyGui/)
- [py-cpuinfo](https://github.com/workhorsy/py-cpuinfo)

## Contribute
Open for any type of contribution, thanks!
