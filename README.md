# lab2csv

Converts 3B Scientific `lab` files produced by Science Studio to `csv` files that can be read by Origin etc.

Every table inside a `lab` file, which is located inside a `vecteur` section, will be put into separate column, so expect *many* duplicates.

You can either use GUI or simply Drag'n'Drop `lab` file onto `exe` to immediately convert it to `csv`.

Download: https://github.com/xtotdam/lab2csv/releases


![Screenshot](https://user-images.githubusercontent.com/5108025/157852537-447f7085-c3c8-4d8c-9b0d-95c9ce0c77af.png)


### Requirements to build

* `pyinstaller`
* `PySimpleGUI`
* `unidecode`
