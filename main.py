#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#This Script is for Monitoring Directories on RHEL/Cent/OEL OS 6.x,7.x and Ubuntu 14+ Versions OS that are Older than "n" days and triggers Mail.
#Script Name            : Directory_Monitor.py
#Dated                  : February 2019
#Author                 : M.S. Arun (538880)
#Email                  : msarun003@gmail.com
#Usage                  : Directory_Monitor.py
#Last Update            : February 2019


#****************************************************************** Start of Script ********************************************************************#

import datetime
import os
import sys
import socket
import shutil
import csv
import pandas as pd
import smtplib


#--------------------------------------------------------(Editable Section)--------------------------------------------------------#

AGING_THRESHOLD = 3
#Seperated by Commas(,) for below [inputs]
PATH_TO_MONITOR = ['/var/www/html/yum6', '/var/www/html/yum7']
IGNORE_DIR = ['packages', 'BACKUPS_DO_NOT_DELETE']

TO_RECEPIENT = ['msarun003@gmail.com']
CC_RECEPIENT = ['msarun003@gmail.com']

SMTP_SERVER = "smpt.example.com"

MAIL_SUBJECT = "Directories Monitor Logs"

#----------------------------------------------------------------------------------------------------------------------------------#

current_date = datetime.datetime.today() #Get current date

current_date_frmt = current_date.strftime("%m/%d/%Y--%H:%M:%S")

backup_directory = os.getcwd() + "/Directory_Monitor_Logs"


def backup_directory_remove():
        try:
                if os.path.exists(backup_directory):
                        shutil.rmtree(backup_directory)
        except:
                print("Unable to Remove: " + backup_directory)
                sys.exit(1)


def backup_directory_create():
        try:
                if not os.path.exists(backup_directory):
                        os.mkdir(backup_directory)
        except:
                print("Unable to Create: " + backup_directory)
                sys.exit(1)


def host_name_ip():
        try:
                host_name = socket.gethostname()
                ip_address = socket.gethostbyname(host_name)
                return(host_name, ip_address)
        except:
                print("Unable to fetch Hostname and IP")


def csv_output(csv_input):
        try:
                csvfile = open(backup_directory + '/output.csv', 'a')
                writer = csv.writer(csvfile)
                writer.writerow(csv_input)
                csvfile.close()
        except:
                print("Unable to Open: " + backup_directory + "/output.csv")


def directory_check():
        try:
                for single_path in PATH_TO_MONITOR:
                        dir_path = os.listdir(single_path)
                        input_path = [name for name in dir_path if name not in IGNORE_DIR]
                        for dir in input_path:
                                full_path = (os.path.join(single_path, dir))
                                if os.path.isdir(full_path):
                                        modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(full_path))
                                        duration_days = current_date - modified_date
                                        if duration_days.days > AGING_THRESHOLD:
                                                csv_value = (full_path, (modified_date.strftime("%Y-%m-%d %H:%M")), "Not upto date")
                                                csv_output(csv_value)
        except:
                print("Inputed Directories does not exists: " + str(PATH_TO_MONITOR))
                sys.exit(1)


def send_mail():
        FROM = ", ".join(TO_RECEPIENT[:1])
        TO = ", ".join(TO_RECEPIENT)
        CC = ", ".join(CC_RECEPIENT)
        SUBJECT = str(MAIL_SUBJECT)

        columns = ['Path', 'Last Updated Date / Time', 'Status']
        csv_table = pd.read_csv(backup_directory + '/output.csv', names=columns, index_col=None)

        host_name_ip_result = host_name_ip()

        message = """From: %s
To: %s
CC: %s
Subject: %s
MIME-Version: 1.0
Content-type: text/html

<p>Team,<br><br>Please investigate!!!<br><br>The below directories are not updated to current timestamp.<br><br></p>
<p>Aging Threshold: <b>%s</b> days</p>

Hostname: %s<br><br>
IP Address: %s<br>
<style>table {text-align: left;}
table thead th {text-align: center;}
</style><br>%s<br><br>
""" % (FROM, TO, CC, SUBJECT, str(AGING_THRESHOLD), host_name_ip_result[0], host_name_ip_result[1], csv_table.to_html())
        try:
                server = smtplib.SMTP(SMTP_SERVER, port=25)
                server.sendmail(FROM, TO, message)
                server.quit()
        except:
                print("Error: unable to send email")


if __name__== "__main__":
        backup_directory_remove()
        backup_directory_create()
        directory_check()
        if os.path.exists(backup_directory + '/output.csv'):
                send_mail()
        else:
                print("No Files Older than " + str(AGING_THRESHOLD) + " days")
        backup_directory_remove()


#****************************************************************** End of Script **********************************************************************#
