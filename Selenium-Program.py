
from selenium import webdriver
from selenium.webdriver.support import ui
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import ConfigParser
import logging
import coloredlogs
import time
import uuid
import sys
import os

logDict = {

            'ALARM.log'  : ['Logs:LOGS', 'Charts:CHART'],
            'DHCP.log'   : ['Logs:LOGS'],
	    'AUTH.log'   : ['Events:LOGS', 'Policies:LOGS', 'Charts:CHART'],
            'NGFW.log'   : ['Logs:LOGS', 'Charts:CHART'],
	    'CGNAT.log'  : ['Logs:LOGS', 'Charts:CHART'],
	    'DOS.log'    : ['MainPage:LOGS'],
	    'IDP.log'    : ['MainPage:LOGS'],
	    'AV.log'     : ['MainPage:LOGS'],
	    'URLF.log'   : ['MainPage:LOGS'],
	    'IPF.log'    : ['MainPage:LOGS'],
	    'TM.log'     : ['Logs:LOGS', 'Charts:CHART'],
	    'TM.log.http': ['Logs:LOGS', 'Charts:CHART'],
	    'SDWAN.log'  : ['MainPage:LOGS'],
	    'SDWAN_SLAVIOL.log': ['MainPage:LOGS'],
	    'SSL.log'    : ['MainPage:LOGS'],
	    'ADC.log'    : ['MainPage:LOGS'],
	    'SYSTEM.logvnfevents': ['MainPage:LOGS'],
	    'PCAP.log'   : ['MainPage:LOGS'] 
}

OrderList = [ 'ALARM.log', 'DHCP.log' ,'AUTH.log','NGFW.log','CGNAT.log','DOS.log','IDP.log','AV.log','URLF.log','IPF.log','TM.log','TM.log.http','SDWAN.log','SDWAN_SLAVIOL.log','SSL.log'  ,'ADC.log'  ,'SYSTEM.logvnfevents','PCAP.log'] 

class Logger:
    def __init__(self, logFile,
                 logger_name='vFrameWork',
                 loglevel=logging.DEBUG):
        try:
            self.logger = logging.getLogger(logger_name)
            self.logger.setLevel(loglevel)
            self.addLogHandler(logFile, logger_name, loglevel)
            self.ERROR_FLAG = False
        except Exception as ex:
            print("ERROR::An exception occurred while initialising loggers" + str(ex))
            exit(0)

    def addLogHandler(self, logFile,
                      logger_name='vFrameWork',
                      loglevel=logging.DEBUG):
        try:
            hdlr = logging.FileHandler(logFile, mode='w')
            if logger_name == 'Result':
                formatter = logging.Formatter('%(message)s')
            else:
                formatter = logging.Formatter(
                    '%(asctime)s %(levelname)s (%(threadName)-10s) %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')
            hdlr.setFormatter(formatter)
            hdlr.setLevel(loglevel)
            self.logger.addHandler(hdlr)
            return hdlr
        except Exception as ex:
            print("ERROR::An exception occurred while adding log handlers" + str(ex))
            exit(0)

    def Log(self, logLevel, msg):
        try:
            for line in msg.split("\n"):
                if logLevel == logging.INFO:
                    self.logger.info("   " + str(line))
                elif logLevel == logging.WARNING:
                    self.logger.warn(line)
                elif logLevel == logging.ERROR:
                    self.logger.error("  " + str(line))
                else:
                    self.logger.debug("  " + str(line))
        except Exception as ex:
            print("ERROR::An exception occurred while writting the log messages." + str(ex))
            exit(0)
    
    def close(self):
        try:
            self.logger.close()
        except Exception as ex:
            print("ERROR::An exception occurred while closing the logging file." + str(ex))
            exit(0)

def setupDriver():
    print("Hit create driver")
    chromedriver = "/usr/local/bin/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)
    return driver
    
