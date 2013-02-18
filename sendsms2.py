#!/usr/bin/env python

import sys
import time
from   urlparse import urlparse,parse_qs
import re
from   time import sleep
import traceback

#put way2sms credentials below
username = ""
password = ""

#post wait time in seconds, depends on connection speed.
post_wait = 8 

#Turn on debug to get additional information
debug = True 

#Useragent:
user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)"



try:
    import mechanize
except ImportError:
    print "Please install mechanize module for python"
    print "Install python-mechanize, if you are on a Ubuntu/Debian machine"
    sys.exit(1)
try:
    from optparse import OptionParser
except ImportError:
    print "Error importing optparse module"
    sys.exit(1)

 
class smsHandler():
   def __init__(self,username,password):
      print ">>> initializing.."
      if debug:
         print ">>> Debug: ON"
      self.username= username
      self.password= password
      self.idreg1  = re.compile('rqMob="([A-z]*)"')
      self.idreg2  = re.compile(r"<style type='text/css'>#([A-z]*){display:none;}</style>")
      self.tknreg  = re.compile('rqTok="([A-z]*)"')
      self.master     = "http://site3.way2sms.com/entry.jsp"
      self.authurl    = "http://site1.way2sms.com/Login1.action"
      self.sendsmsurl = "http://site1.way2sms.com/jsp/SingleSMS.jsp"
      self.smsposturl = "http://site1.way2sms.com/jsp/stp2p.action"
      self.br = mechanize.Browser()

   def coock_controls(self,html):
       self.id1  = self.idreg1.findall(html)[1]
       self.id2  = self.idreg2.findall(html)[0]
       self.tkn  = self.tknreg.findall(html)[1]

   def get_token(self,url):
       urlhandle  = urlparse(url)
       info       = parse_qs(urlhandle.query)
       self.token = info['id'][0]

   def do(self,mobile,text):
       print ">>> connecting to way2sms..."
       try:
          response = self.br.open(self.master)
          if debug:
             print ">>> %s/HTTP: %s" %  (self.master,response.code)
          self.br.select_form(name="loginform")
          self.br["username"] = self.username
          self.br["password"] = self.password
          self.br.form.method="POST"
          self.br.form.action=self.authurl
          print 30 * "-"  
          print self.br.title()
          print 30 * "-"  
          response = self.br.submit()
          if debug:
             print ">>> %s/HTTP: %s" %  (self.authurl,response.code)
       except:
          if debug:
             print "Debug information"
             print 25 * "*"
             print traceback.format_exc()
             print 25 * "*"
          print ">>> FATAL: Error occured while performing process!"
          sys.exit(1)
       try:
          self.get_token(response.geturl())
       except:
          if debug:
             print "Debug information"
             print 25 * "*"
             print traceback.format_exc()
             print 25 * "*"
          print ">>> Did not get proper Token ID/Error occured."
          print ">>> Please check your username/password."
          sys.exit(1)
       print ">>> Received Token: %s" % self.token
       print ">>> sending message..."
       print ">>> Opening %s?Token=%s" % (self.sendsmsurl,self.token)
       self.br.addheaders = [{"User-Agent": user_agent, 
			       "Referer": "%s?Token=%s" % (self.sendsmsurl,self.token)}]
       r = self.br.open("%s?Token=%s" % (self.sendsmsurl,self.token))
       if debug:
          print ">>> %s/HTTP: %s" %  (self.sendsmsurl,r.code)

       self.br.select_form(name="InstantSMS")
       if debug:
          print ">>> Setting InstantSMS form readonly: False."
       self.br.form.set_all_readonly(False)
       try:
          self.coock_controls(r.get_data())
          print ">>> ID1: %s, ID2: %s, TKN:%s" % (self.id1,self.id2,self.tkn)
       except:
          if debug:
             print "Debug information"
             print 25 * "*"
             print traceback.format_exc()
             print 25 * "*"
          print ">>> Error occured while processing dynamic ids."
          print ">>> Exiting."
          sys.exit(1)
       if debug:
          print ">>> Filling up form details.."
       try:
          self.br[self.id1]          = mobile
          self.br[self.id2]          = ''
          self.br[self.tkn]          = self.token
          self.br["textArea"]   = text
          self.br.form.method="POST"
          self.br.form.action=self.smsposturl
          self.br.form.fixup()
       except:
          if debug:
             print "Debug information"
             print 25 * "*"
             print traceback.format_exc()
             print 25 * "*"
          print ">>> Error occured while processing InstantSMS form."
          print ">>> Exiting."
          sys.exit(1)
       print ">>> submitting..."
       try:
          response = self.br.submit()
          if debug:
             print ">>> %s/HTTP: %s" %  (self.smsposturl,response.code)
       except:
          if debug:
             print "Debug information"
             print 25 * "*"
             print traceback.format_exc()
             print 25 * "*"
          print ">>> Error occured while submitting InstantSMS form."
          print ">>> Exiting."
          sys.exit(1)
       print ">>> Waiting...%s sec/POST wait." % post_wait
       sleep(post_wait)
       if debug:
          print ">>> %s/HTTP: %s" %  (response.geturl(),response.code)
       else:
          print response.geturl()
       print ">>> Closing session.."
       self.br.close()
       print ">>> Done."

def main():
    parser = OptionParser()
    usage = "Usage: %prog -m [number] -t [text]"
    parser = OptionParser(usage=usage, version="%prog 1.0")
    parser.add_option("-m", "--number",  action="store", type="string",dest="number",  help="Mobile number to send sms")
    parser.add_option("-t", "--text", action="store", type="string", dest="text", help="Text to send")
    (options, args) = parser.parse_args()
    if options.number and options.text:
       handler = smsHandler(username,password)
       handler.do(options.number,options.text)
    else:
       print "Fatal: Required arguments are missing!"
       print "Use: -h / --help to get help."

if __name__ == "__main__":
   main()
