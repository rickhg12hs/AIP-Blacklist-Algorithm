from data_processing_functions import *
from whitelist_module import *

def update_records_files(path_to_historical_data, list_of_known_new_IP_data, unknown_IP_flows, current_time,
                         current_directory, AIPP_direcory, FP_log_file):
    absolute_data, IPs_in_abs_file = open_sort_abs_file(path_to_historical_data)
    new_absolute_file_flows = []
    new_absolute_file_flows += absolute_data
    unknown_IP_flows_new = []
    for new_flow2 in unknown_IP_flows:
        new_flow2.extend([new_flow2[1]])
        unknown_IP_flows_new.append(new_flow2)
    new_absolute_file_flows.extend(unknown_IP_flows_new)
    if not list_of_known_new_IP_data:
        pass
    else:
        for x1, new_flow in enumerate(list_of_known_new_IP_data):
            for x2, absolute_flow in enumerate(new_absolute_file_flows):
                if absolute_flow[0] == new_flow[0]:
                    days_since_first_seen = (current_time - float(absolute_flow[9])) // 86400.0
                    if days_since_first_seen != 0:
                        updated_event_average = ((float(absolute_flow[10])) * (days_since_first_seen - 1) + float(
                            new_flow[1])) / days_since_first_seen
                    else:
                        updated_event_average = ((float(absolute_flow[10])) * (days_since_first_seen - 1) + float(
                            new_flow[1])) / 1

                    updated_total_events = float(new_flow[1]) + float(absolute_flow[1])
                    updated_total_duration = float(absolute_flow[2]) + float(new_flow[2])
                    updated_average_duration = (float(absolute_flow[3]) + float(new_flow[3])) / 2.0
                    updated_total_bytes = float(absolute_flow[4]) + float(new_flow[4])
                    updated_average_bytes = (float(absolute_flow[5]) + float(new_flow[5])) / 2.0
                    updated_total_packets = float(absolute_flow[6]) + float(new_flow[6])
                    updated_average_packets = (float(absolute_flow[7]) + float(new_flow[7])) / 2.0
                    updated_last_event = new_flow[9]

                    updated_entry = [new_flow[0], updated_total_events, updated_total_duration,
                                     updated_average_duration,
                                     updated_total_bytes, updated_average_bytes, updated_total_packets,
                                     updated_average_packets,
                                     absolute_flow[8], updated_last_event, updated_event_average]
                    new_absolute_file_flows[x2] = updated_entry
                    break
                else:
                    continue
    with open(current_directory + '/Main/ASN/strings_to_check.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        list_of_good_organiations = list(csv_reader)
    asn_info = get_ASN_data(current_directory + '/Main/ASN/GeoLite2-ASN.mmdb', new_absolute_file_flows)
    whitelisted_nets, whitelisted_ips = load_whitelist()
    list_of_FPs = []
    for index, flow in enumerate(new_absolute_file_flows):
        judgement1 = check_if_ip_is_in_whitelisted_nets(flow[0], whitelisted_nets)
        judgement2 = check_if_ip_is_in_whitelisted_ips(flow[0], whitelisted_ips)
        judgement3, entry = check_organization_strings(asn_info[flow[0]], list_of_good_organiations)
        if judgement1 == True:
            list_of_FPs.append(flow)
            del new_absolute_file_flows[index]
            with open(AIPP_direcory + "/log.txt", "a") as myfile:
                myfile.write('Found ' + str(flow[0]) + ' in Whitelisted Nets. Deleting entry...' + "\n")
        elif judgement2 == True:
            list_of_FPs.append(flow)
            del new_absolute_file_flows[index]
            with open(AIPP_direcory + "/log.txt", "a") as myfile:
                myfile.write('Found ' + str(flow[0]) + ' in Whitelisted IPs. Deleting entry...' + "\n")
        elif judgement3 == True:
            list_of_FPs.append(flow)
            del new_absolute_file_flows[index]
            with open(AIPP_direcory + "/log.txt", "a") as myfile:
                myfile.write('Found ' + str(flow[0]) + ' ASN matches organization ' + str(entry) + ' Deleting entry...' + "\n")
        else:
            continue
    with open(FP_log_file, 'a') as FP_file:
        csvwriter = csv.writer(FP_file)
        csvwriter.writerows(list_of_FPs)
    with open(path_to_historical_data, 'w') as new_file_another:
            wr2 = csv.writer(new_file_another, quoting=csv.QUOTE_ALL)
            for y in new_absolute_file_flows:
                wr2.writerow(y)