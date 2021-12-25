#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 21 09:44:04 2021
@author: Atul Ghumade
"""

######## Import all modules ######################################################
import getpass
import subprocess
import re
import os
from time import sleep
from shutil import copyfile,rmtree
import pyudev
import psutil
import ntpath
import logging
from NVConfig import *
#################################################################################
if not os.path.isdir('/home/{}/.config/NV'.format(getpass.getuser())):
    os.makedirs('/home/{}/.config/NV'.format(getpass.getuser()))
    
if(getDebugMode() == 'ON'):
    logging.basicConfig(filename='/home/{}/.config/NV/app.log'.format(getpass.getuser()), filemode='w+', format='%(name)s - %(levelname)s - %(message)s')
    logging.warning('Logging Started!!!')

####### Browser Names and Path ##################################################
walletName = "NatiVault"
shortName = "NatiVault"
AllowedProcesses = ["NatiVault"]
#browserPath = '/tmp/{}'.format(walletName)
browserPath = '/home/{}/.config/NV/{}'.format(getpass.getuser(),walletName)

#browserPath = '/home/{}/{}'.format(getpass.getuser(),walletName)
#################################################################################

############### Pyudev Context Declaration ######################################
context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by('block')
removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
#################################################################################

#################### USB Related Funtions #######################################
def mount(devicePartition):
    try:
        os.system("udisksctl mount -b {}".format(devicePartition))
        #print("Mounted")
    except:
        if(getDebugMode() == 'ON'):
            logging.error("Unable to Mount %s"%devicePartition)

def unmount(devicePartition):
    try:
        os.system("udisksctl unmount -b {}".format(devicePartition))
        #print("Unmount")
    except:
        if(getDebugMode() == 'ON'):
            logging.error("Unable to UnMount %s"%devicePartition)        

def USBPath(devicePartition):
    #print(psutil.disk_partitions())
    try:
        for p in psutil.disk_partitions():
            if p.device in devicePartition:
                if(p.mountpoint != ""):
                    return p.mountpoint
    except:
        if(getDebugMode() == 'ON'):
            logging.error("Unable to load the USB Path. Function: USBPath()")          
               
def ValidateUSB(devRef):
    try:
        #print(getDeviceFirstTime())
        if(getDeviceFirstTime()):
            setVID(devRef.get("ID_VENDOR_ID").upper())
            setPID(devRef.get("ID_MODEL_ID").upper())
            setDeviceFirstTime(False)
            
        SavedUSBInfoDict = {"VID": getVID(), "PID": getPID()} 
        liveUSBInfoDict = {"VID": devRef.get("ID_VENDOR_ID").upper(), "PID": devRef.get("ID_MODEL_ID").upper()}
        return liveUSBInfoDict == SavedUSBInfoDict
    except:
        pass
#        print("Please connect ZeroV device")
#        logging.error("Please connect ZeroV device. Loading ZeroV Device Error. Function: ValidateUSB()")  
    
def getZeroVDevice():
    try:
        for device in removable:
            if ValidateUSB(device):
                partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
                for p in psutil.disk_partitions():
                    #print(p.device)
                    if p.device in partitions:
                        if(p.mountpoint != ""):
                            return {"partition": p.device, "devicePath": p.mountpoint}
    except:
        pass
        #logging.error("Unable to get the path of ZeroV device. Function: getZeroVDevice()")  

def getPartition(deviceRef):
    try:
        dev_partition = [deviceRef.device_node for deviceRef in context.list_devices(subsystem='block', DEVTYPE='partition', parent=deviceRef)]
        return dev_partition[0]
    except:
        if(getDebugMode() == 'ON'):
            logging.error("Unable to get the Partition. Function: getPartition()") 

def usbEvent():
    oneTimewritten = False
    for device in iter(monitor.poll, None):
        try:
            if all([device['ACTION'] == "add", 'ID_FS_TYPE' in device,device['ID_USB_DRIVER'] == "usb-storage",ValidateUSB(device),]):
                print("NV Inserted")
                global device_partition
                device_partition = getPartition(device)
                #unmount(device_partition)
                if(oneTimewritten == False):
                    setDevicePartition(device_partition)
                    oneTimewritten = True
                copySoftware()
                startBrowser()
            elif all([device['ACTION'] == "remove", 'ID_FS_TYPE' in device,device['ID_USB_DRIVER'] == "usb-storage",]):  #ToDo: Handle the same device removal
                print("NV Removed")
                killBrowser()
                deleteBrowser()
        except:
            if(getDebugMode() == 'ON'):
                logging.error("USB Events are not functioning. Function: usbEvent()")
#################################################################################################################################################

############################################ Browser Based Functions ############################################################################

def get_active_window_title():
    try:
        root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
        stdout, stderr = root.communicate()
        m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)
        if m != None:
            window_id = m.group(1)
            window = subprocess.Popen(['xprop', '-id', window_id, 'WM_NAME'], stdout=subprocess.PIPE)
            stdout, stderr = window.communicate()
        else:
            return None
        match = re.match(b"WM_NAME\(\w+\) = (?P<name>.+)$", stdout)
        if match != None:
            return match.group("name").strip(b'"').decode('UTF-8')
        return None
    except:
        if(getDebugMode() == 'ON'):
            logging.error("Get Active Window Title Section not functioning. Function: get_active_window_title()")

def copySoftware():
    sleep(2) #Mandatory
    if(not os.path.exists(browserPath)):
        try:
            #print(getZeroVDevice()['devicePath']+'/'+walletName,browserPath)
            copyfile(getZeroVDevice()['devicePath']+'/'+walletName,browserPath)
            #copyfile(USBPath(device_partition)+'/'+walletName,browserPath)
            os.chmod(browserPath,0o777)
        except:
            if(getDebugMode() == 'ON'):
                logging.error("Unsble to copy NatiVault: copySoftware()")
            print("Please insert NV Device.")
            return -1

        
def startBrowser():
    #browserPath = '/home/{}/{}'.format(getpass.getuser(),walletName)
    try:
        #PopUpMessage("Before Starting Software")
        os.system(browserPath +" &")
        #PopUpMessage("After Starting Software")
    except:
        print("Unable to run the Browser")
        if(getDebugMode() == 'ON'):
            logging.error("Browser Unable to start Function: startBrowser()")
    
def killBrowser():
    os.system("killall NatiVault")
    #os.system("killall /tmp/.mount_electr*/usr/bin/python3.7")
    #os.system("killall {}".format(shortName))
    
def deleteBrowser():
    #browserPath = '/home/{}/{}'.format(getpass.getuser(),walletName)
    try:
        #print("Delete Browser Path: {}".format(browserPath))
        os.remove(browserPath)
    except:
        print("{} Not available".format(browserPath))


def windowMonitor():
    InsertedFlag = False
    while True:
        try:
            window = get_active_window_title()
        except:
            continue
        if(window != None):
            strippedData = window.strip()
            arr = strippedData.split()
    #       print(window)
            if(arr[0] in AllowedProcesses):
                if(InsertedFlag == False):
                    mount(device_partition)
                    InsertedFlag = True
            else:
                if(InsertedFlag == True):
                    unmount(device_partition)
                    InsertedFlag = False
            sleep(0.2)
        else:
            if(InsertedFlag == True):
                unmount(device_partition)
                InsertedFlag = False

def files_folders_monitor():
    allow_files = ['NatiVault']
    allow_dirs = ['.config','pyethapp','keystore']
    getZeroVDevice()#Generating New USB Config
    while True:
        try:
            devicePartitionPath = getZeroVDevice()
            if(devicePartitionPath != None):
                path = devicePartitionPath['devicePath']
                for root,d_names,f_names in os.walk(path):
                    if(ntpath.basename(root) != 'keystore'):
                        for file in f_names:
                            if(file in allow_files):
                                pass
                            else:
                                os.remove(os.path.join(root,file))
                                unmount(device_partition)
                                
                        for folder in d_names:
                            if(folder in allow_dirs):
                                pass
                            else:
                                rmtree(os.path.join(root,folder))
                                unmount(device_partition)
                    else:
                        for folder in d_names:
                            if(folder in allow_dirs):
                                pass
                            else:
                                rmtree(os.path.join(root,folder))
                                unmount(device_partition)
                                
                        for file in f_names:
                            if(len(file) >= 35):
                                pass
                            else:
                                os.remove(os.path.join(root,file))
                                unmount(device_partition)
            else:
                pass
            sleep(0.001)
        except:
            if(getDebugMode() == 'ON'):
                logging.error("Files and folders monitoring failed Function: files_folders_monitor()")
             
#################################################################################################################################
            
if __name__ == "__main__":
#   print(getDeviceFirstTime())
    print(getZeroVDevice())
#    copySoftware()
#    windowMonitor()
#    USBThread = Thread(target=usbEvent)
#    BrowserThread = Thread(target=windowMonitor)
#    USBThread.start()
#    BrowserThread.start()
#    USBThread.join()
#    BrowserThread.join()
