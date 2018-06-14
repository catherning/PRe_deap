# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 14:02:08 2018

@author: cx10
"""

# globals.py
# containing global variables
import datetime
MAXTIME = datetime.datetime(9999, 12, 31, 23, 59, 59)

cloudStorageWebsites = ['http://www.4shared.com/','http://1and1.com/','https://archive.org/','http://bluehost.com/','http://bp.blogspot.com/','http://yousendit.com/','http://yfrog.com/','http://webs.com/','http://twitpic.com/','http://soundcloud.com/','http://secureserver.net/','http://custhelp.com/','http://megaupload.com/','http://megaclick.com/','http://hostgator.com/','http://flippa.com/','https://www.dropbox.com/']
hacktivistWebsites = ['http://wikileaks.org/']
jobHuntingWebsites = ['http://northropgrumman.com/','http://lockheedmartin.com/','http://careerbuilder.com/','http://craigslist.org/','http://simplyhired.com/','http://monster.com/','http://jobhuntersbible.com/','http://job-hunt.org/','http://indeed.com/','http://linkedin.com/']
ex = 'http://tw.rpi.edu/ontology/DataExfiltration/'
a = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
xsd = 'http://www.w3.org/2001/XMLSchema#'

# Average logon time of first 10 days -15min
# dailyStartDic = {'ACM2278': datetime.time(7,12,12), \
#                'CMP2946': datetime.time(8,42,36), \
#                'CDE1846': datetime.time(8,27,6), \
#                'MBG3183': datetime.time(7,56,36) }
# # Average logoff of first 10 days +15min
# dailyEndDic = {'ACM2278': datetime.time(17,49,48), \
#               'CMP2946': datetime.time(18,18,36), \
#               'CDE1846': datetime.time(19,1,24), \
#               'MBG3183': datetime.time(17,29,54) }
#
# usbDriveUsageFrequency = {'ACM2278': 0, 'CMP2946': 5.1, 'PLJ1771': 0, 'CDE1846': 0, 'MBG3183': 1.9 }