# -*- coding: utf-8 -*-
"""
Created on Sun Aug  3 16:38:03 2014

@author: huapu
"""

# Put in const.py...:
class _const:
    class ConstError(TypeError): pass
    def __setattr__(self,name,value):
        if self.__dict__.has_key(name):
            raise self.ConstError, "Can't rebind const(%s)"%name
        self.__dict__[name]=value
import sys
sys.modules[__name__]=_const()