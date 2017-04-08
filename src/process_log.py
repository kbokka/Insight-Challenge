# your Python code to implement the features could be placed here
# note that you may use any language, there is no preference towards Python
# -*- coding: utf-8 -*-
import re
import sys
import copy
from collections import defaultdict

class InputData:
    def __init__(self, file, hostFile, resourceFile, hoursFile, blockedFile):
        """InputData's memeber variables contian lists to store the various data from the log file
            self.host contains list of all host names
            self.timeStamp contains list of all the timestamps in the format ["[DD/MON/YYYY:HH:MM:SS -0400]", ....]
            self.request constinas a list of all the requests in the format [["request"],....]
            self.replyCode contians a list of all response codes
            self.bytes contains the list bytes 
            self.timeZone contains the list of all time zones seperated from self.timeStamp
            self.activeHosts contains a dictionary with the key values pairs as (host, number of visits host as accessed the site (int)]
            
            Functionality for active hosts is in the looping structures for read data
        """
        #check if file path is valid
        if not file:
            raise ValueError("Error accessing input file.")

        self.host = []
        self.timeStamp = []
        self.request = []
        self.replyCode = []
        self.bytes = []
        self.timezZone = []
        self.activeHosts = {}

        #reads in the data
        with open(file, "r") as myFile:
            lines = myFile.readlines()
        i = 0
        while i != len(lines):
            temp = lines[i].split()
            self.request.append(((re.findall(r'\".*\"', lines[i]))))
            self.host.append(temp[0].strip())
            self.timeStamp.append(temp[3].strip())
            self.timezZone.append(temp[4].strip())
            self.replyCode.append(temp[-2].strip())
            self.bytes.append(temp[-1].strip())

            #create hashtable to count most visited
            if self.host[i] in self.activeHosts:
                self.activeHosts[self.host[i]] += 1
            else:
                self.activeHosts[self.host[i]] = 1
            i+=1

        #sorts the dictionary of active hosts based on its value and writes it to the corresponding file
        activeUsers = sorted(self.activeHosts.items(), key=lambda x:x[1], reverse=True)
        self.writeTopTen(activeUsers[0:10], hostFile)

        #all features are called here
        self.determineTopTenResources(resourceFile)
        self.determineTopTenHours(hoursFile)
        self.determineBlocked(blockedFile)


    #writes the top 10 hosts to corresponding file (Feature 1)
    def writeTopTen(self, data, file):
        lines = ""
        for values in data:
            lines += values[0] + "," + str(values[1]) + "\n"
        with open(file, "w") as myFile:
            myFile.write(lines)
        pass

    #writes the top 10 used resources to corresponding file (Feature 2)
    def writeTopTenResources(self, data, file):
        lines = ""
        for values in data:
            lines += "{}\n".format(values[0])
        pass
        with open(file, "w") as myFile:
            myFile.write(lines)

    #writes the top 10 time periods to corresponding file (Feature 3)
    def writeTopTenHours(self, data, file):
        lines = ""
        i = 0
        while i != len(data):
            lines += data[i][0] + "," + str(data[i][1]) + "\n"
            i+=1
        with open(file, "w") as myFile:
            myFile.write(lines)
        pass

    # writes all blocked users to corresponding file (Feature 4)
    def writeBlocked(self, data, file):
        if "\r" in file:
            newFile = file.split("\r")
        with open(newFile[0], "w") as myFile:
            myFile.write(data)
        pass

    """ Feature 2
        This function determines which resources are consumed the most based on the log file
        self.resoruces is a dictionary that holds the data the following format {resource name: number of bytes}
        the dictionary is sorted based on the number of bytes and written to a file
    """
    def determineTopTenResources(self, file):
        #create hashtable to get most accesed resources
        self.resources = {}
        i = 0
        #print(self.request)
        while i != len(self.request):
            temp = ((self.request[i][0].split()))
            if len(temp) > 1:
                if temp[1] in self.resources:
                    if self.bytes[i] == "-":
                        self.resources[temp[1]] += 0
                    else:
                        self.resources[temp[1]] += int(self.bytes[i])
                else:
                    if self.bytes[i] == "-":
                        self.resources[temp[1]] = 0
                    else:
                        self.resources[temp[1]] = int(self.bytes[i])
            i+=1
        activeResources = sorted(self.resources.items(), key=lambda x: x[1], reverse=True)
        self.writeTopTenResources(activeResources[0:10], file)

    """ Feature 3
        This function determines the most active 1 hour time periods
        self.time contains a list that tracks the number of times the site has been accessed for the 60 minute intervals and sorts the the list based on the second index of each list
        self.time has the format ["time stamp", number of visits]
    """
    def determineTopTenHours(self, file):
        # need to handle day changes, month changes, and year changes
        i = 0
        self.time = []
        # inatalize time list of all elements
        while i != len(self.timeStamp):
            self.time.append([self.timeStamp[i].split("[")[1] + " " + self.timezZone[i].split("]")[0], 0])
            i += 1

        self.newTime = copy.deepcopy(self.time)  # need this for part 4 functionality

        # determine number of hits in 60 min interval
        i = 0

        limit = int(self.time[0][0].split(":")[1]) + 1
        j = 0
        count = 0
        flag = 0
        while i != len(self.time) and j != len(self.time):
            hour = int(self.time[i][0].split(":")[1])
            if hour > limit:
                self.time[j][1] = count
                j += 1
                count -= 1
                limit = int(self.time[j][0].split(":")[1]) + 1
            else:
                count += 1
            if i + 1 == len(self.time) and i != j:
                flag = 1
            i += 1

        if flag == 1:
            prev = self.time[j][0]
            self.time[j][1] = count
            count -= 1
            j += 1
            while j != len(self.time):
                # print(prev, self.time[j][0])
                if prev != self.time[j][0]:
                    self.time[j][1] = count
                    count -= 1
                    prev = self.time[j][0]
                else:
                    prev = self.time[j][0]
                    del self.time[j]
                    count -= 1
                j += 1
        if self.time[j - 2][1] == 0:
            del self.time[j - 2]
        self.time.sort(key=lambda x: x[1], reverse=True)
        self.writeTopTenHours(self.time[0:10], file)

    """Feature 4
       This function determines who should be blocked based on the criteria set by feature 4
       blocked is a dictionary with the following format {host name: number of failed attempts}
       blockedTime is a dictionary with the following format (host name: time stamp)
       blockedSecTime is a dictionary with the following fomrat {host name: (previous time stamp converted to seconds, total amount time in seconds)}
       lines is the string of data to be written into the corresponding file
    """
    def determineBlocked(self, file):
        # detect failed login attempts
        i = 0
        # create hashmap and put each host with a 401 reply code
        blocked = {}  # holds the number of times host has been blocked
        blockedTime = defaultdict(list)  # holds list of timestamps for host
        blockedSecTime = defaultdict(list)
        lines = ""
        while i != len(self.host):
            # print(self.host[i], self.replyCode[i], self.newTime[i], (self.timeStamp[i].split(":")))
            if self.replyCode[i] == '401' and self.host[i] in blocked:
                blocked[self.host[i]] += 1
                blockedTime[self.host[i]].append(self.newTime[i])  # add all other data to print in this dictionary
                blockedSecTime[self.host[i]][0][1] = ((int(self.timeStamp[i].split(":")[3]) + (
                int(self.timeStamp[i].split(":")[2]) * 60) + (int(self.timeStamp[i].split(":")[1]) * 3600)) -
                                                      blockedSecTime[self.host[i]][0][0]) + \
                                                     blockedSecTime[self.host[i]][0][1]
                blockedSecTime[self.host[i]][0][0] = int(self.timeStamp[i].split(":")[3]) + (
                int(self.timeStamp[i].split(":")[2]) * 60) + (int(self.timeStamp[i].split(":")[1]) * 3600)
                if blocked[self.host[i]] > 3 and blockedSecTime[self.host[i]][0][
                    1] <= 300:  # and blockedSecTime[self.host[i]][0][1] <= 300:
                    lines += self.host[i] + " - - " + "[{}] ".format(
                        self.newTime[i][0])  # need to add in web address and reply codes and byte size
                    webAddress = re.match(r'\".*\"', self.request[i][0])
                    if webAddress:
                        lines += webAddress.group() + " {} ".format(self.replyCode[i]) + "{}\n".format(self.bytes[i])
                elif blockedSecTime[self.host[i]][0][1] > 300:
                    blockedSecTime[self.host[i]][0][0] = 0
                    blockedSecTime[self.host[i]][0][1] = 0
                    blockedSecTime[self.host[i]] = 0
            elif self.replyCode[i] == '401' and not (self.host[i] in blocked):
                blocked[self.host[i]] = 1
                blockedTime[self.host[i]] = self.newTime[i]
                blockedSecTime[self.host[i]].append([int(self.timeStamp[i].split(":")[3]) + (
                int(self.timeStamp[i].split(":")[2]) * 60) + (int(self.timeStamp[i].split(":")[1]) * 3600), 0])
            elif self.replyCode[i] != '401' and self.host[i] in blocked:
                if blocked[self.host[i]] > 3 and blockedSecTime[self.host[i][0][1]] <= 300:
                    blocked[self.host[i]] += 1
                    lines += self.host[i] + " - - " + "[{}] ".format(
                        self.newTime[i][0])  # need to add in web address and reply codes and byte size
                    webAddress = re.match(r'\".*\"', self.request[i][0])
                    if webAddress:
                        lines += webAddress.group() + " {} ".format(self.replyCode[i]) + "{}\n".format(self.bytes[i])
                elif blockedSecTime[self.host[i]][0][1] > 300:
                    blockedSecTime[self.host[i]][0][1] = 0
                    blockedSecTime[self.host[i]][0][0] = 0
                    blockedSecTime[self.host[i]] = 0

            i += 1
        self.writeBlocked(lines, file)
    pass

if __name__ == "__main__":
    filePaths = []
    for arg in sys.argv[1:]:
        filePaths.append(arg)

    #check if input data file is provided
    if filePaths and filePaths[0]:
        values = InputData(filePaths[0], filePaths[1], filePaths[3], filePaths[2], filePaths[4])
    else:
        raise TypeError("Error, not input data file provided")
