__author__ = 'Sean Yu'
'''created @2015/6/11''' 

import subprocess
import re, string
import os, sys
import telnetlib
import time
#import urllib2
#import urllib
#import cookielib
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
# from selenium.webdriver.support import expected_conditions as EC
from common import baseSession
class WebSession(baseSession):
    url=None
    webdriver =None
    currentElement=None
    def __init__(self,name,attrs={},logger=None, logpath=None):
        if attrs['BROWSER'].strip()=='':
            attrs['BROWSER']='FireFox'

        baseSession.__init__(self, name,attrs,logger,logpath)

        if attrs['BROWSER'].lower() == 'firefox':
            self.webdriver = webdriver.Firefox()
        elif attrs['BROWSER'].lower() == 'chrome':
            self.webdriver = webdriver.Chrome()
        elif attrs['BROWSER'].lower() == 'chrome':
            self.webdriver = webdriver.Ie()

    def CheckUrl(self,url):
        if not self.url:
            self.url = url

        if url:
            self.url = url

        if not self.url:
            self.error
            raise Exception('Url hasn\'t been given!')
        return  self.url
    def GetElement(self, type, by):
        if not type:
            type ='id'
        else:
            type= type.lower()
        element=None
        if type== 'id':
            element= self.webdriver.find_element_by_id(by)
        elif type == 'xpath':
            element= self.webdriver.find_element_by_xpath(by)
        elif type == 'name':
            element=self.webdriver.find_element_by_name(by)
        elif type == 'link_text':
            element= self.webdriver.find_element_by_link_text(by)
        self.currentElement=element
        return  self.currentElement
    def Send(self,by , keys, type =None, index=None, url=None):
        if index:
            element = self.GetOneFromElements(type, by, index)
        else:
            element = self.GetElement(type,by)
        for key in keys:
            if key in ['\n', '\r']:
                element.send_keys(Keys.RETURN)
            else:
                element.send_keys(key)

    def get(self, url):
        self.webdriver.get(self.CheckUrl(url))
    def Click(self, by, type =None ,index =None, url=None):
        if index:
            element = self.GetOneFromElements(type,by, index)
        else:
            element = self.GetElement(type,by)

        element.click()

    def select(self, obj, selectBy, selectKey):
        selectBy = selectBy.strip().lower()
        if selectBy in [None, '']:
            obj.select_by_visible_text(selectKey)
        elif selectBy.strip().lower()== 'value':
            obj.select_by_value(selectKey)
        elif selectBy.strip().lower()== 'index':
            obj.select_by_index(selectKey)
        elif selectBy == 'text':
            obj.select_by_visible_text(selectKey)
    def Select(self, by, selectBy, selectKey, type =None, index =None, url=None):
        if not type:
            type ='id'
        else:
            type= type.lower()
        if index:
            element = self.GetOneFromElements(type,by, index)
        else:
            element = self.GetElement(type,by)
        selectObj = Select(element)
        self.select(selectObj, selectBy,selectKey)
    def Clear(self, by, type =None,index=None ,url=None):
        if index:
            element = self.GetOneFromElements(type,by, index)
        else:
            element = self.GetElement(type,by)

        element.clear()


    def GetOneFromElements(self, type, by, index):
        if not type:
            type ='id'
        else:
            type= type.lower()
        element=None
        if type== 'id':
            element= self.webdriver.find_elements_by_id(by)
        elif type == 'xpath':
            element= self.webdriver.find_elements_by_xpath(by)
        elif type == 'name':
            element=self.webdriver.find_elements_by_name(by)
        elif type == 'link_text':
            element= self.webdriver.find_elements_by_link_text(by)
        self.currentElement = element[index]
        return self.currentElement

    def WalkElement(self, wait = 5):
        elements=None
        elements = self.webdriver.find_elements_by_xpath('//input')
        import time
        i = 0
        output = ''
        for e in elements:
            try:

                #print("input[%d] id:" %i ,e.id)
                e.click()
                e.send_keys('Index%d'%i)
                output += "input[%d] id:" %i+"%s\n"%(str(e.id))
                i+=1
                time.sleep(wait)
            except Exception as err:

                output += "input[%d] id:" %i+"%s\n"%(str(err.msg))
                i+=1
        print(output)








