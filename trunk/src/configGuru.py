#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Handles the reading, writing of (and general access to) guru's
persistent configuration information, stored (by default) in
the data/guru.ini file.
"""

import os
import string,re
import sys

import ConfigParser

configFileName = "data/guru.ini"

# Load default values for various config-file options.
# The defaults are scattered throughout the frontend and
# backend modules, each of which may have a dictionary
# attribute called configDefaults similar to the one
# below.  This code merges all the configDefaults into
# one master copy.
configDefaults = {
    "botinfo.name":              "guru",
    "botinfo.master":               "maple",
    "botinfo.gender":             "male",
    "botinfo.location":      "beijing",
    "botinfo.birthday":          "May 15th, 2011",
    }


def _WriteINI(file, config=configDefaults):
    """
    Writes the config dictionary to a .INI file.
    """
    if len(config) == 0:
        return
    iniFile = open(file, "w")
    currentSection = ""
    keys = config.keys()
    keys.sort()
    for key in keys:
        # Don't write entries with no value
        value = config[key]
        if value == "":
            continue

        # Split the key into section and variable.		
        section, var = string.split(key, ".", 1)
        if section != currentSection:
            # start a new section
            if currentSection:
                iniFile.write("\n")
            iniFile.write("[%s]\n" % section)
            currentSection = section

        # write the entry
        iniFile.write("%s = %s\n" % (var, value))
    iniFile.close()

def _ReadINI(file, config={}):
    """
    Returns a dictionary with keys of the form
    <section>.<option> and the corresponding values.
    """
    config = config.copy()
    cp = ConfigParser.ConfigParser()
    cp.read(file)
    for sec in cp.sections():
        name = sec.lower()
        for opt in cp.options(sec):
            config[name + "." + opt.lower()] = string.strip(cp.get(sec, opt))
    return config

_config = None
def load(file):
    """
    Returns a dictionary containing the current configuration information,
    read from the specified .INI file.
    """
    global _config, configDefaults
    try:
        if not os.path.exists(file):
            _WriteINI(file)
        _config = _ReadINI(file, configDefaults)
    except:
        print "ERROR: could not load config file %s" % file
        sys.exit(-1)
    return _config

def get():
    global _config
    if _config is None:
        _config = load(configFileName)
    return _config

def getProperty(category,name):
    global _config
    if _config is None:
        _config = get()
    key = category.strip() +"."+name.strip()
    if _config.has_key(key):
        return _config[key]
    return None

#去掉字符串中的标点
def filter_string(str):
    str = str.strip().upper()
    if not isinstance(str, unicode):
        try:
            str = str.decode('utf8')
        except:
            return str
    a = u'\uff11\uff12\uff13\uff14\uff15\uff16\uff17\uff18\uff19\uff10\u4e00\u4e8c\u4e09\u56db\u4e94\u516d\u4e03\u516b\u4e5d\u96f6\u58f9\u8d30\u53c1\u8086\u4f0d\u9646\u67d2\u634c\u7396\u96f6\u2488\u2489\u248a\u248b\u248c\u248d\u248e\u248f\u2490\u2491\u2474\u2475\u2476\u2477\u2478\u2479\u247a\u247b\u247c\u247d\u2460\u2461\u2462\u2463\u2464\u2465\u2466\u2467\u2468\u2469\u3220\u3221\u3222\u3223\u3224\u3225\u3226\u3227\u3228\u3229\uff41\uff42\uff43\uff44\uff45\uff46\uff47\uff48\uff49\uff4a\uff4b\uff4c\uff4d\uff4e\uff4f\uff50\uff51\uff52\uff53\uff54\uff55\uff56\uff57\uff58\uff59\uff5a\uff21\uff22\uff23\uff24\uff25\uff26\uff27\uff28\uff29\uff2a\uff2b\uff2c\uff2d\uff2e\uff2f\uff30\uff31\uff32\uff33\uff34\uff35\uff36\uff37\uff38\uff39\uff3a\uff0d\uff1d\uff3b\uff3d\u3001\uff1b\uff40\uff07\u2018\u2019\uff0c\u3002\uff0f\uff5e\uff01\xb7\uff03\uffe5\uff05\ufe3f\uff06\uff0a\u203b\uff08\uff09\u2014\uff0b\uff5b\uff5d\uff5c\uff1a\u300a\u300b\uff1f\u2026\uff3c\uff0e\uff20\uff04\uff3f\u201c\uff02\u201d\uff1c\uff1e\u3000\u3008\u3009\u3010\u3011'
    b = u'1234567890123456789012345678901234567890123456789012345678901234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-=[],;`\'`\',./~!.#$%^&**()-+{}|:<>?.\\.@$_"""<> <>[]'
    table = dict(zip([ord(i) for i in a], b))
    table_no_punct = dict((ord(i), u'') for i in u'!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~\t\n\x0b\x0c\r ')
    return str.translate(table).translate(table_no_punct)

##过滤HTML中的标签
#将HTML中标签等信息去掉
#@param htmlstr HTML字符串.
def filter_tags(htmlstr):
    #先过滤CDATA
    re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
    re_script=re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>',re.I)#Script
    re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
    re_br=re.compile('<br\s*?/?>')#处理换行
    re_h=re.compile('</?\w+[^>]*>')#HTML标签
    re_comment=re.compile('<!--[^>]*-->')#HTML注释
    s=re_cdata.sub('',htmlstr)#去掉CDATA
    s=re_script.sub('',s) #去掉SCRIPT
    s=re_style.sub('',s)#去掉style
    s=re_br.sub('\n',s)#将br转换为换行
    s=re_h.sub('',s) #去掉HTML 标签
    s=re_comment.sub('',s)#去掉HTML注释
    #去掉多余的空行
    blank_line=re.compile('\n+')
    s=blank_line.sub('\n',s)
    s=replaceCharEntity(s)#替换实体
    return s

##替换常用HTML字符实体.
#使用正常的字符替换HTML中特殊的字符实体.
#你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
#@param htmlstr HTML字符串.
def replaceCharEntity(htmlstr):
    CHAR_ENTITIES={'nbsp':' ','160':' ',
                'lt':'<','60':'<',
                'gt':'>','62':'>',
                'amp':'&','38':'&',
                'quot':'"','34':'"',}
   
    re_charEntity=re.compile(r'&#?(?P<name>\w+);')
    sz=re_charEntity.search(htmlstr)
    while sz:
        key=sz.group('name')#去除&;后entity,如&gt;为gt
        try:
            htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
            sz=re_charEntity.search(htmlstr)
        except KeyError:
            #以空串代替
            htmlstr=re_charEntity.sub('',htmlstr,1)
            sz=re_charEntity.search(htmlstr)
    return htmlstr

def repalce(s,re_exp,repl_string):
    return re_exp.sub(repl_string,s)


get()
#print getProperty("fileloc","kvplus")
#s = '中华 人,民,，共和国（北京）？?abcDEfg**'
#print filter_string(s)