def analyticsLogin():
    print("Hit analytics login page %s" % analyticsUrl)
    try:
        time.sleep(1)
        driver.get(analyticsUrl)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "logo-text"))
        )
    except Exception as ex:
        msg = 'Failed: Could not load the analytics login page :: An Exception occured %s ' % ex
        logger.Log(logging.ERROR, msg)
        driver.quit()
        sys.exit()

    try:
         time.sleep(1)
         driver.find_element_by_xpath("//input[@name='username']").send_keys(role)
         driver.find_element_by_xpath("//input[@name='password']").send_keys(password)
         time.sleep(.5)
         driver.find_element_by_id("login_submit").click()
         time.sleep(1)
         element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "widget-grid"))
        )
    except Exception as ex:
         msg = 'Failed: %s failed to authenticate analytics login page' % role
         logger.Log(logging.ERROR, msg)
         return False
    else:
        msg = 'Passed: %s logged into the analytics dashboard ' % role
        logger.Log(logging.INFO, msg)
        return True

def directorLogin():
    print("Hit director login page")
    try:
        driver.get("http://10.40.38.3/xxx/login")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "xxx-login-logo-text"))
        )
    except TimeoutException: 
        msg = "Failed: %s could not load director login page" % role
        logger.Log(logging.ERROR, msg)
        driver.quit()
        sys.exit()
    else:
        msg = "Passed: %s loaded director login page" % role
        logger.Log(logging.INFO, msg)
        
    try:
        time.sleep(1)
        username = driver.find_element_by_id("inputEmail")
        username.send_keys("Administrator")
        password = driver.find_element_by_id("inputPassword")
        password.send_keys("xxx123")
        password.send_keys(Keys.RETURN)
    except NoSuchElementException:
        msg = 'Failed: %s failed to locate an element on the director login page' % role
        logger.Log(logging.ERROR, msg)
        
    else:
        msg = 'Passed: %s found all elements on the director login page' % role
        logger.Log(logging.INFO, msg)
        

    try:
        driver.get("http://10.40.38.3//#director/monitoring/organizations/Provider!23a6545b-aaf2-49da-a100-fb6732202bd9")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "notification-container"))
        )
    except TimeoutException:
        msg = 'Failed: %s failed to authenticate and load director dashboard' % role
        logger.Log(logging.ERROR, msg)
        driver.quit()
        sys.exit()
    else:
        msg = 'Passed: %s authenticated and loaded director dashboard ' % role
        logger.Log(logging.INFO, msg)
        return True

