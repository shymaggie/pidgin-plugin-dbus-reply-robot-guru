#!/usr/bin/python
# -*- coding: utf-8 -*-
'''
an aiml engine for alice
pyaiml module (http://pyaiml.sourceforge.net/)used here
Created on May 20, 2011
@author: maple
'''
import aiml,configGuru,os
import traceback
import cPickle as p

class aiBrain:
    brainFile = configGuru.getProperty("fileloc", "aibrainfile")
    sessionFile = configGuru.getProperty("fileloc","aisessionfile")
    brain = None;
    
    #初始化ai机器人
    def setup_aiml(self,config):
        guru = aiml.Kernel()
        if os.path.isfile(self.brainFile):
            guru.bootstrap(brainFile = self.brainFile)
        else:
            guru.bootstrap(learnFiles = "data/std-startup.xml", commands = "load aiml b")
            guru.saveBrain(self.brainFile)
        guru.setTextEncoding("utf8")
        # Initialize bot predicates
        for k,v in config.items():
            if k[:8] != "botinfo.":
                continue
            guru.setBotPredicate(k[8:], v)
        return guru
    
    # 获得当前AI
    def get_ai(self):
        if not self.brain == None:
            return self.brain
        return self.setup_aiml(configGuru.get())
    
    #加载session
    def load_sessions(self):
        myFile = None
        try:
            ai = self.get_ai()
            myFile = file(self.sessionFile, "r")
            sessions = p.load(myFile)
            myFile.close()
            for sessionid,session in sessions.items():
                for pred,value in session.items():
                    ai.setPredicate(pred, value, sessionid)
        except:
            print "error when try loading ai"
        print "ai loaded"    
        if not myFile == None:
            myFile.close()
    
    #保存session
    def save_session(self):
        myFile = None
        try:
            ai = self.get_ai()
            session = ai.getSessionData()
            myFile = file(self.sessionFile, "w")
            p.dump(session, myFile)
            myFile.close()
        except:
            if not myFile == None:
                myFile.close()
            print "error when save session"
            print traceback.print_exc() 
            return False
        else:
            myFile.close()
            return True
    
    #在退出时保存聊天session
    def __del__(self):
        print "saving session before dying..."
        if self.save_session():
            print "session saved"
       
    #得到某个用户某个消息的回复
    def response(self,user,q):
        user = configGuru.filter_string(user)
        q = configGuru.filter_string(q)
        a = self.get_ai().respond(q, user)
        return a
    
    def __init__(self):
        self.brain = self.setup_aiml(configGuru.get())
        self.load_sessions()
            

##############################################################
if __name__ == "__main__":
    guru = aiBrain()
    i = 1
    while i <= 5: 
        print guru.get_ai().respond(raw_input("> "),"maple")
        i+=1
    #guru.save_session()