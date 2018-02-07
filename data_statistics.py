#!/usr/bin/env python3
from scipy.stats.mstats import normaltest
import matplotlib.pyplot as plt
import numpy
import pandas as pd
import scipy 
import requests
import time

class DataStats:

    urls = {    'port_info'      : '/core/switch/all/port-desc/json',            
                'flow_src_info'  : 'query_range?query=ovs_ip_dst_flows&start={}&end={}&step=1s', 
                'flow_dst_info'  : 'query_range?query=ovs_ip_dst_flows&start={}&end={}&step=1s', 
                'flow_count'     : 'query_range?query=flow_count&start={}&end={}&step=1s',
                'tx_packets'     : 'query_range?query=ovs_transmitted_packets&start={}&end={}&step=1s',
                'rx_packets'     : 'query_range?query=ovs_received_packets&start={}&end={}&step=1s',
                'tx_bytes'       : 'query_range?query=ovs_transmitted_bytes&start={}&end={}&step=1s',
                'rx_bytes'       : 'query_range?query=ovs_received_bytes&start={}&end={}&step=1s',
                'kill_flow'      : 'core/switch/all/port-desc/json',
                'port_stats'     : 'core/switch/all/port/json',
                'pair'           : 'core/switch/all/flow/json'
           }

    def __init__(self, ip, port):
        self.n = 0
        self.filtr = ''
        self.port_lists = {}
        self.port_color = [] # Consider all ports are green in the beginning
        self.port_cntrs = {}
        self.cntrs_len = 10
        self.avg_duration = 0
        self.prediction_mtrx1 = []
        self.prediction_mtrx2 = []

        self.ip = ip
        self.port = port
        self.floodlight_urls = 'http://' + self.ip + ':' + self.port + '/wm/'
        self.prometheus_urls = 'http://' + '172.1.0.3' + ':' + '9090' + '/api/v1/'
        self.init_ports()

    def post_request(self, request):
        post_data = {   "switch" : "00:00:00:00:00:00:00:01",
                        "name" : "kill_the_port_1",
                        "cookie" : "0",
                        "priority" : "1",
                        "in_port" : "1",
                        "actions" : "drop"
                    }
        
        url = self.floodlight_urls + self.urls[request]
        request.post(url, data = post_data)

    def make_request(self, request):
        if request not in self.urls:
            return 

        end = time.time()
        start = time.time() - 60

        if request == 'pair':
            url = self.floodlight_urls + self.urls[request]

        if request == 'port_info':
            url = self.floodlight_urls + self.urls[request]

        if request == 'flow_src_info':
            url = self.prometheus_urls + self.urls['flow_src_info'].format(start, end)

        if request == 'flow_dst_info':
            url = self.prometheus_urls + self.urls['flow_dst_info'].format(start, end)

        if request == 'flow_count':
            url = self.prometheus_urls + self.urls[request].format(start, end)

        if request == 'tx_packets' or request == 'tx_bytes':
            url = self.prometheus_urls + self.urls[request].format(start, end)

        if request == 'rx_packets' or request == 'rx_bytes':
            url = self.prometheus_urls + self.urls[request].format(start, end)

        if request == 'port_stats':
            url = self.floodlight_urls + self.urls[request]

        with requests.get(url) as f:
            return f.json()

    def init_ports(self):
        ports = self.make_request('port_info')

        for item, values in ports.items():
            self.port_lists.setdefault(item, [])
            for port_number in values['port_desc']:
                if port_number['port_number'] == 'local':
                    continue
                self.port_lists[item].append(port_number['port_number'])

        print(self.port_lists)

    def get_port_data_db(self, request):
        port_data = self.make_request(request)

        list_values = {}
        for item in port_data['data']['result']:
            val = []
            # list_values[item['metric']['name'] + item['metric']['nodeid'][-3:]] = item['values']
            for i in item['values']:
                val.append(int(i[1]))

            list_values[item['metric']['name'] + item['metric']['nodeid'][-3:]] = val
            # print(item['metric']['name'], item['metric']['nodeid'][-3:])
            # for lst in item['values']:
                # print(lst)

        return list_values

    def get_port_data(self):
        port_data = self.make_request('port_stats')
        self.n += 1
        if not port_data:
            return -1

        list_values = {}

        for item, values in port_data.items():
            for port in values['port_reply'][0]['port']:
                if port['port_number'] == 'local':
                    continue
                list_values[port['port_number'] + item[-3:]] = [ int(port['receive_packets']) , int(port['receive_bytes'])  , int(port['receive_packets']) ,  int(port['receive_bytes'])]

        # print(list_values)
 
        return list_values

    def analyze_packet_data(self, tx_pkts, tx_bts):

        # print('Correlation')
        # print('P  1', scipy.stats.pearsonr(tx_pkts['1'],  tx_bts['1'])) 
        # print('P 11', scipy.stats.pearsonr(tx_pkts['11'], tx_bts['11'])) 
        # print('P 21', scipy.stats.pearsonr(tx_pkts['21'], tx_bts['21'])) 

        # print(tx_bts.describe())

        # print(tx_bts['12:02'].describe())

        tx_bts['12:02'].plot()
        plt.show()
        print('=================================')

    def get_flow_counts(self):
        flow_count = self.make_request('pair')
        
        for item, values in flow_count.items():
            print(values['in_port'])

    def add_to_counters(self, data):
        key = ''
        values = []
        for cnt in data:
            key = list(cnt.keys())[0]

            if key not in self.port_cntrs:
                self.port_cntrs[key] = []
            else:
                if len(self.port_cntrs[key]) < self.cntrs_len:
                    self.port_cntrs[key].append(list(cnt.values())[0])
                else:
                    self.port_cntrs[key].pop(0)
                    self.port_cntrs[key].append(list(cnt.values())[0])

        # print(self.port_cntrs)

    def exp_smooting(self, ports, weight, prev_i):
        if prev_i == []:
            return ports[3]
        
        ret = []
        values = ports[3]

        for i in range(0, len(ports[3])):
            ret.append(values[i]*weight + (1-weight)*prev_i[i])

        return ret

    def pred_matrix(self, curr_values):
       #define pred_matrix for next values
        weight_a = .2
        weight_b = .8
        ports = curr_values.as_matrix()
        
        try:
            self.prediction_mtrx1 = self.exp_smooting(ports, weight_a, self.prediction_mtrx1)
            self.prediction_mtrx2 = self.exp_smooting(ports, weight_b, self.prediction_mtrx2)
        except IndexError:
            pass

    def stats_analysis(self, data, now):
        print(data.columns)
        value = data.as_matrix()

        val1 = 0
        val2 = 0

        init = True
        if time.time() - now > 30.0:
            print("init", init)
            init = False

        total_val_log1 = []
        total_val_log2 = []

        total_val_div1 = []
        total_val_div2 = []

        for i in range(0, len(value[3])):
            self.prediction_mtrx1.append(value[3][i])
            self.prediction_mtrx2.append(value[3][i])

        err = []

        for i in range(0, len(value[3])):
            # print(numpy.log(value[3][i]/self.prediction_mtrx[i]))
            val1 = value[3][i]/self.prediction_mtrx1[i]
            val2 = value[3][i]/self.prediction_mtrx2[i]

            total_val_log1.append(numpy.exp(val1))
            total_val_log2.append(numpy.exp(val2))

            total_val_div1.append(numpy.square(val1))
            total_val_div2.append(numpy.square(val1))

        self.pred_matrix(data)
        print("err:", err)

        return total_val_div1, total_val_div2
        # return total_val_log1, total_val_log2

    def cycle(self, now):
        tx_packets = []
        tx_bytes = []
        #tx_packets = self.get_port_data_db('tx_packets')
        #tx_bytes = self.get_port_data_db('tx_bytes')

        instant_port_stats = self.get_port_data()
        if instant_port_stats == -1:
            return 0, 0
        instant_ps_df = pd.DataFrame(instant_port_stats)
        bytes_df = pd.DataFrame(tx_bytes)

        values_log, values_div = self.stats_analysis(instant_ps_df, now)
        print(values_log)
        print(values_div)

        return values_log, values_div

    def graph(self, portno):
        data1 = ''
        data2 = ''