def createOrganizationUser():
    print("Hit create organization user tab")
    global password
    password = "xxx@123$"
    try:
        time.sleep(1)
        driver.get("http://10.40.38.3/xxx/#director/administration/users/organization")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-jqgrid-sortable"))
        )
    except TimeoutException:
        msg = 'Failed: %s redirect to the organization users page' % role
        logger.Log(logging.ERROR, msg)
        driver.quit()
        sys.exit()
    else:
        msg = 'Passed: %s redirected to the organization users page' % role
        logger.Log(logging.INFO, msg)

    try:
        time.sleep(1)
        existingRoles = driver.find_elements_by_xpath('//tr[@role="row"]')
        for i in range(len(existingRoles)):
            userRole = existingRoles[i].find_elements_by_tag_name("td")[1]
            if userRole == role: raise Exception 
    except Exception:
        msg = "Failed: %s unable to create new organization user :: Organization user already exists" % role
        logger.Log(logging.ERROR, msg)
        driver.quit()
        sys.exit()
  
    try:
        driver.find_element_by_id("CREATE_organization-user").click()
    except NoSuchElementException:
        msg = 'Failed: %s failed to locate element CREATE_organization-user ' % role
        logger.Log(logging.ERROR, msg)
    else:
        msg = 'Passed: %s located element CREATE_organization-user ' % role
        logger.Log(logging.INFO, msg)

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "popup-wrap"))
        )
    except TimeoutException:
        msg = "Failed: %s is unable to load create user pop-up" % role
        logger.Log(logging.ERROR, msg)
        driver.quit()
        sys.exit()
    else:
        msg = "Passed: %s loaded create user pop-up" % role
        logger.Log(logging.INFO, msg)

    try:
        time.sleep(1)
        driver.find_element_by_id("users-organisation-username").send_keys(role)
        time.sleep(.5)
        driver.find_element_by_id("users-organisation-first_name").send_keys(role)
        time.sleep(5)
        driver.find_element_by_id("users-organisation-last_name").send_keys(role)
        p1 = driver.find_element_by_id("users-organisation-password")
        p1.clear()
        p1.send_keys(password)
        time.sleep(.5)
        p2 = driver.find_element_by_id("users-organisation-confirm_password")
        p2.clear()
        p2.send_keys(password)
        time.sleep(.5)
        driver.find_element_by_id("users-organisation-email").send_keys("test@xxx-networks.com")
    except NoSuchElementException:
        msg = "Failed: %s could not find one of the users-organisation-* id" % role
        logger.Log(logging.ERROR, msg)

    try:
        time.sleep(.5)
        option = driver.find_elements_by_tag_name("option")[0]
        option.click()
        time.sleep(3)
        select = '//option[@value="%s"]' % role
        driver.find_element_by_xpath(select).click()
        time.sleep(1)
        driver.find_element_by_id("form_ok_organization-user").click()
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alertBoxSize"))
        )
    except Exception as ex:
        msg = "Failed: %s filled and submit his information in the pop-up model :: An Exception occured %s " % (role, ex)
        logger.Log(logging.ERROR, msg)
        driver.quit()
        sys.exit()
    else:
        msg = "Passed : %s has just created a new organization user from the director " % role
        logger.Log(logging.INFO, msg)
        time.sleep(5)
        return True
        
def verifyUserRoles():
    print("Hit verify user roles")
    panel = driver.find_element_by_class_name("l-panel-dashboard")
    listElements = panel.find_elements_by_class_name("menu-item-parent")
    listLen = len(listElements)
    
    if (role == "TenantSuperAdmin" or role == "Administrator" or role == "admin"):
        try:
            assert listLen == 5, '%s is showing %s instead of 5 menu dashboard items' % (role, listLen)
        except AssertionError as err:
            msg = "Failed: %s showing incorrect user roles :: An Exception occured %s " % (role, err)
            logger.Log(logging.ERROR, msg)
            return True
        except Exception as ex:
            msg = "Failed: %s could not generate menu list length from dashboard :: An Exception occured %s " % (role, ex)
            logger.Log(logging.ERROR, msg)
            return True
        msg = "Passed: %s has been verified and has the correct access roles " % role
        logger.Log(logging.INFO, msg)
        return True
    elif (role == "TenantOperator" or role == "TenantSecurityAdmin"):
        try:
            for i in range(listLen):
                assert listElements[i].text != "SD-WAN", '%s has access to SD-WAN'
        except AssertionError as err:
            msg = "Failed: %s showing SD-WAMN data " % role
            logger.Log(logging.ERROR, msg)
            return True
    else:
        msg = "Failed: did not verify data role, did not recognize the role %s " % role
        logger.Log(logging.ERROR, msg)
        return True

