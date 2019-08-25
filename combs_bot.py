#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket, ssl
import time
from prettytable import PrettyTable
from ping import Pinger
import os
import datetime
from scan import is_up, is_down

version = "0.19"
edit_date = "09.19.2017"
create_date = "09.15.2017"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "iss.cat.pdx.edu" # Server
#channel = "#Arctic" # Channel
channel = "#catacombs" # Channel
botnick = "ET_Phone_Comb" # Bots nick
adminname = "Arctic" #admin IRC nickname
exitcode = "kill" #Text that we will use to stop bot
filename = "/home/combscat/Documents/bots/combs_bot/kittenz.pdx.edu.db" #filename to read hosts from
news_filename = "/home/combscat/Documents/bots/combs_bot/news.txt" #filename to read news from 
art_backup = "/var/lib/tftpboot/art_backup.cfg"
science_backup = "/var/lib/tftpboot/science_backup.cfg"
catacombs_url = "https://chronicle.cat.pdx.edu/projects/braindump/wiki/Guide_to_the_Catacombs_2016"
tiered_url = "https://chronicle.cat.pdx.edu/projects/braindump/wiki/Zombie_Tiered_Progression"
delay = 0.9
secret = "mattsonly"

s.connect((server, 6697)) # Connect to the server using the port 6667
ircsock = ssl.wrap_socket(s)
ircsock.send(bytes("USER "+ botnick +" "+ botnick +" "+ botnick + " " + botnick + "\n")) # user information
ircsock.send(bytes("NICK "+ botnick +"\n")) # assign the nick to the bot

def joinchan(chan): # join channel(s).
  ircsock.send(bytes("JOIN "+ chan + " " + secret +"\r\n")) 
  ircmsg = ""
  while ircmsg.find("End of /NAMES list.") == -1: 
    ircmsg = ircsock.recv(2048).decode("UTF-8")
    ircmsg = ircmsg.strip('\n\r')
    print(ircmsg)

def ping(): # respond to server Pings.
  ircsock.send(bytes("PONG :pingis\n"))

def sendmsg(msg, target=channel): # sends messages to the target.
  #With this we are sending a ‘PRIVMSG’ to the channel. The ":” lets the server separate the target and the message.
  ircsock.send(bytes("PRIVMSG "+ target +" :"+ msg +"\n"))
  time.sleep(delay)

def display_news(target=channel):
  file_obj = open(news_filename, 'r')
  print "opening " + news_filename
  news_time = datetime.datetime.fromtimestamp(os.path.getmtime(news_filename))
  print news_time.strftime("%A, %B %d %Y %I:%M%p")
  sendmsg("CATACOMBS NEWS " + news_time.strftime("%A, %B %d %Y %I:%M%p"), target)
  for line in file_obj:
    print line
    sendmsg("-" + line, target)
  file_obj.close()

def load_hosts(): #creates a dictionary of hosts
  file_obj = open(filename, 'r') 
  temp = []
  hosts = {}
  count = 0
  garbage = True
  second = False

  while(garbage):
    line = file_obj.readline()
    if(line[0] == ';' and second == False):
      #at the first ';' so ignore and set second flag
      second = True	
    elif(line[0] == ';'):
      #we are at the ';' before where we want to start reading in
      garbage = False
      line = file_obj.readline()
      while(line[0] != ';'):
        line = line.split() #split tabs
        print line
	hostname = line[0]
	print "hostname: " + hostname
        ip = line[2]
	print "ip: " + ip
        comment = " "
	comment = comment.join(line[4:])
	print "comment: " + comment
        fqdn = hostname + ".kittenz.pdx.edu"
    	pinger = Pinger(target_host=ip)
	avg = pinger.ping()
    	ping = "%0.4fms" % avg
        info = {"hostname":hostname, "ip":ip, "owner":comment, "fqdn":fqdn, "ping":ping}
        hosts[hostname] = info 
        line = file_obj.readline()

  print "Hosts have been read in from " + filename + "."
  print hosts
  file_obj.close()
  return hosts

def display_hosts(sort = "IP", target = channel):
  hosts = load_hosts()
  hosts_table = PrettyTable()
  hosts_table.field_names = ["HOSTNAME","OWNER","FQDN","IP","PING"]
  info = ["","","","",""]
  for key, value in hosts.iteritems():
    hosts_table.add_row([value["hostname"],value["owner"],value["fqdn"],value["ip"],value["ping"]])
  hosts_table.align = "l"
  #hosts_table.border = False
  #print hosts_table.get_string(sortby="IP")

  sendmsg_table(hosts_table, target, sort)

