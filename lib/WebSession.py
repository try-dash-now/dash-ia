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
class WebSession(baseSession,webdriver.Firefox):
    def __init__(self,name,attrs={},logger=None, logpath=None):
        baseSession.__init__(self, name,attrs,logger,logpath)
        webdriver.Firefox.__init__(self)


def changeIP(driver, ip, newIP):
    ipnew = '1.1.1.1'
    driver.get('http://%s/advancedsetup_schedulingaccess.html'%ip)
    apply_button = driver.find_element_by_link_text("DHCP Settings")
    apply_button.click()

    try:
        assert "CenturyLink Modem Configuration" in driver.title
        apply_button = driver.find_element_by_xpath("//input[@name='dhcp_server'][@checked='checked']")
        apply_button.click()
        #name="IPInterfaceIPAddress" id="IPInterfaceIPAddress"
        IPaddress =   driver.find_element_by_xpath("//input[@name='IPInterfaceIPAddress'][@id='IPInterfaceIPAddress']")
        IPaddress.clear()
        IPaddress.send_keys(ipnew)
        IPaddress.clear()
        IPaddress.send_keys(ip)
        IPaddress.send_keys(Keys.RETURN)
        disalbe =driver.find_elements_by_name("dhcp_server")#("//input[@name='dhcp_server'][@type='radio']").
        #disalbe = apply_button.select_by_visible_text("Disable")
        disalbe[1].click()
        #disalbe.click()
        apply_button = driver.find_element_by_link_text("Apply")
        apply_button.click()
    except Exception,e:
        apply_button = driver.find_element_by_link_text("Logout")
        apply_button.click()
        driver.quit()
        print("FAILURE: Unable to login to GUI on modem. " + str(e))
        return False
def actiontec_change_defaults(ip, newip):
    if not ip:
        ip='192.168.0.1'
    else:
        ip =ip.strip()
    url = 'http://%s/supportconsole'%(ip)#modem["defaultURL"]
    telnet_url = "http://%s/advancedsetup_remotetelnet.html"%(ip) #modem["telnetURL"]
    admin_url = "http://%s/advancedsetup_admin.html"%(ip) # modem["adminURL"]
    login =  "CenturyL1nk"
    password = 'CTLsupport12'
    newlogin = 'admin'
    newpassword = 'admin'
    import sys,os
    #sys.path.insert(0, os.path.abspath(os.getcwd()))
    print('\n'.join(sys.path))
    webdriver.Chrome()
    driver = webdriver.Firefox()#webdriver.Chrome()#('C:/syu/auto/webGUI')#
    driver.get(url)
    #login to modem
    try:
        assert "CenturyLink Modem Configuration" in driver.title
        elem = driver.find_element_by_name("admin_user_name")
        elem.send_keys(login)
        elem = driver.find_element_by_name("admin_password")
        elem.send_keys(password)
        elem.send_keys(Keys.RETURN)
        apply_button = driver.find_element_by_link_text("Apply")
        apply_button.click()
    except Exception,e:
        driver.quit()
        print("FAILURE: Unable to login to GUI on modem. " + str(e))
        return False





 #config wan as VDSL2
    driver.get('http://%s/advancedsetup_schedulingaccess.html'%ip)
    apply_button = driver.find_element_by_link_text("Broadband Settings")
    apply_button.click()
    driver.get('http://%s/advancedsetup_broadbandsettings.html'%(ip))
    try:
        assert "CenturyLink Modem Configuration" in driver.title
        #wan_type
        telnet_select = Select(driver.find_element_by_id("wan_type"))
        telnet_select.select_by_visible_text("VDSL2")
        apply_button = driver.find_element_by_link_text("Apply")
        apply_button.click()
    except Exception,e:
        driver.quit()
        print("FAILURE: Unable to off WIFI  GUI on modem. " + str(e))
        return False




    #OFF WIFI
    driver.get('http://%s/wirelesssetup_basicsettings.html'%(ip))
    try:
        assert "CenturyLink Modem Configuration" in driver.title
        elem = driver.find_element_by_id("id_wl_on")
        elem.click()
        elem = driver.find_element_by_id("id_wl_off")
        elem.click()
        apply_button = driver.find_element_by_link_text("Apply")
        apply_button.click()
    except Exception,e:
        driver.quit()
        print("FAILURE: Unable to off WIFI  GUI on modem. " + str(e))
        return False

    #end of OFF WIFI
    driver.get(telnet_url)
    try:
        assert "CenturyLink Modem Configuration" in driver.title
        telnet_select = Select(driver.find_element_by_id("remote_management"))
        telnet_select.select_by_visible_text("Telnet Enabled")
        telnet_login = driver.find_element_by_id("admin_user_name")
        telnet_password = driver.find_element_by_id("admin_password")
        telnet_confirm = driver.find_element_by_id("confirmPass")
        apply_button = driver.find_element_by_link_text("Apply")
        telnet_login.clear()
        telnet_password.clear()
        telnet_confirm.clear()
        telnet_login.send_keys(newlogin)
        telnet_password.send_keys(newpassword)
        telnet_confirm.send_keys(newpassword)
        apply_button.click()
    except Exception,e:
        driver.quit()
        print("FAILURE: Unable to set telnet password through GUI on modem. " + str(e))
        return False
    driver.get(telnet_url)
    driver.get(admin_url)
    try:
        assert "CenturyLink Modem Configuration" in driver.title
        admin_login = driver.find_element_by_id("admin_user_name")
        admin_password = driver.find_element_by_id("admin_password")
        admin_confirm = driver.find_element_by_id("confirmPass")
        apply_button = driver.find_element_by_link_text("Apply")
        admin_login.clear()
        admin_password.clear()
        admin_confirm.clear()
        admin_login.send_keys(newlogin)
        admin_password.send_keys(newpassword)
        admin_confirm.send_keys(newpassword)
        apply_button.click()
    except Exception,e:
        driver.quit()
        print("FAILURE: Unable to set administration password through GUI on modem. " + str(e))
        return False


#config the lan ip address:
    changeIP(driver, ip, newip)




    driver.get(admin_url)
    logout_button = driver.find_element_by_id("logout_btn")
    logout_button.click()
    driver.close()
    print("SUCCESS: Successfully enabled telnet and updated administrative username and password to " + newlogin + " " + newpassword + ".")
    return True

if __name__ == '__main__':
    print("######################NEW TEST---------------------------")
    import sys
    ip = sys.argv[1]
    newip = sys.argv[2]
    try:
        #ip = '192.168.0.153'
        actiontec_change_defaults(ip, newip)
    except Exception as e:
        import traceback
        print(traceback.format_exc())

    #actiontec_telnet("192.168.0.1","admin","admin")
    #/advancedsetup_remotetelnet.html
