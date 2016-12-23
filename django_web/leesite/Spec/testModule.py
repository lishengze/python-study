import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
print os.path.abspath(__file__)
print os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print BASE_DIR