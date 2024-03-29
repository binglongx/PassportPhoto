# PassportPhoto
Passport Photo Cropper: GUI tool to crop your photo to meet requirements of passport photo of China/USA

# How to run

The tool is a Python GUI application. You need to have Python to run this tool. Download `PassportPhoto.py` here to your local disk, and run

`python PassportPhoto.py`

or 

`python3 PassportPhoto.py`

Follow the instructions on the right side of the main window. 

It basically allows you to load an image file from your disk, and then you can move and zoom the photo to fit a template dictated by passport photo requirements of a country you choose.

See https://binglongx.com/2023/06/26/passport-photo-cropper-python-gui-app/ for some examples of usage.

# Additional Notes

* All the source code is in one single `PassportPhoto.py` file.
* If you run into errors, read the first few lines. You may need to run `pip install` for some required packages.
* Check the last few lines if you need to manually change the country to crop passport photo for.
* The code currently has photo templates for passports of China and USA, as Python classes. It is relative simple to support other countries by adding new templates.