def verifySiteTabs():
    print("Hit verify sites tab")
    sdwan = analyticsUrl + "index.html#dashboard?type=SDWAN.SITES"
    try:
        time.sleep(1)
        driver.get(analyticsUrl + "index.html#dashboard?type=SDWAN.SITES")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "containerTabs"))
        )
    except TimeoutException:
        msg = "Failed: %s could not load sd-wan sites page" % role
        logger.Log(logging.ERROR, msg)
    else:
        msg = "Passed: %s loaded SD-WAN site page" % role
        logger.Log(logging.INFO, msg)

    try:
        time.sleep(1)
        container = driver.find_element_by_class_name("containerTabs")
    except NoSuchElementException:
        msg = "Failed: %s could not find element with className containerTabs" % role
        logger.Log(logging.ERROR, msg)
    else:
        msg = "Passed: %s found element with className containerTabs" % role
        logger.Log(logging.INFO, msg)
    
    try:
        element = "ul.containerTabs.nav.nav-tabs.bordered > li > a > span"
        tabs = container.find_elements_by_css_selector(element)
    except NoSuchElementException:
        msg = "Failed: %s could not find SD-WAN navbar tab elements" % role
        logger.Log(logging.ERROR, msg)
    else:
        msg = "Passed: %s found SD-WAN navbar tab elements" % role
        logger.Log(logging.INFO, msg)

    try:
        if len(sdwanNavTabs) != len(tabs): raise ValueError()
    except ValueError:
            msg = "Failed: %s is missing SD-WAN site navbar tabs is missing tabs" % role
            logger.Log(logging.ERROR, msg)


def verifySdwanData():
    print("Hit verify sd-wan data")
    time.sleep(1)

    #grab the list of sites tabs so we can loop over them and verify their data
    container = driver.find_element_by_class_name("containerTabs")
    element = "ul.containerTabs.nav.nav-tabs.bordered > li > a > span"
    navTabs = container.find_elements_by_css_selector(element)
    time.sleep(1)
    tabs = driver.find_elements_by_css_selector("ul.containerTabs.nav.nav-tabs.bordered > li > a > span")
    
    #verify datatables data for USAGE tab
    datatables_loaded = len(driver.find_elements_by_class_name("dt-wrapper"))
    datatables_nodata = len(driver.find_elements_by_class_name("dataTables_empty"))
    if datatables_loaded >= 0:
        msg = "Success: %s SD-WAN-Appliance-%s page loaded %s datatables" % (role, "Usage", datatables_loaded)
        logger.Log(logging.INFO, msg)
    if datatables_nodata > 0:
        msg = "Warning: %s SD-WAN-Appliance-%s page loaded %s datatables without data" % (role, "Usage", datatables_nodata)
        logger.Log(logging.WARNING, msg)

    #logic to loop over the rest of the sdwan sites tabs to verify data, this is excluding USAGE tab
    name = None
    i = 1
    for i in range(len(sdwanNavTabs)):
        time.sleep(1)
        name = sdwanNavTabs[i]

        if name == "Availability":
            try:
                time.sleep(1)
                tabs[1].click()
                time.sleep(1)
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "highcharts-container"))
                )
            except TimeoutException:
                msg = "Failed: could not load sd-wan availability page"
                logger.Log(logging.ERROR, msg)
            else:
                msg = "Passed: %s is able to navigate to SD-WAN-Availability" % role
                logger.Log(logging.INFO, msg)   

            #highcharts there is either data or no data, if no data then hightcharts is broken
            highcharts_total = len(driver.find_elements_by_class_name("highcharts-container"))
            highcharts_without_data = len(driver.find_elements_by_class_name("highcharts-no-data"))
            highcharts_data = len(driver.find_elements_by_tag_name("defs"))
            highcharts_broken = highcharts_total - highcharts_data
                                
            if highcharts_data > 0:
                msg = "Success: %s SD-WAN-Appliance-%s page loaded %s highcharts with data" % (role, name, highcharts_data)
                logger.Log(logging.INFO, msg)
            
            if highcharts_without_data > 0:
                msg = "Warning: %s SD-WAN-Appliance-%s page loaded %s higchart without data" % (role, name, highcharts_without_data) 
                logger.Log(logging.WARNING, msg)
                
            if highcharts_broken > 0:
                msg = "Error: %s SD-WAN-Appliance-%s page loaded %s higchart is broken" % (role, name, highcharts_broken) 
                logger.Log(logging.ERROR, msg)

            continue

        if name == "Connections":
            time.sleep(1)
            try:
                tabs[2].click()
                time.sleep(1)
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "chord_tooltip"))
                )
            except TimeoutException:
                msg = "Failed: %s could not load SD-WAN connections page" % role
                logger.Log(logging.ERROR, msg)
            else:
                msg = "Passed: %s is able to navigate to SD-WAN-CONNECTIONS " % role
                logger.Log(logging.INFO, msg)

            #highcharts there is either data or no data, if no data then hightcharts is broken
            highcharts_total = len(driver.find_elements_by_class_name("highcharts-container"))
            highcharts_without_data = len(driver.find_elements_by_class_name("highcharts-no-data"))
            highcharts_data = len(driver.find_elements_by_tag_name("defs"))
            highcharts_broken = highcharts_total - highcharts_data                    
            if highcharts_data > 0:
                msg = "Success: %s SD-WAN-Appliance-%s page loaded %s highcharts with data" % (role, name, highcharts_data)
                logger.Log(logging.INFO, msg)
            if highcharts_without_data > 0:
                msg = "Warning: %s SD-WAN-Appliance-%s page loaded %s higchart without data" % (role, name, highcharts_without_data) 
                logger.Log(logging.WARNING, msg)
            if highcharts_broken > 0:
                msg = "Error: %s SD-WAN-Appliance-%s page loaded %s higchart is broken" % (role, name, highcharts_broken) 
                logger.Log(logging.ERROR, msg)
            continue

        if name == "HeatMap":
            time.sleep(1)
            try:
                tabs[3].click()
                time.sleep(1)
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "highcharts-container"))
                )
            except TimeoutException:
                msg = "Failed: could not navigate SD-WAN-HEATMAP"
                logger.Log(logging.ERROR, msg)
            else:
                msg = "Passed: %s is able to navigate to SD-WAN-HEATMAP " % role
                logger.Log(logging.INFO, msg)

            #highcharts there is either data or no data, if no data then hightcharts is broken
            highcharts_total = len(driver.find_elements_by_class_name("highcharts-container"))
            highcharts_without_data = len(driver.find_elements_by_class_name("highcharts-no-data"))
            highcharts_data = len(driver.find_elements_by_tag_name("defs"))
            highcharts_broken = highcharts_total - highcharts_data                   
            if highcharts_data > 0:
                msg = "Success: %s SD-WAN-Appliance-%s page loaded %s highcharts with data" % (role, name, highcharts_data)
                logger.Log(logging.INFO, msg)
            if highcharts_without_data > 0:
                msg = "Warning: %s SD-WAN-Appliance-%s page loaded %s higchart without data" % (role, name, highcharts_without_data) 
                logger.Log(logging.WARNING, msg)
            if highcharts_broken > 0:
                msg = "Error: %s SD-WAN-Appliance-%s page loaded %s higchart is broken" % (role, name, highcharts_broken) 
                logger.Log(logging.ERROR, msg)
            return True
                
