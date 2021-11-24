#!/usr/bin/python
from os import system as r
import random
import string


for i in range(101, 105):
    r('mkdir -p {}'.format(i))
    r("ssh-keygen -t rsa -N '' -f {}/ssh_key".format(i))