def display_backups(target=channel):
  art_time = datetime.datetime.fromtimestamp(os.path.getmtime(art_backup))
  science_time = datetime.datetime.fromtimestamp(os.path.getmtime(science_backup)) 
  backup_table = PrettyTable()
  backup_table.field_names = ["SWITCH","LOCATION","LAST BACKUP (MTIME)"]
  row = ["art", "dennis @ " + art_backup, art_time.strftime("%A, %B %d %Y %I:%M%p")]
  backup_table.add_row(row) #add art row
  row = ["science", "dennis @ " + science_backup, science_time.strftime("%A, %B %d %Y %I:%M%p")]
  backup_table.add_row(row) #add science row
  backup_table_str = backup_table.get_string(sortby="SWITCH") #get string of table
  backup_lines = backup_table_str.split('\n') #put each line of table into list
  for line in backup_lines: #send msg to irc line by line
    print line
    sendmsg(line, target)

def display_version(target=channel):
  sendmsg(botnick + " version: " + version, target)

def display_about(target=channel):
  about_table = PrettyTable()
  about_table.field_names = [""]
  about_table.add_row(["v."+version])
  about_table.add_row([edit_date])
  about_table.add_row([create_date])
  about_table.add_row(["~arctic"])
  about_table.border = False
  about_table.header = False
  sendmsg_table(about_table, target)

def display_free(show_kittenz=True, target=channel):
  free_table = PrettyTable()
  #free_table.field_names=["N00BS", "JUMPSTART", "PROJECTS", "KITTENZ-N00BS"]
  names=["N00BS", "JUMPSTART", "PROJECTS", "KITTENZ-NOOBS"]
  sendmsg("Scanning available IP's on N00bs vlan...", target)
  noobs = is_down("131.252.211.194-222")
  sendmsg("Scanning available IP's on Jumpstart vlan...", target)
  jumpstart = is_down("131.252.211.226-238")
  sendmsg("Scanning available IP's on Projects vlan...", target)
  projects = is_down("131.252.211.242-254")
  if(show_kittenz == True):
    sendmsg("Scanning available IP's on kittenz-N00bs vlan (takes awhile)...", target)
    kittenz = is_down("10.218.201.4-254")
    increment = len(kittenz) / 5
    start = 0
    end = increment
    kittenz1 = kittenz[start:end]  
    start = start + increment
    end = end + increment
    kittenz2 = kittenz[start:end]  
    start = start + increment
    end = end + increment
    kittenz3 = kittenz[start:end]  
    start = start + increment
    end = end + increment
    kittenz4 = kittenz[start:end]  
    start = start + increment
    #end = end + increment
    kittenz5 = kittenz[start:] 
 
  #find host list with the most entries
  noobs_size = len(noobs)
  jumpstart_size = len(jumpstart)
  projects_size = len(projects)
  kittenz_size = 0
  if(show_kittenz == True):
    kittenz1_size = len(kittenz1)
    kittenz2_size = len(kittenz2)
    kittenz3_size = len(kittenz3)
    kittenz4_size = len(kittenz4)
    kittenz5_size = len(kittenz5)
  
  list_lens = [noobs_size, jumpstart_size, projects_size]
  if(show_kittenz == True):
    list_lens.append(kittenz1_size)
    list_lens.append(kittenz2_size)
    list_lens.append(kittenz3_size)
    list_lens.append(kittenz4_size)
    list_lens.append(kittenz5_size)
  max_len = max(list_lens)
  #extend lists so they all have the same len()
  jumpstart.extend('' for _ in xrange(max_len - jumpstart_size))
  noobs.extend('' for _ in xrange(max_len - noobs_size))
  projects.extend('' for _ in xrange(max_len - projects_size))
  if(show_kittenz == True):
      kittenz1.extend('' for _ in xrange(max_len - kittenz1_size))
      kittenz2.extend('' for _ in xrange(max_len - kittenz2_size))
      kittenz3.extend('' for _ in xrange(max_len - kittenz3_size))
      kittenz4.extend('' for _ in xrange(max_len - kittenz4_size))
      kittenz5.extend('' for _ in xrange(max_len - kittenz5_size))

  free_table.add_column("N00BS",noobs)
  free_table.add_column("JUMPSTART",jumpstart)
  free_table.add_column("PROJECTS",projects)
  if(show_kittenz == True):
      free_table.add_column("KITTENZ-N00BS",kittenz1)
      free_table.add_column("KITTENZ-N00BS",kittenz2)
      free_table.add_column("KITTENZ-N00BS",kittenz3)
      free_table.add_column("KITTENZ-N00BS",kittenz4)
      free_table.add_column("KITTENZ-N00BS",kittenz5)
  free_table.align = "l"
  sendmsg_table(free_table, target)
  return free_table