def navigate_sdwan_appliance_site():
    print("Hit verify sd-wan-appliance site")
    usageTab = driver.find_elements_by_css_selector("ul.containerTabs.nav.nav-tabs.bordered > li > a > span")[0]
    #mimic user behavior of clicking on an appliance and navigating to appliance site page
    try:
        time.sleep(1)
        usageTab.click()
        time.sleep(1)
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "containerTabs"))
        )
        print(driver.current_url)
    except TimeoutException:
        msg = "Failed: %s could not load sd-wan sites page" % role
        logger.Log(logging.ERROR, msg)
    else:
        msg = "Passed: % loaded SD-WAN site page" % role
        logger.Log(logging.INFO, msg)
    finally:
        time.sleep(1)
        driver.find_elements_by_class_name("clickClass")[0].click()
        return True

def verify_appliance_site_tabs():
    print("Hit verify sd-wan-appliance site tabs")
    try:
        time.sleep(1)
        container = driver.find_element_by_class_name("containerTabs")
    except NoSuchElementException:
        msg = "Failed: %s could not find SWAN-SITES appliances tab container" % role 
        logger.Log(logging.ERROR, msg)
    else:
        msg = "Passed: %s located SWAN-SITES appliances tab container" % role 
        logger.Log(logging.INFO, msg)
    
    try:
        element = "ul.containerTabs.nav.nav-tabs.bordered > li > a > span"
        tabs = container.find_elements_by_css_selector(element)
    except NoSuchElementException:
        msg = "Failed: %s could not find SWAN-SITES appliances navbar items" % role
        logger.Log(logging.ERROR, msg)
    else:
        msg = "Passed: %s located SWAN-SITES appliances navbar items" % role
        logger.Log(logging.INFO, msg)

    try:
        if len(tabs) != len(sdwanapplianceNavTabs): raise ValueError(len(tabs))
    except ValueError as err:
        msg = "Failed: %s is loading the incorrect number of sdwan-appliance tabs :: An Exception occured user is only displaying %s tabs" % (role, err)
        logger.Log(logging.ERROR, msg)
    else:
        msg = "Passed: %s verified user is showing all the correct sdwan-appliance tabs" % role
        logger.Log(logging.INFO, msg)
    finally: 
        return True

