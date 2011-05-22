#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
struct for storing answerdata
Created on May 20, 2011
@author: maple
'''
import time

#答案结构，包括答案本身和最后使用时间
class answer:
    ans = None
    time = time.time()
    
    def __init__(self,ans):
        self.ans = ans      