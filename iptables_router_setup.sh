iptables -I PREROUTING -t nat -p udp -s 192.168.1.226 -d 8.8.8.8 --dport 53 -j DNAT --to-destination 208.122.23.22
iptables -I PREROUTING -t nat -p udp -s 192.168.1.226 -d 8.8.4.4 --dport 53 -j DNAT --to-destination 208.122.23.23
