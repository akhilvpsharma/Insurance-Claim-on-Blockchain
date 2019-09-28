from flask import Flask
from flask import request
from flask import jsonify
import store
import hashlib
import requests
import json
import datetime

insurancePurchaseId=0
claimRequestId=0
verificationRequestId=0
claimValidationId=0
claimSettlementId=0

app = Flask(__name__)
@app.route('/insurance-purchase', methods = ['GET', 'POST'])
def insurance_purchase():
    if request.method == 'POST':
        global insurancePurchaseId
        insurancePurchaseId=insurancePurchaseId+1
        body=request.get_json()
        key="insurancePurchaseId_"+str(insurancePurchaseId)
        store.InsurancePurchaseList.update(
            { key:
                {
                    "customerName":body["customerName"],
                    "insurerName":body["insurerName"],
                    "productName":body["productName"],
                    "productCost":body["productCost"],
                    "issueDate":body["issueDate"],
                    "endDate":body["endDate"],
                    "premiumAmount":body["premiumAmount"],
                    "coveredCost":body["coveredCost"]
                }
            })
        store.writeToBlockchain(key, store.InsurancePurchaseList[key])        
        return jsonify(store.InsurancePurchaseList)

    if request.method == 'GET':
        return jsonify(store.InsurancePurchaseList)

@app.route('/claim-request', methods = ['GET', 'POST'])
def claim_request():
    if request.method == 'POST':
        global claimRequestId
        claimRequestId=claimRequestId+1
        body=request.get_json()
        key="claimRequestId_"+str(claimRequestId)
        endDateObject = datetime.datetime.strptime(store.InsurancePurchaseList[body["insurancePurchaseId"]]["endDate"], '%d-%m-%Y').date()
        claimDateObject = datetime.datetime.strptime(body["claimDate"], '%d-%m-%Y').date()
        # currentTime = datetime.datetime.now().date()
        if claimDateObject < endDateObject:
            store.ClaimRequestList.update(
                {key:
                    {
                        "insurancePurchaseId":body["insurancePurchaseId"],
                        "customerName":store.InsurancePurchaseList[body["insurancePurchaseId"]]["customerName"],
                        "insurerName":store.InsurancePurchaseList[body["insurancePurchaseId"]]["insurerName"],
                        "endDate":store.InsurancePurchaseList[body["insurancePurchaseId"]]["endDate"],
                        "productName":store.InsurancePurchaseList[body["insurancePurchaseId"]]["productName"],
                        "claimDate":body["claimDate"],
                        "claimDetails":body["claimDetails"]
                    }
                })
            store.writeToBlockchain(key, store.ClaimRequestList[key])                    
        else:
            return jsonify("Insurance Expired")
        

    if request.method == 'GET':
        return jsonify(store.ClaimRequestList)

@app.route('/verification-request', methods = ['GET', 'POST'])
def verification_request():
    if request.method == 'POST':
        global verificationRequestId
        verificationRequestId=verificationRequestId+1
        body=request.get_json()
        key="verificationRequestId_"+str(verificationRequestId)
        inputString=store.ClaimRequestList[body["claimRequestId"]]["claimDate"]+store.ClaimRequestList[body["claimRequestId"]]["claimDetails"]
        hash= hashlib.sha256(inputString.encode('utf-8')).hexdigest()
        store.VerificationRequestList.update(
            {key:
                {
                    "claimRequestId":body["claimRequestId"],
                    "customerName":store.ClaimRequestList[body["claimRequestId"]]["customerName"],
                    "endDate":store.ClaimRequestList[body["claimRequestId"]]["endDate"],
                    "productName":store.ClaimRequestList[body["claimRequestId"]]["productName"],
                    "commodityDetailsHash":hash
                }
            })
        store.writeToBlockchain(key, store.VerificationRequestList[key])
        return jsonify(store.VerificationRequestList)   

    if request.method == 'GET':
        return jsonify(store.VerificationRequestList)

@app.route('/claim-validation', methods = ['GET', 'POST'])
def claim_validation():
    if request.method == 'POST':
        global claimValidationId
        claimValidationId=claimValidationId+1
        body=request.get_json()
        key="claimValidationId_"+str(claimValidationId)
        store.ClaimValidationList.update(
            {key:
                {
                    "verificationRequestId":body["verificationRequestId"],
                    "firNumber":body["firNumber"],
                    "claimStatus":body["claimStatus"],
                    "additionalComments":body["additionalComments"]
                }
            })
        store.writeToBlockchain(key, store.ClaimValidationList[key])
        return jsonify(store.ClaimValidationList)

    if request.method == 'GET':
        return jsonify(store.ClaimValidationList)

@app.route('/claim-settlement', methods = ['GET', 'POST'])
def claim_settlement():
    if request.method == 'POST':
        global claimSettlementId
        claimSettlementId=claimSettlementId+1
        body=request.get_json()
        key="claimSettlementId_"+str(claimSettlementId)
        store.ClaimSettlementList.update(
            {key:
                {
                    "claimValidationId":body["claimValidationId"],
                    "firNumber":store.ClaimValidationList[body["claimValidationId"]]["firNumber"],
                    "settlementResult":body["settlementResult"],
                    "additionalComments":body["additionalComments"]
                }
            })
        store.writeToBlockchain(key, store.ClaimSettlementList[key])
        return jsonify(store.ClaimSettlementList)

    if request.method == 'GET':
        return jsonify(store.ClaimSettlementList)

@app.route('/block-explorer', methods = ['GET'])
def block_explorer():
    if request.method == 'GET':
        resultList={}
        for key in store.InsurancePurchaseList:
            response=requests.get(url = "http://localhost:8000/search/"+key)
            responseJSON=json.loads(response.text)
            resultList.update({key:responseJSON["message"]})

        for key in store.ClaimRequestList:
            response=requests.get(url = "http://localhost:8000/search/"+key)
            responseJSON=json.loads(response.text)
            resultList.update({key:responseJSON["message"]})

        for key in store.VerificationRequestList:
            response=requests.get(url = "http://localhost:8000/search/"+key)
            responseJSON=json.loads(response.text)
            resultList.update({key:responseJSON["message"]})

        for key in store.ClaimValidationList:
            response=requests.get(url = "http://localhost:8000/search/"+key)
            responseJSON=json.loads(response.text)
            resultList.update({key:responseJSON["message"]})
        
        for key in store.ClaimSettlementList:
            response=requests.get(url = "http://localhost:8000/search/"+key)
            responseJSON=json.loads(response.text)
            resultList.update({key:responseJSON["message"]})

    return jsonify(resultList)
    
# if _name == '__main_':
app.run(debug=True, port=5000)
    