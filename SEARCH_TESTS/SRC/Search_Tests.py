#! /usr/bin/python
import requests
import os
import sys
import socket
import xml.etree.ElementTree as X
from colorama import Fore, init
init(autoreset=True)

search_file = 'search_test.xml'
cred_file = 'credentials.txt'
adv_search_file = 'search_advanced.xml'

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

cred_path = os.path.join(application_path, cred_file)
search_path = os.path.join(application_path, search_file)
adv_search_path = os.path.join(application_path, adv_search_file)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("gmail.com", 80))
local_ip = (s.getsockname()[0])
s.close()

os.system('chcp 65001')
os.system('cls')

cred = open(cred_path)
serv_w = str(cred.readlines(1))
serv_w = serv_w[2:-4]
port = str(cred.readlines(2))
port = port[2:-4]
user = str(cred.readlines(3))
user = user[2:-4]
passw = str(cred.readlines(4))
passw = passw[2:-2]
cred.close()

c = input("Connect to " + str(serv_w) + str(port) + " - Change Connection (C) ")
if c.lower() == "c":
    serv_w = input("Server?: ")
    port = input("Port?: ")
    user = input("User?: ")
    passw = input("Pass?: ")
    if port == "":
        port = ":80"
    else:
        port = ':' + port

    cred = open(cred_path, 'w')
    cred.writelines(serv_w + "\n")
    cred.writelines(port + "\n")
    cred.writelines(user + "\n")
    cred.writelines(passw)
    cred.close()

    server = serv_w + port
else:
    server = serv_w + port

loginPayload = {'action': 'login', "data": {"username": user, "password": passw}}
r = requests.post('http://' + server + '/montana/webApi', json=loginPayload)
jsonResponse = r.json()

if jsonResponse['status'] != 'OK':
    print('Cannot login...')
    sys.exit()
else:
    sesId = jsonResponse['sessionId']
    system = jsonResponse['systemMsId']


def advanced_search():
    id_full = '"sessionId":"' + sesId + ':' + user + ':' + local_ip + '"}'
    xml = X.parse(adv_search_path)
    root = xml.getroot()
    info = []
    payload_value = []
    results = []

    for child in root:
        info_value = child.get('name')
        pl_value = child.get('value')
        result_value = child.get('result')
        info.append(info_value)
        payload_value.append(pl_value)
        results.append(result_value)

    print(Fore.LIGHTYELLOW_EX + '\n' + 'ADVANCED SEARCH TESTS:\n')
    iterator = 0
    for x in payload_value:
        advanced_search_payload = x + id_full
        q = requests.post('http://' + server + '/montana/webApi', data=advanced_search_payload)

        if q.status_code != 200:
            print('Error on search')
            input()
        else:
            response = q.json()
            if response['status'] != 'OK':
                print('Cannot search')
                input()
            else:
                if int(response['data']['total']) == int(results[iterator]):
                    print(info[iterator])
                    print('result: ' + str(response['data']['total']) + '\t ' + '--' * 5 + Fore.LIGHTGREEN_EX +
                          ' Pass\n')
                else:
                    print(info[iterator])
                    print("Expected: " + str(results[iterator]) + ', Result: ' +
                          str(response['data']['total']) + '\t ' + '--' * 2 + Fore.LIGHTRED_EX + ' Fail\n')
        iterator += 1
    input()
    command_input()


def test_lucene():
    xml = X.parse(search_path)
    root = xml.getroot()
    key_list = []
    result_list = []
    for child in root:
        key = child.get('key')
        result = child.get('result')
        key_list.append(key)
        result_list.append(result)

    os.system('cls')
    print(Fore.WHITE + "Connected to: " + server + " " + system + "\n")
    print(Fore.LIGHTYELLOW_EX + '\n' + 'KEYWORD SEARCH TESTS:\n')
    result_list_iterator = 0
    for keyword in key_list:
        search_payload = {"action": "searchKeywordLucene", "data": {"maxPerPage": 1000, "getChildFields": 'true',
                                                                    "getMatchedChildren": 'true',
                                                                    "highlightAssetFields": 'true', "keyword": keyword,
                                                                    "returnType": {"type": "asset",
                                                                                   "metadata": ["displayName", "source",
                                                                                                "createDate",
                                                                                                "program_id",
                                                                                                "program_notes"]}},
                          "sessionId": sesId + ":" + user + ":" + local_ip}

        q = requests.post('http://' + server + '/montana/webApi', json=search_payload)
        if q.status_code != 200:
            print("Error on search")
        else:
            json_response = q.json()
            if json_response['status'] != 'OK':
                print('Cannot search...')
            else:
                if int(json_response['data']['total']) == int(result_list[result_list_iterator]):
                    print('key: ' + str(result_list_iterator) + ' -> results: ' + str(json_response['data']['total']) +
                          '\t' + '--' * 5 + Fore.LIGHTGREEN_EX + ' Pass' + '\n')
                else:
                    print('key: ' + str(result_list_iterator) + ' -> results: ' + str(json_response['data']['total']) +
                          '\t' + 'expected: ' + result_list[result_list_iterator] + ' - ' + Fore.LIGHTRED_EX +
                          'Fail' + '\n')
        result_list_iterator += 1
    advanced_search()

    view_key = input("View key: ")
    if view_key == 'm':
        k = input("\nKey to modify: ")
        key_to_modify = str("search[@key='" + str(key_list[int(k)]) + "']")
        f = root.find(key_to_modify)
        new_value = input("New search value: ")
        new_result = input("New result value: ")
        f.set('key', new_value)
        f.set('result', new_result)
        X.ElementTree(root).write(search_path)
        input("\nKey updated...")
        command_input()
    try:
        if key_list[int(view_key)] == '':
            print('\nkey value is: null')
        else:
            print('\nkey value is: ' + key_list[int(view_key)])
        input()
        command_input()
    except ValueError:
        print('\nKey not found..')
        input()
        command_input()
    except IndexError:
        print('\nKey not found..')
        input()
        command_input()


