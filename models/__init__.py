import re
# Clean IP with range
def clean_IP_with_range(ip):
    return clean_IP(ip).split(',')

def clean_IP(ip):
    return ip.replace(' ', '')
# Regex Match
def regex_match(regex, text):
    pattern = re.compile(regex)
    return pattern.search(text) is not None
# Check IP with range (IPv4 only now)
# TODO: Add IPv6 support
def check_IP_with_range(ip):
    return regex_match("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|\/)){4}(0|1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|" +
                    "18|19|20|21|22|23|24|25|26|27|28|29|30|31|32)(,|$)", ip)

# Check allowed ips list
def check_Allowed_IPs(ip):
    ip = clean_IP_with_range(ip)
    for i in ip:
        if not check_IP_with_range(i): return False
    return True
# Check DNS
def check_DNS(dns):
    dns = dns.replace(' ','').split(',')
    status = True
    for i in dns:
        if not (regex_match("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}", i) or regex_match("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]",i)):
            return False
    return True

# Check remote endpoint (Both IPv4 address and valid hostname)
# TODO: Add IPv6 support
def check_remote_endpoint(address):
    return (regex_match("((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\.|$)){4}", address) or regex_match("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z][a-z]{0,61}[a-z]",address))