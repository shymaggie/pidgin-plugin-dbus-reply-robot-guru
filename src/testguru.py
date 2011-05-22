#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
just some test and experiment 

'''
import re,configGuru
import cPickle as p

message = " Q:abcdefg你好吗？A:higklmn你好"
regex = re.compile(configGuru.getProperty("command", "regexqa"))
regex1 = re.compile(configGuru.getProperty("command", "regexq"))
regex2 = re.compile(configGuru.getProperty("command", "regexa"))
regex3 = re.compile(configGuru.getProperty("command", "bye"))


message = message.strip()
if regex.match(message):
    print True
else:
    print False

match1 = regex1.search(message)
if match1:
    print match1.group(1)

match2 = regex2.search(message)
if match2:
    print message[match2.end():]

str1 ="hello"
str2 = "Hell"

print cmp(str1.upper(),str2.upper())

#message = "再见"
#match3 = regex3.search(message)
#if match3:
#    print match3.group(0)

sessions ={}
sessions[12345]="hello"
print sessions[12345]
myfile = file("data/hello.txt","w")
p.dump(sessions,myfile)