def display_free_kittenz(target=channel):
  free_table = PrettyTable()
  sendmsg("Scanning available IP's on kittenz-N00bs vlan (takes awhile)...", target)
  kittenz = is_down("10.218.201.4-254")
  increment = len(kittenz) / 7
  start = 0
  end = increment
  kittenz1 = kittenz[start:end]  
  start = start + increment
  end = end + increment
  kittenz2 = kittenz[start:end]  
  start = start + increment
  end = end + increment
  kittenz3 = kittenz[start:end]  
  start = start + increment
  end = end + increment
  kittenz4 = kittenz[start:end]  
  start = start + increment
  end = end + increment
  kittenz5 = kittenz[start:end]  
  start = start + increment
  end = end + increment
  kittenz6 = kittenz[start:end]  
  start = start + increment
  kittenz7 = kittenz[start:] 

  #find host list with the most entries
  kittenz1_size = len(kittenz1)
  kittenz2_size = len(kittenz2)
  kittenz3_size = len(kittenz3)
  kittenz4_size = len(kittenz4)
  kittenz5_size = len(kittenz5)
  kittenz6_size = len(kittenz6)
  kittenz7_size = len(kittenz7)
  
  list_lens = [kittenz1_size, kittenz2_size, kittenz3_size, kittenz4_size, kittenz5_size, kittenz6_size, kittenz7_size]
  max_len = max(list_lens)
  #extend lists so they all have the same len()
  kittenz1.extend('' for _ in xrange(max_len - kittenz1_size))
  kittenz2.extend('' for _ in xrange(max_len - kittenz2_size))
  kittenz3.extend('' for _ in xrange(max_len - kittenz3_size))
  kittenz4.extend('' for _ in xrange(max_len - kittenz4_size))
  kittenz5.extend('' for _ in xrange(max_len - kittenz5_size))
  kittenz6.extend('' for _ in xrange(max_len - kittenz6_size))
  kittenz7.extend('' for _ in xrange(max_len - kittenz7_size))

  free_table.add_column("KITTENZ-N00BS",kittenz1)
  free_table.add_column("KITTENZ-N00BS",kittenz2)
  free_table.add_column("KITTENZ-N00BS",kittenz3)
  free_table.add_column("KITTENZ-N00BS",kittenz4)
  free_table.add_column("KITTENZ-N00BS",kittenz5)
  free_table.add_column("KITTENZ-N00BS",kittenz6)
  free_table.add_column("KITTENZ-N00BS",kittenz7)
  free_table.align = "l"
  sendmsg_table(free_table, target)
  return free_table


def display_help(target=channel):
  #display_version(target)
  help_table = PrettyTable()
  help_table.field_names = ["COMMAND","","DESCRIPTION"]
  help_table.add_row(["?help","?h", "Access this help menu."])
  help_table.add_row(["?about","?a", "Shows info about this bot. ?version."])
  help_table.add_row(["?news","?n", "Displays catacombs announcements."])
  help_table.add_row(["?who [column]","?w","Show registered hosts sorted by [column]."])
  help_table.add_row(["?free","?f","Show available IP's on N00bs, Jumpstart, and Projects."])
  help_table.add_row(["?free fast","?ff", "Show available IP's from previous ?free."])
  help_table.add_row(["?free kittenz", "?fk", "Show available IP's on all vlans including kittenz-N00bs."])
  help_table.add_row(["?free kittenz fast", "?fkf", "Show available IP's from previous ?fk."])
  help_table.add_row(["?projects", "?p", "Get project ideas."])
  help_table.add_row(["?backups", "?bu", "Show last switch backups."])
  help_table.add_row(["?chronicle", "?ch", "URL to chronicle page."])
  help_table.add_row(["?kill", "?k", "Kills bot if admin."])
  help_table.align = "l"
  sendmsg_table(help_table,target)

