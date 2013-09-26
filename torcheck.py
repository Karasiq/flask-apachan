import os
TOR_IP_LIST = list()

def LoadList(listfile):
	with open (listfile, "r") as lf:
		TOR_IP_LIST = lf.read().splitlines()
	return len(TOR_IP_LIST)

def CheckIP(ip):
	return ip in TOR_IP_LIST