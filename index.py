# -*- coding:utf-8 -*-
from huawei_function_graph.apig_sdk import signer
import requests
import json

# obtain ak/sk
sig = signer.Signer()

# query sms migration task
def smsTask():
    querySmsreq = signer.HttpRequest(
        "GET", 
        "https://sms.ap-southeast-1.myhuaweicloud.com/v3/tasks/eb1c0236-ee61-4058-8090-c51bcf1096ff")
    querySmsreq.headers = {"content-type": "application/json"}
    sig.Sign(querySmsreq)
    querySmsresp = requests.request(
        querySmsreq.method, 
        querySmsreq.scheme + "://" + querySmsreq.host + querySmsreq.uri, 
        headers = querySmsreq.headers, 
        data = querySmsreq.body
    )
    sapiMsg = "SMS Query Task API Response: "
    sapiRescode = str(querySmsresp.status_code)
    sapiResreas = querySmsresp.reason
    sapiRes = sapiMsg + sapiRescode + " " + sapiResreas
    print(sapiRes)

    # decode returned byte object
    byteObject = querySmsresp.content
    dictList = json.loads(byteObject.decode('UTF-8'))
    # show state: {READY, RUNNING, ABORTING, ABORT, SYNC_SUCCESS, MIGRATE_FAIL, MIGRATE_SUCCESS}
    taskStatus = dictList['state']
    print("State --> " + taskStatus)

    return(taskStatus)

# resume sms migration task
def resumeTask():
    resumeSmsreq = signer.HttpRequest("POST", "https://sms.ap-southeast-1.myhuaweicloud.com/v3/tasks/eb1c0236-ee61-4058-8090-c51bcf1096ff/action")
    resumeSmsreq.headers = {"content-type": "application/json"}
    resumeSmsreq.body = "{\"operation\" : \"start\"}"
    sig.Sign(resumeSmsreq)
    resumeSmsresp = requests.request(
        resumeSmsreq.method, 
        resumeSmsreq.scheme + "://" + resumeSmsreq.host + resumeSmsreq.uri, 
        headers = resumeSmsreq.headers, 
        data = resumeSmsreq.body
    )
    rapiMsg = "SMS Resume Task API Response: "
    rapiRescode = str(resumeSmsresp.status_code)
    rapiResreas = resumeSmsresp.reason
    rapiRes = rapiMsg + rapiRescode + " " + rapiResreas
    print(rapiRes)
    return(resumeSmsresp.status_code)

# send notification via email
def smnMsg(msg):
    publishSmnreq = signer.HttpRequest(
        "POST", 
        "https://smn.ap-southeast-3.myhuaweicloud.com/v2/056d9838768026062f7dc00fc2543155/notifications/topics/urn:smn:ap-southeast-3:056d9838768026062f7dc00fc2543155:sdk_test_kar/publish")
    publishSmnreq.headers = {"content-type": "application/json"}

    if msg == 'migrateSuccess':
        publishSmnreq.body = "{\"message\": \"Migration/Synchronization task completed successfully.\"}"
    if msg == 'resumeSuccess':
        publishSmnreq.body = "{\"message\": \"Error occurred and resume migration task successfully. Please check on console to ensure that the migration is resumed automatically.\"}"
    if msg == 'resumeFail':
        publishSmnreq.body = "{\"message\": \"Error occurred and fail to resume migration task. Please manually resume the migration task on SMS console.\"}"

    sig.Sign(publishSmnreq)
    publishSmnresp = requests.request(
        publishSmnreq.method, 
        publishSmnreq.scheme + "://" + publishSmnreq.host + publishSmnreq.uri, 
        headers = publishSmnreq.headers, 
        data = publishSmnreq.body
    )
    napiMsg = "SMN API Response: "
    napiRescode = str(publishSmnresp.status_code)
    napiResreas = publishSmnresp.reason
    napiRes = napiMsg + napiRescode + " " + napiResreas
    print(napiRes)

    if(publishSmnresp.status_code==200):
        print("Note --> Email notification sent.")
    else:
        print("Note --> Fail to send an email notifation.")

def handler (event, context):
    sig.Key = context.getUserData('accessKey')
    sig.Secret = context.getUserData('secretKey')
    taskStatus = smsTask()
    
    # sent notification according to task status
    if taskStatus=='MIGRATE_SUCCESS' or taskStatus=='SYNC_SUCCESS':
        smnMsg(msg='migrateSuccess')
    # resume the migration when error occured
    if taskStatus == 'MIGRATE_FAIL' or taskStatus == 'SYNC_FAIL' or taskStatus == 'ABORTING' or taskStatus == 'ABORT':
        resp = resumeTask()
        if(resp==200):
            smnMsg(msg='resumeSuccess')
        else:
            smnMsg(msg='resumeFail')