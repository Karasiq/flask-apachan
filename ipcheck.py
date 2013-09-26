import netaddr
class IpList():
    ip_list = None
    def Load(self, listfile):
        with open (listfile, "r") as lf:
            lines = lf.read().splitlines()
            self.ip_list = list()
            for l in lines:
                self.ip_list.extend(netaddr.IPNetwork(l))
            lf.close()
    def InList(self, ip):
        return self.ip_list and netaddr.IPAddress(ip) in self.ip_list