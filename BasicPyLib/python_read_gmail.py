# -*- coding: utf-8 -*-
"""
Created on Sun Jun 29 15:19:05 2014

@author: Huapu (Peter) Pan
"""
import imaplib
import email
import datetime
import pytz
import re

class EmailObject(object):
    """
    EmailObject has 4 default attributes: From, To, Date, Content
    """
    def __init__(self, From, To, DateTime, Subject, Content):
        self.From = From; self.To = To
        self.DateTime = DateTime; self.Content = Content
        self.Subject = Subject
        if (len(self.From.split(' ')) > 0):
            self.FromName = self.From.split(' ')[0]
        else:
            self.FromName = ''
        if (len(self.To.split(' ')) > 0):
            self.ToName = self.To.split(' ')[0]
        else:
            self.ToName = ''
            
    def print_email(self):
        print "From: ", self.From
        print "To: ", self.To
        print "Time: ", self.DateTime
        print "Subject: ", self.Subject
        if len(self.Content) > 35:
            print "Content: ", self.Content[0:32] + '...'
        else:
            print "Content: ", self.Content
            
class ReadGmailObject(object):
    """
    ReadEmailObject reads and stores a certain number of emails from 
    specified email address
    """
    def __init__(self, user, passwd, emailServer = 'imap.gmail.com', DEBUG = False):
        """ determine US Eastern time zone depending on EST or EDT """
        if datetime.datetime.now(pytz.timezone('US/Eastern')).tzname() == 'EDT':
            self.USeasternTimeZone = pytz.timezone('Etc/GMT+4')
        elif datetime.datetime.now(pytz.timezone('US/Eastern')).tzname() == 'EST':
            self.USeasternTimeZone = pytz.timezone('Etc/GMT+5')   
        else:
            self.USeasternTimeZone = None
        # user and passwd
        self.emailServer = emailServer
        self.user = user; self.passwd = passwd
        self.mail = imaplib.IMAP4_SSL(self.emailServer, '993')
        self.mail.login(self.user, self.passwd)
        
        # if print DEBUG info or not
        self.DEBUG = DEBUG
    
    def destructor(self):
        self.mail.logout()
        
    def convert_string_date_to_time(self, dateString):
        """
        this function converts the date/time in the email to python datetime
        object, and should be overwritten in the derived class if date/time 
        format is different
        """
        if (self.DEBUG):
            print "input time string: ", dateString
        dateStringNoTimeZone = ' '.join(dateString.split(' ')[:-1])
        emailDateTime = datetime.datetime.strptime(dateStringNoTimeZone, '%d %b %Y %H:%M:%S')
        if (dateString.split(' ')[-1] == '+0000'):
            rawTimeZone = '+0'
        else:
            rawTimeZone = dateString.split(' ')[-1][:3]
            if (rawTimeZone[2] != 0): # if rawTineZone is not +10 or -10, remove addtional 0
                rawTimeZone = re.sub('0', '', rawTimeZone)
            # flip +/- sign because the displayed timezone is in UTC
            if (rawTimeZone[0] == '-'):
                rawTimeZone = '+' + rawTimeZone.strip('-')
            elif (rawTimeZone[0] == '+'):
                rawTimeZone = '-' + rawTimeZone.strip('+')
        timeZone = pytz.timezone('Etc/GMT' + rawTimeZone)
        emailDateTime = emailDateTime.replace(tzinfo = timeZone)
        emailDateTime = emailDateTime.astimezone(self.USeasternTimeZone)
        if (self.DEBUG):
            print "time zone: ", rawTimeZone
            print "converted time: ", emailDateTime
        return emailDateTime

    def read_email(self, numberOfEmails = 1, emailFolder = 'Inbox', 
                   emailType = 'UnSeen', emailFrom = '#ALL#', 
                   emailDays = [], readStartFrom = 0, webParsingTimesToTry = 5):
        """
        the function read_email has several options:
            numberOfEmails is the number of emails to be read
            emailFolder is the folder in the email to be read
            emailType is the type of emails to be read ('UnSeen', 'All', etc)
            emailFrom is the name of the email sender (not email address), 
                and '#ALL#' refers to all email senders
            emailDay is the list of days or a tuple of closed day range of 
            the email to be read, format of its element is 
            %Y(xxxx)-%M(xx)-%D(xx) (eg. '2014-07-11'), and order should be 
            ascending (earlier dates first)
        """
        self.emailList = []
        flagMessageRead = False
        for ii in range(webParsingTimesToTry):
            try:
                self.mail.select(emailFolder)
                typ ,data = self.mail.search(None, emailType)
                flagMessageRead = True
                break
            except:
                try:
                    self.mail = None
                    self.mail = imaplib.IMAP4_SSL(self.emailServer, '993')
                    self.mail.login(self.user, self.passwd)
                    print 're-login at: ', datetime.datetime.now(self.USeasternTimeZone)
                except:
                    pass
        if (not flagMessageRead):
            return flagMessageRead
        ids = data[0] # data is a list.
        if (self.DEBUG):
            print data
        id_list = ids.split() # ids is a space separated string
        latest_email_id = int( id_list[-1])
        #iterate through all messages in decending order starting 
        # with the latest email to find all the emails that satisfy the
        # criteria
        if (emailDays != [] and isinstance(emailDays, list)):
            emailDays.sort() # sort to make sure ascending order 
        ii = readStartFrom; matched_ii = 0; strEmailDate = emailDays[-1]
        while (matched_ii < numberOfEmails # number of matched
        and ii < latest_email_id # not exceed total number of emails
        and (emailDays == [] or strEmailDate >= emailDays[0])):
            # either no requirement on dates or current email date later 
            # than the earliest date in the emailDays list
           typ, data = self.mail.fetch(latest_email_id-ii, '(RFC822)' )
           for response_part in data:
              # find the tuple in data
              if isinstance(response_part, tuple):
                  msg = email.message_from_string(response_part[1])
                  emailDateTime = self.convert_string_date_to_time(\
                  msg['Date'].split(',')[1].strip(' '))
                  strEmailDate = str(emailDateTime).split(' ')[0]
                  if (self.DEBUG):
                      print "From: ", msg['From'].split(' ')[0], emailFrom
                      print "email Day:", strEmailDate, emailDays, \
                      strEmailDate
                  if (emailFrom == '#ALL#' or msg['From'].split(' ')[0] == \
                  emailFrom):
                      if (emailDays == [] or (isinstance(emailDays, list) and\
                      strEmailDate in emailDays) or (isinstance(emailDays, \
                      tuple) and strEmailDate <= emailDays[-1])):
                          self.emailList.append(
                              EmailObject(From = msg['From'], 
                                          To = msg['To'], 
                                        DateTime = emailDateTime, 
                                        Subject = msg['Subject'], 
                                        Content = msg._payload))
                          # increase matched count only when match found  
                          matched_ii += 1
           #  increase email id count in every loop               
           ii += 1
        # sort the email
        self.emailList = sorted(self.emailList, key = lambda x: x.DateTime)
        if (self.DEBUG):
            for emailObj in self.emailList:
                emailObj.print_email()
        
        return flagMessageRead

if __name__ == "__main__":
    t = ReadGmailObject(user = 'peterfflom', passwd = 'peterfflommessage', 
                        DEBUG = True)
    t.read_email(numberOfEmails = 1000, emailType = 'ALL', emailFrom = 'gold', 
                 emailDays = ('2014-07-09','2014-07-14'))
    
    print "Finished!"