def verify_appliance_site_data():
    print("Hit verify sd-wan-appliance-site data")
    current_url = driver.current_url
    #we are goign to grab the url and splice it; python string are immutable so you cant splice it, below is a work-around
    ext = current_url[current_url.find("&"):len(current_url)] +"&tab="
    new_url = analyticsUrl + "index.html#dashboard?type=SDWAN.SITES" + ext
    count = 0
    time.sleep(1)
    logger.Log(logging.INFO, "\n")
    for key in sdwanSiteTabs:
        name = key
        link = new_url + str(count)

        try:
            time.sleep(2)
            driver.get(link)
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "highcharts-container"))
            )
        except TimeoutException:
            msg = "Failed: %s SD-WAN-Appliance-%s page did not load" % (role, name)
            logger.Log(logging.WARNING, msg)
            continue
        else:
            msg = "Passed: %s SD-WAN-Appliance-%s page loaded" % (role, name)
            logger.Log(logging.INFO, msg)   

        count = count + 1

        time.sleep(1)
        #plan is to find each case for datatables and highchart and print it out, by counting the elements 
        datatables_loaded = len(driver.find_elements_by_class_name("dt-wrapper")) #loaded charts
        datatables_nodata = len(driver.find_elements_by_class_name("dataTables_empty")) #nodata

        if datatables_loaded >= 0:
            msg = "Success: %s SD-WAN-Appliance-%s page loaded %s datatables" % (role, name, datatables_loaded)
            logger.Log(logging.INFO, msg)

        if datatables_nodata > 0:
            msg = "Warning: %s SD-WAN-Appliance-%s page loaded %s datatables without data" % (role, name, datatables_nodata)
            logger.Log(logging.WARNING, msg)

        #highcharts there is either data or no data, if no data then hightcharts is broken
        highcharts_total = len(driver.find_elements_by_class_name("highcharts-container"))
        highcharts_without_data = len(driver.find_elements_by_class_name("highcharts-no-data"))
        highcharts_data = len(driver.find_elements_by_tag_name("defs"))
        highcharts_broken = highcharts_total - highcharts_data
                            
        if highcharts_data > 0:
            msg = "Success: %s SD-WAN-Appliance-%s page loaded %s highcharts with data" % (role, name, highcharts_data)
            logger.Log(logging.INFO, msg)
        
        if highcharts_without_data > 0:
            msg = "Warning: %s SD-WAN-Appliance-%s page loaded %s higchart without data" % (role, name, highcharts_without_data) 
            logger.Log(logging.WARNING, msg)
            
        if highcharts_broken > 0:
            msg = "Error: %s SD-WAN-Appliance-%s page loaded %s higchart is broken" % (role, name, highcharts_broken) 
            logger.Log(logging.ERROR, msg)

