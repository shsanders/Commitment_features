#!/usr/bin/python

import pysvn
import pdb

passwd = "PASSWORD" #this is not correct; just making this private.

def login(realm, username, may_save):
   return True, username, passwd, False

def update():
   client = pysvn.Client()
   client.update("../../features/bounds_dump")
   

if __name__ == "__main__":
   update()
