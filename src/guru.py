#!/usr/bin/python
# -*- coding: utf-8 -*-

import dbus, os,time,re,random,string,traceback
import gobject, configGuru,logging
import cPickle as p
from dbus.mainloop.glib import DBusGMainLoop
from kvBrain import kvBrain
from aiBrain import aiBrain

class guru:        
    msg_sessions = {}    
    #开启回复的状态 3=away, 4=invisible,5=unavailable,6=extended
    botstatus =[3,4,5,6]
    #设置与AI有关的提示，使其只出现一次
    popup = {}
    pidgin = None
    guru_ai = None
    guru_kv = None
    #读取相关配置
    SESSIONFILE = configGuru.getProperty("fileloc", "sessionfile")
    guru_name =  configGuru.getProperty("general", "name")
    guru_cname =  configGuru.getProperty("general", "cname")
    ai_name = configGuru.getProperty("botinfo", "name")
    regexqa = re.compile(configGuru.getProperty("command", "regexqa"))
    regexq = re.compile(configGuru.getProperty("command", "regexq"))
    regexa = re.compile( configGuru.getProperty("command", "regexa"))
    regexbye = re.compile( configGuru.getProperty("command", "bye"))
    gossipnum = string.atoi(configGuru.getProperty("settings", "gossipnum"))
    sessiontimeout = eval(configGuru.getProperty("settings","sessiontimeout"))
    
    #给发信账户回复消息
    def sendMessage(self,m, account, sender, conversation, flags, bot):
        conversation = self.pidgin.PurpleConversationNew(1, account, sender)
        im = self.pidgin.PurpleConvIm(conversation)
        msg = "%s: %s" % (bot,m)
        self.pidgin.PurpleConvImSend(im, msg)
        self.msg_sessions[str(sender)] = time.time()
        logging.info("message sent to %s : %s",str(sender), m.decode("utf-8"))
    
    #发送欢迎消息
    def sendWelcomeMessage(self,account,sender,conversation,flags):
        m = "Hi, 我是%s(%s), 主人好像不在, 我来陪你聊天吧^_^\r\n 我知道主人的好多小秘密哟, 使用gossip命令我就告诉你。作为交换，你能告诉我蓝仙女在哪儿吗？" %(self.guru_cname,self.guru_name)
        self.sendMessage(m,account,sender,conversation,flags,self.guru_name)
        self.msg_sessions[str(sender)] = time.time()
        self.save_session()

    #根据用户发来的消息生成AIML回复
    def get_ai_replymessage(self, sender, message):
        if self.guru_ai == None:
            self.guru_ai = aiBrain()        
        return self.guru_ai.response(sender, message)
    
    #根据用户发来的消息生成storage回复
    def get_kv_replymessage(self, sender, message):
        if self.guru_kv == None:
            self.guru_kv = kvBrain()
        return self.guru_kv.response(message)

    #gossip闲话模式
    def gossip(self,account,sender,conversation, flags):
        index = random.randint(0,self.gossipnum-1)
        m = self.guru_kv.response(str(index))
        self.sendMessage(m, account, sender, conversation, flags,self.guru_name)
        
    #处理用户发来的消息，生成回复
    def process_message(self,account,sender, message,conversation, flags):
        
        #如果是第一次进入聊天或上一次聊天间隔较长，发送欢迎消息
        if not self.msg_sessions.has_key(sender) or time.time() - self.msg_sessions[sender] >= self.sessiontimeout:
            self.sendWelcomeMessage(account,sender,conversation,flags)
            return None
        message = message.strip()
        
        #如果是gossip命令，则进入gossip模式
        if cmp(message.strip().upper(),"GOSSIP") == 0:
            self.gossip(account,sender,conversation, flags)
            return None     
        
        #如果是学习命令，则执行该命令
        if self.regexqa.match(message):
            self.learn(account,sender, message,conversation, flags)
            return None
        
        #如果是bye指令，则保存各类session信息,这个地方还有问题
        if self.regexbye.match(message):
            self.bye(account,sender, message,conversation, flags)
            return None   
        
        #查找kv回复
        reply = self.get_kv_replymessage(sender, message)
        if reply == None:
            reply = self.get_ai_replymessage(sender, message)
            self.sendMessage(reply, account, sender, conversation, flags, self.ai_name)
            #第一次给出ai回复时同样给出提示
            print "conversation:%s" % str(conversation)
            if not self.popup.has_key(str(conversation)):
                reply = "%s还比较笨，不懂你在说什么，上面的话是%s的朋友%s说的。" % (self.guru_cname,self.guru_cname,self.ai_name)
                reply += " 你可以使用 \"Q:问题内容 A:回答内容\" 来教会%s，或者可以继续同%s聊天" % (self.guru_cname,self.ai_name)
                self.sendMessage(reply, account, sender, conversation, flags, self.guru_name)
                self.popup[str(conversation)] = 1
        else:
            self.sendMessage(reply, account, sender, conversation, flags, self.guru_name)
        return None
    
    def bye(self,account,sender,message,conversation,flags):
        m = self.get_kv_replymessage(sender, message)
        if m == None:
            m = "Sorry, I am a little busy now, let's chat later"
        self.sendMessage(m, account, sender, conversation, flags, self.guru_name)
        self.guru_ai.save_session()
        self.guru_kv.save_plus_data()
        self.save_session()
        
    #解析命令执行并返回执行结果
    def learn(self,account,sender, command,conversation, flags):
        q =None
        a = None
        msg = None
        matchq = self.regexq.search(command)
        matcha = self.regexa.search(command)
        if matchq and matcha:
            q = matchq.group(1)
            a = command[matcha.end():]
            msg = self.guru_kv.learn(q, a)
        else:
            msg = "command format error: %s" % command
        self.sendMessage(msg, account, sender, conversation, flags)
        
    #入口方法 
    def guru_main(self,account, sender, message, conversation, flags):
        buddy = self.pidgin.PurpleFindBuddy(account, sender)
        if buddy != 0:
            alias = self.pidgin.PurpleBuddyGetAlias(buddy)
        else:
            alias = sender
        account_name = self.pidgin.PurpleAccountGetUsername(account) + "@"+self.pidgin.PurpleAccountGetProtocolName(account)
        message = re.sub("<.*?>", "", message)#html2text
        status_id = self.pidgin.PurpleSavedstatusGetCurrent() 
        status = self.pidgin.PurpleSavedstatusGetType(status_id)
        
        if status in self.botstatus: 
            logging.info("message received from %s in account %s: %s",alias,account_name,message) 
            self.process_message(account,sender,message,conversation,flags)

    #加载训练文件
    def load_session(self):
        myfile = None
        try:
            myfile = open(self.SESSIONFILE,"r")
            self.msg_sessions = p.load(myfile)
            print "load session file done"
        except:
            print "error when loading session"
            print traceback.print_exc()
        finally:
            if myfile:
                myfile.close()
            
    #保存训练文件
    def save_session(self):
        myfile = None
        try:
            myfile = open(self.SESSIONFILE,"w")
            p.dump(self.msg_sessions,myfile)
            print "save session succeed"
        except:
            print "error when saving session"
            print traceback.print_exc()
        finally:
            if myfile:
                myfile.close()
                
    def __init__(self):
        bus = dbus.SessionBus()
        bus.add_signal_receiver(self.guru_main,
            dbus_interface='im.pidgin.purple.PurpleInterface',
            signal_name='ReceivedImMsg')
        self.pidgin = bus.get_object("im.pidgin.purple.PurpleService", "/im/pidgin/purple/PurpleObject")
        self.pidgin = dbus.Interface(self.pidgin, "im.pidgin.purple.PurpleInterface")
        self.guru_ai = aiBrain()
        self.guru_kv = kvBrain()
        self.load_session()

if __name__ == "__main__":
    logging.basicConfig(filename = os.path.join(os.getcwd(), 
                        configGuru.getProperty("fileloc", "log")),
                        level = logging.INFO, 
                        filemode = 'a', 
                        format = '%(asctime)s - %(levelname)s: %(message)s')
    # Setup dbus glib mainloop
    DBusGMainLoop(set_as_default=True)
    # Create new instance of our plugin class
    guru()
    # Get main loop and run it
    gobject.MainLoop().run()