def verifySystemParams():
    import pdb; pdb.set_trace()
    print("Hit verify system params")
    driver.find_element_by_id("administration").click()
    time.sleep(2)
    rsVersion = driver.find_element_by_xpath('%s'%(Globals.config['rsversion']))
    time.sleep(2)
    dbVersion = driver.find_element_by_xpath('%s'%(Globals.config['dbversion']))
    try:
        if Globals.config['release'] == str(rsVersion.text):
   	    print("Passed: release versions match")
	    msg = ("Passed: release versions match")
	    logger.Log(logging.INFO, msg)
        else:
	    print("Failed: release version does not match")
	    msg = ("Failed: release versions do not match") 
	    logger.Log(logging.ERROR, msg)
	    time.sleep(1)
        if Globals.config['database'] == str(dbVersion.text):
	    print("Passed: database versions match")
	    msg = ("Passed: database versions match")
	    logger.Log(logging.INFO, msg)
        else:
	    print("Failed: database versions do not match")
	    msg = ("Failed: database versions do not match")
	    logger.Log(logging.ERROR, msg)

    except TimeoutException:
	msg = ("Failed to compare versions")
	logger.Log(logging.ERROR, msg) 

    else:
	msg = ("Passed: Succesful comparison of database and release versions")
	logger.Log(logging.INFO, msg)

def verifyLogsParam():
    import pdb; pdb.set_trace()
    print("Hit verify log data")
    driver.find_element_by_xpath('//*[@id="left-panel"]/nav[1]/ul[1]/li[2]/a[1]/i[1]').click()
    time.sleep(1)
    current_url = driver.current_url 
    #we are goign to grab the url and splice it; python string are immutable so you cant splice it, below is a work-around
    ext = current_url[current_url.find("&"):len(current_url)] +"&tab="
    #get key from the Ordered List of lOGS
    for key in OrderList:
	time.sleep(1)
	count = 0
	new_url = analyticsUrl + "index.html#dashboard?type=%s"%(str(key)) + ext
        time.sleep(1)
        logger.Log(logging.INFO, "\n")
	values = logDict[key]
    #create a link for each tab and analyse datatables and Charts
	for i in range (len(values)):
	    name = key + "-" + values[i].split(":")[0]
	    print("\n %s" %(name))
	    type = values[i].split(":")[1]
	    link = new_url + str(count)
	    try:
		time.sleep(2)
		driver.get(link)
		element = WebDriverWait(driver, 10).until(
		    EC.presence_of_element_located((By.CLASS_NAME, "jarviswidget")) 
		)
	    except TimeoutException:
		msg = "Failed: %s Log-Data-%s page did not load" % (role, name)
		logger.Log(logging.WARNING, msg)
		continue
	    else:
		msg = "Passed: %s Log-Data-%s page loaded" % (role, name)
		logger.Log(logging.INFO, msg)

 	    if type  == 'LOGS':
		time.sleep(2)
		#plan is to find each case for datatables and highchart and print it out, by counting the elements
		datatables_loaded = len(driver.find_elements_by_class_name("dt-wrapper")) #loaded charts
		print "datatables loaded: %s" %(datatables_loaded)
		datatables_nodata = len(driver.find_elements_by_class_name("dataTables_empty")) #nodata
		print "datatables with no data: %s" % (datatables_nodata)
		#dataTables_wrapper form-inline
		if datatables_loaded >= 0:
		    msg = "Success: %s Log-Data-%s page loaded %s datatables" % (role, name, datatables_loaded)
		    logger.Log(logging.INFO, msg)
		    print("%s Log-Datatables-%s page loaded %s datatables" % (role, name, datatables_loaded))            
		if datatables_nodata > 0:
		    msg = "Warning: %s Log-Data-%s page loaded %s datatables without data" % (role, name, datatables_nodata)
		    logger.Log(logging.WARNING, msg)

	    elif type == 'CHART':
		time.sleep(2)
		#highcharts there is either data or no data, if no data then hightcharts is broken
		highcharts_total = len(driver.find_elements_by_class_name("jarviswidget"))
		print "Highcharts total:" + str(highcharts_total)
		highcharts_without_data = len(driver.find_elements_by_class_name("highcharts-no-data"))
		print "Highcharts No Data:" + str(highcharts_without_data)
		highcharts_data = len(driver.find_elements_by_tag_name("defs"))
		print "Highcharts Data:" + str(highcharts_data)
		highcharts_broken = highcharts_total - highcharts_data
		print "Highcharts Broken:" + str(highcharts_broken)
		if highcharts_data > 0:
		    msg = "Success: %s Log-Data-%s page loaded %s highcharts with data" % (role, name, highcharts_data)
		    logger.Log(logging.INFO, msg)
		    print "%s Log-Data-%s page loaded %s highcharts with data" % (role, name, highcharts_data)
		if highcharts_without_data > 0:
		    msg = "Warning: %s Log-Data-%s page loaded %s higchart without data" % (role, name, highcharts_without_data)
		    logger.Log(logging.WARNING, msg)	   
		if highcharts_broken > 0:
		    msg = "Error: %s Log-Data-%s page loaded %s higchart is broken" % (role, name, highcharts_broken)
		    logger.Log(logging.ERROR, msg)
	    
	    count = count + 1


