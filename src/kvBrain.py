#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
A key-value storage for guru
Created on May 18, 2011
@author: maple
'''
import string,time,configGuru,traceback
import cPickle as p
from answer import answer

class kvBrain:
    ans_constants = {}
    ans_plus = {}
    
    STATICFILE = configGuru.getProperty("fileloc", "kvstatic")
    PLUSFILE = configGuru.getProperty("fileloc", "kvplus")
    cleanInternel = eval(configGuru.getProperty("settings","clean"))
    
    #加载静态数据文件,该文件只能手工修改，优先级高于学习文件
    def load_static_data(self):
        myfile = open(self.STATICFILE)
        content = myfile.readline()
        while  not content.strip() == "":
            names = content.split("###")
            if len(names) == 2:
                ans = answer(names[1].strip())
                self.ans_constants[names[0].strip().upper()] = ans
            content = myfile.readline()
        print "load static file done"
    
    #加载训练文件
    def load_plus_data(self):
        myfile = None
        try:
            myfile = open(self.PLUSFILE,"r")
            self.ans_plus = p.load(myfile)
            print "load learned file done"
        except:
            print "error when loading learned file"
            print traceback.print_exc()
        finally:
            if myfile:
                myfile.close()
       
    #保存训练文件
    def save_plus_data(self):
        myfile = None
        try:
            myfile = open(self.PLUSFILE,"w")
            p.dump(self.ans_plus,myfile)
            print "save learned file done"
        except:
            print "error when saving learned file"
            print traceback.print_exc()
        finally:
            if myfile:
                myfile.close()

    
    #学习某个问题及其答案(内存及文件)
    def learn(self, q, a):
        q = configGuru.filter_string(q)
        a = a.strip()
        ans = answer(a)
        self.ans_plus[q] = ans
        self.save_plus_data()
        return "question: %s learned, answer is: %s"  % (q, a)

    # 找到某个问题的答案,并更新最后使用日期
    # 如果找不到则返回None
    def response(self,q):
        q = configGuru.filter_string(q)
        if self.ans_constants.has_key(q.encode("utf-8")):
            return self.ans_constants[q.encode("utf-8")].ans        
        if self.ans_plus.has_key(q):
            self.ans_plus[q].time = time.time()
            return self.ans_plus[q].ans
        return None

    # 清除过期的学习数据（超过settings.clean时间没有使用，单位为秒）
    def clean_plus_data(self):
        print "cleaning data..."
        for k,v in self.ans_plus.items():
            if time.time() - v.time > self.cleanInternel:
                print "deleting data:"+k
                del self.ans_plus[k]
        self.save_plus_data()
    
    def __init__(self):
        self.load_static_data()
        self.load_plus_data()
        
    ##测试
    def test(self):
        print self.response("hello")
        #self.learn("maple", "hey,maple")
        print self.response("maple")
        self.learn("你在哪里", "我住在maple的电脑里")
        print self.response("你在哪里")

############################################################################################################################
if __name__ == "__main__":
    b = kvBrain()
    b.test()
    #b.clean_plus_data()
    #b.test()