#!/usr/bin/env python
import sys, urllib2
import boto.route53

DEBUG = False
def debug(s):
  if DEBUG:
    print s

AWS_ACCESS_KEY_ID = 'ket_id'
AWS_SECRET_ACCESS_KEY = 'secret_access_key'
AWS_DEFAULT_REGION = 'eu-west-1'


def changerecord(connection, zoneid, zone, operation, hostname, ip):
	change = boto.route53.record.ResourceRecordSets(connection, zoneid)
	record = change.add_change(operation, "{0}.{1}".format(hostname, zone), "A")
	record.add_value(ip)
	change.commit()

def help():
	print("Usage: {0} --zone example.com --action add|rem --hostname hostname(not fqdn) [--ipaddr 192.168.3.33] ".format(sys.argv[0]))
	print("If you do not provide -ipaddr when adding the record, it will get it from aws metadata ")
	exit(1)

if len(sys.argv) < 1:
	print("please provide argv")
	help()
	exit(1)

def parseArgum(param):
	parparam = None
	for i in range(0,len(sys.argv)-1):
        	if sys.argv[i] == '--{0}'.format(param):
                     parparam = sys.argv[i+1]
		     return parparam
                     	
	if not parparam:
		help()
		exit(1)

def FindRecord(connection, hostname, zone_dict, zone):
	zone_f = boto.route53.zone.Zone(connection, zone_dict)
	findRec = zone_f.find_records("{0}.{1}".format(hostname, zone), 'A')
        debug(findRec)
	if findRec != None:
               print("Record exist {0} {1}".format("{0}.{1}".format(hostname, zone), str(findRec).split(":")[3]))
               print("Deleting it ... ")
	       return zone_f.delete_record(findRec, 'delete {0}'.format(hostname))
	return findRec

def GetPublicIp():
    url = urllib2.urlopen('http://169.254.169.254/latest/meta-data/public-ipv4')
    content = url.read
    url.close()
    return content

def main ():
    zone = parseArgum('zone')
    debug(zone)
    hostname = parseArgum('hostname')
    debug(hostname)
    oper = parseArgum('action')
    debug(oper)
    if oper != 'del':
        ipa = False
        for i in range(0,len(sys.argv)-1):
            if sys.argv[i] == "--ipaddr":
                ipa = True
	debug("Find {0}".format(ipa))
        if ipa:
	    ipaddr = parseArgum('ipaddr')
        else: 
            ipaddr = GetPublicIp()
    debug("IP address {0}".format(ipaddr))	
    conn = boto.connect_route53(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    allzones = conn.get_all_hosted_zones()
    debug(allzones)

    Iszone = False
    for i in allzones['ListHostedZonesResponse']['HostedZones']:
	debug(i['Name'])	
	if i['Name'] == "{0}.".format(zone):
		Iszone = True

    if Iszone:
	for i in allzones['ListHostedZonesResponse']['HostedZones']:
	  zoneid = i['Id'].split('/')[-1]
	  zone_dict = i['Id']
	  zone_dict = i
    else:
	print("There is not such zone {0} on Route53. Enter correct zone".format(zone))
	exit(1)

    if oper == "add":
        oper = 'CREATE'
        FindRecord(conn, hostname, zone_dict, zone)
	changerecord(conn, zoneid, zone, oper , hostname, ipaddr)
        print("The record has been added")
    else:
	oper = 'DELETE'
	FindRecord(conn, hostname, zone_dict, zone)
        print("The record has been deleted")

if __name__ == "__main__":
    main()