#############################################Static Url Variables Used For Site Navigation##############################################
sdwanNavTabs = ["Usage", "Availability", "Connections", "HeatMap"]
sdwanSiteTabs = ["Usage", "Availability", "Access Circuits", "Users", "Applications", "Rules", "SLA Metrics", "SLA Violations", "VRF", "QoS", "APM", "MOS" ]

class Globals:
  @staticmethod
  def loadConfigurations():
    try:
      import pdb; pdb.set_trace()
      parser = ConfigParser.SafeConfigParser()
      parser.read("/home/shreya/code/selenium/final/confile.cfg")
      print "Read conf file "
      
      Globals.config = {}
      
      # Configuration keys are saved in lowercase automatically
      for section in parser.sections():
        for key, value in parser.items(section):
          Globals.config[key] = value;
 
      print("Configurations loaded")
    except:
      print("Configuration parsing error: %s", sys.exc_info())
      raise Exception("Configuration parsing error")
  
coloredlogs.install(level="ERROR")
coloredlogs.install(level="WARNING")
driver = setupDriver()
logger = Logger(logFile="./analytics_log.txt")

def main():
    global analyticsUrl
    global role
    global password
    import pdb; pdb.set_trace()
    print "Entering main"
    Globals.loadConfigurations()
    logger.Log(logging.INFO, "Hello world")
    for key in Globals.config:
       print "Key %s Value %s" % (key, Globals.config[key])
    analyticsUrl = "http://%s:8080/xxx/app/" % (Globals.config['analyticsip'])
    role = Globals.config['role']
    password = Globals.config['password']

    print analyticsUrl
    ##############################Scripts Starts Here################################
    #log into analytics, if user has no credentials: log into director to create them
    try:
        if not analyticsLogin():
            if directorLogin():
                    if createOrganizationUser():
                        try:
                            if analyticsLogin(): raise Exception("Finished creating new user in director")
                        except Exception as finished:
                            print(finished)
                            pass
    except Exception:
        pass

    verifySystemParams()
    #check all the data for sd-wan site to make sure everything is loaded
    if verifyUserRoles():
        if verifySiteTabs():
            try:
                if verifySdwanData(): raise Exception("Finished running tests on sd-wan data loaded")
            except Exception as finished:
                print(finished)
                pass
    
    if navigate_sdwan_appliance_site():
        if verify_appliance_site_tabs():
            if verify_appliance_site_data(): 
    		print("finished")
    verifyLogsParam()

    #close everything
    #logger.close()
    driver.quit()


if __name__=="__main__":
    main()