def sendmsg_table(table, target=channel, sort=""):
  if(sort==""):
    table_str = table.get_string() #get string of table
  else:
    table_str = table.get_string(sortby=sort) #get string of table
  table_lines = table_str.split('\n') #put each line of table into list
  for line in table_lines: #send msg to irc line by line
    print line
    sendmsg(line, target)

#def save_table(table, filename):
  #if(filename == ""):
    #return
  #file_obj = open(filename, "w")
  
def display_chronicle(target=channel):
  sendmsg(catacombs_url,target) 
  sendmsg(tiered_url,target) 

def display_projects(target=channel):
  projects_table = PrettyTable()
  projects_table.field_names=["PROJECT","LVL","DESCRIPTION"]
  projects_table.add_row(["Setup a box", "1", "install an OS, get a terminal on screen, setup networking"])
  projects_table.add_row(["SSH", "1", "SSH into your box from tier 1, make ssh config, setup ssh keys"])
  projects_table.add_row(["Zombie Tiered Progression", "1-3", "https://chronicle.cat.pdx.edu/projects/braindump/wiki/Zombie_Tiered_Progression"])
  projects_table.add_row(["TFTP", "1-3", "setup a tftp server"])
  projects_table.add_row(["PXE", "2-3", "setup a PXE server"])
  projects_table.add_row(["LDAP", "2-5", "learn you some LDAP"])
  projects_table.add_row(["IRC BOT", "2-5", "make a bot! get creative!"])
  projects_table.add_row(["SWITCH STUFF", "2-5", "ask combsmaster(s) if interested in switch networking"])
  projects_table.add_row(["DNS", "2-4", "setup a DNS server (ask first)"])
  projects_table.add_row(["DHCP", "2-4", "setup a DHCP server (ask first)"])
  projects_table.add_row(["gentoo challenge", "4+", "install gentoo"])
  projects_table.add_row(["RAID", "2", "set RAID up on two OS hard drives"])
  projects_table.add_row(["VM host", "4", "create a VM server to create and host VM's on"])
  projects_table.align = "l"
  sendmsg_table(projects_table, target)