def system_status():
    os.system('cls')
    status_payload = {"action": "getSystemStatus", "sessionId": sesId + ":" + user + ":" + local_ip}
    q = requests.post('http://' + server + '/montana/webApi', json=status_payload)
    if q.status_code != 200:
        print("Error")
    else:
        json_response = q.json()
        print(Fore.WHITE + "Connected to: " + server + " " + system + "\n")
        print("System Status: " + str(json_response['status']) + "\n\n")
        print('Total Assets: ' + str(json_response['data']['processingInfo']['numAssets']))
        print("\n" + 'Total Instances: ' + str(json_response['data']['processingInfo']['numInstances']))
        print(
            "\n" + 'Transcode engine(s): ' + str(json_response['data']['processingInfo']['connectedTranscodeEngines']))
        print("\n" + 'Data Mover(s): ' + str(json_response['data']['processingInfo']['totalDatamovers']))
        print("\n" + 'Attachments: ' + str(json_response['data']['processingInfo']['numAttachments']))

        input()
        command_input()


def keyword_search():
    os.system('cls')
    print(Fore.WHITE + "Connected to: " + server + " " + system + "\n")
    keyword = input(Fore.LIGHTRED_EX + "Keyword? ")
    search_payload = {"action": "searchKeywordLucene", "data": {"maxPerPage": 1000, "getChildFields": 'true',
                                                                "getMatchedChildren": 'true',
                                                                "highlightAssetFields": 'true', "keyword": keyword,
                                                                "returnType": {"type": "asset",
                                                                               "metadata": ["displayName", "source",
                                                                                            "createDate",
                                                                                            "program_id",
                                                                                            "program_notes"]}},
                      "sessionId": sesId + ":" + user + ":" + local_ip}

    q = requests.post('http://' + server + '/montana/webApi', json=search_payload)
    if q.status_code != 200:
        print("Error on search")
    else:
        results = []
        json_response = q.json()
        if json_response['status'] != 'OK':
            print('Cannot search')
        else:
            print('\n' + "Search returned " + str(json_response['data']['total']) + " items:" + " - Time taken: " +
                  str(json_response['timeTaken']) + "\n")
            for item in json_response['data']['asset']:
                results.append(str(item['displayName']))
        global last_search
        global last_result
        last_search = str(keyword)
        last_result = str(json_response['data']['total'])

        if len(results) > 50:
            pages = int(len(results) / 50) + 1
            count = 1
            slicer = 0
            while count <= pages:
                old_slicer = slicer
                slicer = count * 50
                temp_results = results[old_slicer:slicer]
                print('*' * 30)
                for x in temp_results:
                    print(x)
                print("\n")
                print("Page " + str(count) + " of " + str(pages) + "\n")
                next_pg = input("'N' for next page ")
                if next_pg.lower() == "n":
                    count += 1
                    os.system('cls')
                else:
                    break
        else:
            temp_results = results[:50]
            for x in temp_results:
                print(x)

        new_search()


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def new_search():
    search = input(Fore.LIGHTMAGENTA_EX + "\n" + "N - New Search, A - Add last search to xml: ")
    if search.lower() == "n":
        os.system('cls')
        keyword_search()
    elif search.lower() == "a":
        xml = X.parse(search_path)
        root = xml.getroot()
        X.SubElement(root, 'search', key=last_search, result=last_result)
        indent(root)
        X.ElementTree(root).write(search_path)
        print('Last search added to xml...')
        input()
        command_input()
    else:
        os.system('cls')
        command_input()


def logout():
    logout_payload = {"action": "logout", "data": {"sessionId": sesId + ":" + user + ":" + local_ip},
                      "sessionId": sesId + ":" + user + ":" + local_ip}
    requests.post("http://" + server + "/montana/webApi", json=logout_payload)
    os.system('cls')
    print("Disconnected..." + "\n")
    sys.exit()


