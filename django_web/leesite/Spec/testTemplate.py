from django import template

import os
import sys

def testTemplate ():
	t = template.Template('My name is {{ name }}')
	c = template.Context({'name': 'Adele'})
	print t.render(c)

if __name__ == "__main__":
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "leesite.settings")
	testTemplate()