def main():
  free_table_fast = PrettyTable()
  free_table_fast_kittenz = PrettyTable()
  table_dt = datetime.datetime(2017,1,1)
  table_dt_kittenz = datetime.datetime(2017,1,1)
  joinchan(channel)
  #Start infinite loop to continually check for and receive new info from server. This ensures our connection stays open. 
  #We don’t want to call main() again because, aside from trying to rejoin the channel continuously, you run into problems
  #when recursively calling a function too many times in a row. An infinite while loop works better in this case.
  while 1:
    #Receive information from the IRC server. IRC will send out information encoded in
    #UTF-8 characters so we’re telling our socket connection to receive up to 2048 bytes and decode it as UTF-8 characters. 
    #We then assign it to the ircmsg variable for processing.
    ircmsg = ircsock.recv(2048).decode("UTF-8")

    #This part will remove any line break characters from the string. If someone types in "\n” to the channel, it will
    #still include it in the message just fine. 
    #This only strips out the special characters that can be included and cause problems with processing.
    ircmsg = ircmsg.strip('\n\r')

    #Print the received information to your terminal.
    print(ircmsg)

    #Here we check if the information we received was a PRIVMSG. PRIVMSG is how standard messages
    #in the channel (and direct messages to the bot) will come in. 
    #Most of the processing of messages will be in this section.
    if ircmsg.find("PRIVMSG") != -1:
      #First we want to get the nick of the person who sent the message. Messages come in from from IRC in the format of 
      #":[Nick]!~[hostname]@[IP Address] PRIVMSG [channel] :[message]”
      #We need to split and parse it to analyze each part individually.
      #print "ircmsg: " + ircmsg
      name = ircmsg.split('!',1)[0][1:]
      #Above we split out the name, here we split out the message.
      message = ircmsg.split('PRIVMSG',1)[1].split(':',1)[1]
      channel_msg = ircmsg.split(' ')[2]
      #print "channel_msg: " + channel_msg
      #Now that we have the name information, we check if the name is less than 17 characters.
      if len(name) < 17:
        #print "message: " + message
	if channel_msg.lower() != channel.lower():
            target = name
	else:
	    target = channel
        if message.find('hi ' + botnick) != -1 or message.find('Hi ' + botnick) != -1:
            sendmsg("hi " + name + ".", target)
	if message[0] == '?':
            command = message[1:].lower()
            if (command == 'help') or (command == 'h'):
		if target != name:
		  sendmsg(name + ": help sent as privmsg.", target)
		display_help(name)
            elif (command.find('who ip') != -1) or (command.find('who i') != -1) or (command == 'w'):
                display_hosts("IP",target)
            elif (command.find('who h') != -1) or (command == "w h"):
                display_hosts("HOSTNAME", target)
            elif (command.find('who f') != -1) or (command == "w f"):
                display_hosts("FQDN", target)
            elif (command.find('who o') != -1) or (command == "w o"):
                display_hosts("OWNER",target)
            elif (command.find('who p') != -1) or (command == "w p"):
                display_hosts("PING",target)
            elif (command == "who") or (command == "who is alive") or (command == "w"):
                display_hosts("IP",target)
	    elif (command.find("backup") != -1) or (command == "bu"):
		display_backups(target)
	    elif (command.find("version") != -1) or (command == "v"):
  		display_version(target)
	    elif (command.find("chron") != -1) or (command == "ch"):
		display_chronicle(target)
	    elif (command.find("about") != -1) or (command == "a"):
		display_about(target)
	    elif (command.find("proj") != -1) or (command == "p"):
		if target != name:
		  sendmsg(name + ": projects sent as privmsg.", target)
		display_projects(name)
	    elif (command.find("news") != -1) or (command == "n"):
		display_news(target)
	    elif (command == "free fast") or (command == "ff"):
		if target != name:
		  sendmsg(name + ": ?" + command + " sent as privmsg.", target)
                sendmsg("Displaying last ?free from " + table_dt.strftime("%A, %B %d %Y %I:%M%p"), name)	
		sendmsg_table(free_table_fast, name)
            elif (command == "free kittenz fast") or (command == "fkf"):
		if target != name:
		  sendmsg(name + ": ?" + command + " sent as privmsg.", target)
                sendmsg("Displaying last ?free kittenz from " + table_dt_kittenz.strftime("%A, %B %d %Y %I:%M%p"), name)	
		sendmsg_table(free_table_fast_kittenz, name)
	    elif (command == "free") or (command == "f"):
		if target != name:
		  sendmsg(name + ": ?free sent as privmsg.", target)
		tmp_table = display_free(False, name)
		free_table_fast = tmp_table.copy()
	        table_dt = table_dt.now()	
            elif (command.find("free k") != -1) or (command == "fk"):
		if target != name:
		  sendmsg(name + ": ?" + command + " sent as privmsg.", target)
		tmp_table = display_free_kittenz(name)
		free_table_fast_kittenz = tmp_table.copy()
	        table_dt_kittenz = table_dt_kittenz.now()	
            elif (name.lower() == adminname.lower()) and ((command == exitcode) or (command == exitcode[0])):
              #If we do get sent the exit code, then send a message (no target defined, so to the channel) saying we’ll do it, but making clear we’re sad to leave.
              sendmsg("[E.T. and Elliot embrace each other, then E.T. puts his glowing finger to Elliot's forehead] I'll... be... right... here.", target)
              #Send the quit command to the IRC server so it knows we’re disconnecting.
              ircsock.send(bytes("QUIT \n", "UTF-8"))
              #The return command returns to when the function was called (we haven’t gotten there yet, see below) and continues with the rest of the script. 
              #In our case, there is not any more code to run through so it just ends.
              return
            elif (name.lower() != adminname.lower()) and ((command == exitcode) or (command == exitcode[0])):
	      sendmsg("You don't have permission to kill this bot. Nice try " + name + "...", target)
	    else:
		sendmsg(name + ": Sorry, I don't know that command.", target)
    else:
      #Check if the information we received was a PING request. If so, we call the ping() function we defined earlier so we respond with a PONG.
      if ircmsg.find("PING :") != -1:
        ping()
#Finally, now that the main function is defined, we need some code to get it started.
main()
 