def metadata_def():
    os.system('cls')
    meta_payload = {"action": "getMetadataDefinition", "sessionId": sesId + ":" + user + ":" + local_ip}
    m = requests.post("http://" + server + "/montana/webApi", json=meta_payload)
    json_m = m.json()
    if json_m['status'] != 'OK':
        print("Error..")
    else:
        print(Fore.WHITE + "Connected to: " + server + " " + system + "\n")
        print(Fore.CYAN + 'Asset Metadata:\n')
        print("{:<25} {:<15} {:<10}".format('ID', 'Type', 'ReadOnly'))
        print('-' * 50)
        for item in json_m['data']['asset_metadata']:
            print("{:<25} {:<15} {:<10}".format(str(item['metadata_id']), str(item['type']),
                                                str(item['readOnly'])))
        print('-' * 50)
        print(Fore.CYAN + '\n\nInstance Metadata:\n')
        print("{:<25} {:<15} {:<10}".format('ID', 'Type', 'ReadOnly'))
        print('-' * 50)
        for item in json_m['data']['instance_metadata']:
            print("{:<25} {:<15} {:<10}".format(str(item['metadata_id']), str(item['type']),
                                                str(item['readOnly'])))
        print('-' * 50)
        input()
    command_input()


def storage_locations():
    os.system('cls')
    sl_payload = {"action": "getLocations", "data": {"metadata_options": {"send_all": "true", "detailed": "true"},
                                                     "query": {}}, "sessionId": sesId + ":" + user + local_ip}
    p = requests.post("http://" + server + "/montana/webApi", json=sl_payload)
    json_sl = p.json()
    if json_sl['status'] != 'OK':
        print("Error..")
    else:
        print(Fore.WHITE + "Connected to: " + server + " " + system + "\n")
        print("{:<20} {:<20} {:<10}".format('Name', 'Type', 'Status'))
        print('-' * 50)
        total_loc = 0
        for item in json_sl['data']['storage_locations']:
            total_loc += 1
            if str(item['metadata'][-1]['value']).lower() == 'online':
                print(
                    "{:<20} {:<20} {:<10}".format(str(item['metadata'][0]['value']), str(item['metadata'][2]['value']),
                                                  Fore.LIGHTGREEN_EX + str(item['metadata'][-1]['value'])))
            else:
                print(
                    "{:<20} {:<20} {:<10}".format(str(item['metadata'][0]['value']), str(item['metadata'][2]['value']),
                                                  Fore.LIGHTRED_EX + str(item['metadata'][-1]['value'])))
        print('-' * 50 + "\n" + "Total: " + str(total_loc))
        input()
    command_input()


def system_messages_report():
    os.system('cls')
    seconds = "86400"  # Intervalul de timp
    print("Messages from 24 hours ago: \n\n")

    messages_payload = dict(action="generateSystemMessagesReport", data={"start_date": 1, "end_date": 1,
                                                                         "module_list": ["ALL", "ASSET MANAGER", "CMC",
                                                                                         "CMI",
                                                                                         "CPC", "EIE", "MEDIA LIBRARY",
                                                                                         "MMC", "MMI",
                                                                                         "RESOURCE MANAGER", "SDBI",
                                                                                         "SSC", "SSI",
                                                                                         "SYSTEM", "UII", "XMMPI",
                                                                                         "HARRIS", "OSM", "TSS", "ACI",
                                                                                         "ALE", "DM MANAGER", "MOSI",
                                                                                         "UNKNOWN", "WORKFLOW MANAGER",
                                                                                         "XMTI", "OCP",
                                                                                         "REPORTS MANAGER",
                                                                                         "INDEX MANAGER"],
                                                                         "message_type_list": ["OPERATOR"],
                                                                         "seconds_interval": seconds,
                                                                         "order_by": "msg_time desc"},
                            sessionId=sesId + ":" + user + local_ip)
    s = requests.post("http://" + server + "/montana/webApi", json=messages_payload)
    json_ms = s.json()
    if json_ms['status'] != 'OK':
        print('Error')
    else:
        for item in json_ms['data']['SystemMessagesReport']:
            print(str(item['message_text']) + "\n\n")
    input()
    command_input()


def command_input():
    os.system('cls')
    print(Fore.WHITE + "Connected to: " + server + " - " + system + "\n")
    command = input("Commands: " + Fore.LIGHTRED_EX + "Search(S), Metadata(M), Locations(L), TESTS(T), "
                                                      "SysStatus(Q), Exit(X): ")
    if command.lower() == "s":
        keyword_search()
    elif command.lower() == "q":
        system_status()
    elif command.lower() == "l":
        storage_locations()
    elif command.lower() == "m":
        metadata_def()
    elif command.lower() == "e":
        system_messages_report()
    elif command.lower() == "x":
        os.system('cls')
        sys.exit()
    elif command.lower() == 't':
        test_lucene()
    else:
        command_input()

command_input()
