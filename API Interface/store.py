import hashlib
import json
import requests
InsurancePurchaseList={}
ClaimRequestList={}
VerificationRequestList={}
ClaimValidationList={}
ClaimSettlementList={}

def writeToBlockchain(key, value):
    jsonDict=json.dumps(value)
    hashValue=hashlib.sha256(jsonDict.encode('utf-8')).hexdigest()
    postBody={
        "emailId":"admin",
        "password":"password",
        "key":key,
        "value":hashValue
    }
    # postBody=json.dumps(postBody)
    requests.post(url="http://localhost:8000/save", json=postBody, headers={"Content-Type":"application/json"})