if __name__ == "__main__":
    stats = DataStats('172.1.0.2', '8080')
    now = time.time()
    total_val_div = []
    total_val_log = []

    while time.time() - now <= 60*15:
        val_log, val_div = stats.cycle(now)

        if val_log == 0 or val_div == 0:
            break

        total_val_div.append(val_log)
        total_val_log.append(val_div)
        time.sleep(2)

    # port = '12:02'
    # size0 = pd.read_csv('results/size0', nrows=20)
    # size140 = pd.read_csv('results/size140', nrows=20)
    # size240 = pd.read_csv('results/size240', nrows=20)
    # size340 = pd.read_csv('results/size340', nrows=20)
    # size440 = pd.read_csv('results/size440', nrows=20)
    # size540 = pd.read_csv('results/size540', nrows=20)

    # size0[port].plot(label='0')
    # size140[port].plot(label='140')
    # size240[port].plot(label='240')
    # size340[port].plot(label='340')
    # size440[port].plot(label='440')
    # size540[port].plot(label='540')

    print(total_val_log[1:])
    dete_res = pd.DataFrame(total_val_log[15:])
    dete_res2 = pd.DataFrame(total_val_div[15:])
 
    print(dete_res.filter(items = [0, 1, 2, 3]))

    fig, axes = plt.subplots(nrows=2, ncols=1)
    ax = dete_res.filter(items = [0, 1, 2]).plot(ax=axes[0]) # square
    dete_res2.filter(items = [0, 1, 2]).plot(ax=axes[1]) # exp
    plt.show()

    with open('results/detection', 'w+') as f:
        f.writelines(dete_res.to_csv())
    # plt.legend()
