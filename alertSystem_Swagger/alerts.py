import requests
import json
from flask import Flask, jsonify
import sys
global_services=[]
def nodestatus_get():
    req = requests.get("http://"+str(sys.argv[1])+":4243/nodes")
    res=req.json()
    length=len(res)
    hostsArray=[dict() for x in range(length)]
    hosts={}
    flag=1
    counter=0
    for i in range(0,length):
            if res[i]["Status"]["State"] == "ready":
                    hosts["channel"]=res[i]["Description"]["Hostname"]
                    hosts["value"]="0"
                    hosts["limitmode"]="1"
                    hosts["limitmaxerror"]="0"
                    hosts["limitmaxwarning"]="0"
                    hosts["limitminerror"]="0"
                    hosts["limitminwarning"]="0"
                    hostsArray[i]=hosts
                    hosts={}
            else:
                hosts["channel"]=res[i]["Description"]["Hostname"]
                hosts["value"]="1"
                hosts["limitmode"]="1"
                hosts["limitmaxerror"]="0"
                hosts["limitmaxwarning"]="0"
                hosts["limitminerror"]="0"
                hosts["limitminwarning"]="0"
                hostsArray[i]=hosts
                hosts={}
                flag=0
                counter=counter+1

    if flag == 1:
        return jsonify({'prtg':{"result":hostsArray,"text": "All Nodes are up"}})
    else:
        if counter > 1:
            return jsonify({'prtg':{"result":hostsArray,"text": "{} Nodes are down".format(counter)}})
        else:
            return jsonify({'prtg':{"result":hostsArray,"text": "{} Node is down".format(counter)}})

def servicestatus_get():
    services_req = requests.get("http://"+str(sys.argv[1])+":4243/services")
    services_res=services_req.json()
    services_length=len(services_res)


    tasks_req = requests.get("http://"+str(sys.argv[1])+":4243/tasks")
    tasks_res=tasks_req.json()
    tasks_length=len(tasks_res)

    servicesArray=[dict() for x in range(services_length)]
    services={}
    service_counter=0
    flag=1
    counter=0
    servicesList=[]
    global global_services
    global_services=[]
    for i in range(0,services_length):
        service_counter=0
        for j in range(0,tasks_length):
            if services_res[i]["ID"] == tasks_res[j]["ServiceID"] and tasks_res[j]["Status"]["State"] == "running":
                service_counter=service_counter+1
        temp=services_res[i].get('Spec', {}).get('Mode', {}).get('Replicated')
        if  temp is not None and services_res[i]["Spec"]["Mode"]["Replicated"]["Replicas"] == service_counter:
            services["channel"]=services_res[i]["Spec"]["Name"]
            services["value"]="0"
            services["limitmode"]="1"
            services["limitmaxerror"]="0"
            services["limitmaxwarning"]="0"
            services["limitminerror"]="0"
            services["limitminwarning"]="0"
            servicesArray[i]=services
            services={}
        elif temp is not None:
            services["channel"]=services_res[i]["Spec"]["Name"]
            services["value"]="1"
            services["limitmode"]="1"
            services["limitmaxerror"]="0"
            services["limitmaxwarning"]="0"
            services["limitminerror"]="0"
            services["limitminwarning"]="0"
            global_services.append(services_res[i]["ID"])
            servicesArray[i]=services
            services={}
            flag=0
            counter=counter+1
    for k in range(0,services_length):
        if servicesArray[k]:
            servicesList.append(servicesArray[k])
    if flag == 1:
        return jsonify({'prtg':{"result":servicesList,"text": "All Services are up"}})
    else:
        if counter > 1:
            return jsonify({'prtg':{"result":servicesList,"text": "{} services are down".format(counter)}})
        else:
            return jsonify({'prtg':{"result":servicesList,"text": "{} service is down".format(counter)}})


def containerstatus_get():
    servicestatus_get()

    tasks_req = requests.get("http://"+str(sys.argv[1])+":4243/tasks")
    tasks_res=tasks_req.json()
    tasks_length=len(tasks_res)
    global_services_length=len(global_services)


    services_req = requests.get("http://"+str(sys.argv[1])+":4243/services")
    services_res=services_req.json()
    services_length=len(services_res)
    
    containersArray=[dict() for x in range(tasks_length)]
    containers={}
    container_counter=0
    flag=1
    counter=0
    runningCount=0
    containersList=[]
    for i in range(0,tasks_length):
        for l in range(0,services_length):
            temp=services_res[l].get('Spec', {}).get('Mode', {}).get('Replicated')
            temp_con=tasks_res[i].get('Status', {}).get('ContainerStatus', {}).get('ExitCode') 
            if temp is not None and tasks_res[i]["Status"]["State"] == "running" and services_res[l]["ID"] == tasks_res[i]["ServiceID"]:
                containers["channel"]=services_res[l]["Spec"]["Name"]+"."+str(tasks_res[i]["Slot"])
                containers["value"]="0"
                containers["limitmode"]="1"
                containers["limitmaxerror"]="0"
                containers["limitmaxwarning"]="0"
                containers["limitminerror"]="0"
                containers["limitminwarning"]="0"
                containersArray[i]=containers
                containers={}
                runningCount=runningCount+1
            else:
                for j in range(0,global_services_length):
                    if temp is not None and temp_con is not None and tasks_res[i]["Status"]["State"] != "running" and tasks_res[i]["Status"]["ContainerStatus"]["ExitCode"] != 137 and tasks_res[i]["ServiceID"] == global_services[j] and services_res[l]["ID"] == tasks_res[i]["ServiceID"]:
                        containers["channel"]=services_res[l]["Spec"]["Name"]+"."+str(tasks_res[i]["Slot"])
                        containers["value"]="1"
                        containers["limitmode"]="1"
                        containers["limitmaxerror"]="0"
                        containers["limitmaxwarning"]="0"
                        containers["limitminerror"]="0"
                        containers["limitminwarning"]="0"
                        containersArray[i]=containers
                        containers={}
                        flag=0
                        counter=counter+1
    for k in range(0,tasks_length):
        if containersArray[k]:
            containersList.append(containersArray[k])
    if flag == 1:
        return jsonify({'prtg':{"result":containersList,"text": "All {} container(s) are up and running".format(runningCount)}})
    else:
        if counter > 1:
            return jsonify({'prtg':{"result":containersList,"text": "{} containers are down".format(counter)}})
        else:
            return jsonify({'prtg':{"result":containersList,"text": "{} containers is down".format(counter)}})
