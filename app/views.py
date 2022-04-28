from django.shortcuts import render,redirect
from django.http import FileResponse

import os,requests,json,csv,pandas as pd,datetime

from datetime import datetime

from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings

from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

MEDIA_ROOT = settings.MEDIA_ROOT
today = datetime.today().strftime('%Y%m%d')
x = date.today() + relativedelta(months=-18)
eighteen_months = x.strftime('%Y%m%d')


def save_csv(data):
    count = 0
    for d in data :
        try:
            application_number = d['openfda']['application_number']
        
        except:
            application_number = "-"
        
        try:
            generic_name = d['openfda']['generic_name']
        
        except:
            generic_name = "-"

        try:
            brand_name = d['openfda']['brand_name']
        
        except:
            brand_name = "-"
        
        try:
            product_ndc = d['openfda']['product_ndc']
        
        except:
            product_ndc = "-"

        try:
            indications_and_usage = d['indications_and_usage']
        
        except:
            indications_and_usage = "-"

        try:
            clinical_studies = d['clinical_studies']
        
        except:
            clinical_studies = "-"

        try:
            pediatric_use = d['pediatric_use']
        
        except:
            pediatric_use = "-"

        try:
            use_in_specific_populations = d['use_in_specific_populations']
        
        except:
            use_in_specific_populations = "-"

        try:
            pharm_class_epc = d['openfda']['pharm_class_epc']
        
        except:
            pharm_class_epc = "-"

        try:
            pharm_class_cs = d['openfda']['pharm_class_cs']
        
        except:
            pharm_class_cs = "-"

        try:
            pharm_class_moa = d['openfda']['pharm_class_moa']
        
        except:
            pharm_class_moa = "-"

        try:
            pharm_class_pe = d['openfda']['pharm_class_pe']
        
        except:
            pharm_class_pe = "-"

        df1 = pd.DataFrame([
            (
            application_number,
            generic_name,  
            brand_name,
            product_ndc,
            indications_and_usage,
            clinical_studies,
            pediatric_use,
            use_in_specific_populations,
            pharm_class_epc,
            pharm_class_cs,
            pharm_class_moa,
            pharm_class_pe
            )
        ])
        
        if count == 0:
            df = df1
        
        else:
            df = pd.concat([df,df1])
        count += 1
        
    df.to_csv(f'{MEDIA_ROOT}'+'/'+'data.csv',index=False,mode='a',header=False)
    

def process(no):
    global eighteen_months,today
    no_fin = no
    count = 0
    skip = 0
    no_rep = no
    while skip < 26000:
        if skip > 0:
            print(f"api call {count}")
        if int(no) > 1000:
            no_rep = 1000
            no -= 1000
        
        else :
            no_rep = no
        response = requests.get(f"https://api.fda.gov/drug/label.json?search=effective_time:[{eighteen_months}+TO+{today}]+AND+_exists_:pediatric_use+_exists_:use_in_specific_populations&skip={skip}&limit={no_rep}",
        headers={
            
            "X-RapidAPI-Key": "z3DumUCTRasv3CcNT1qy2sTi0yw5ufRDcchVEYuS",
        }
        )
        

            


        files = response.json()


        with open('data.json', 'w') as f:
            json.dump(files, f)



        
        print(count)
        data = json.load(open('data.json'))['results']
        save_csv(data)
        
        
        
        
    
        df = pd.read_csv(f'{MEDIA_ROOT}'+'/'+'data.csv')
        
        # df = df.rename(columns={'0': 'application number', '1': 'generic name','2':'Trade Name','3':'Product Label','4':'indications and usage','5':'clinical_studies','6':'pediatric use','7':'use in specific populations','8':'Pharmacologic Class EPC','9':'Pharmacologic Class CS','10':'Pharmacologic Class MOA','11':'Pharmacologic Class PE'})
        
        

        skip += 1000
        if skip > no_fin :
            print(f"{no_fin} records fetched")
            
            response = FileResponse(open(f'{MEDIA_ROOT}'+'/'+'data.csv', 'rb'),as_attachment=True)

            return response

        count +=1

def index(req):
    return render(req, 'index.html')

def fetchdata(req):
    try:
        no = int(req.POST.get("recordint"))
    except TypeError:
        return redirect('index')
    
    if no > 25000:
        return redirect('index')
    

    df = pd.DataFrame(columns=["application number", "generic name", "Trade Name", "Product Label","indications and usage","clinical_studies","pediatric use","use in specific populations","Pharmacologic Class EPC","Pharmacologic Class CS","Pharmacologic Class MOA","Pharmacologic Class PE"])
    # df = df.rename(columns={'0': 'application number', '1': 'generic name','2':'Trade Name','3':'Product Label','4':'indications and usage','5':'clinical_studies','6':'pediatric use','7':'use in specific populations','8':'Pharmacologic Class EPC','9':'Pharmacologic Class CS','10':'Pharmacologic Class MOA','11':'Pharmacologic Class PE'})
    df.to_csv(f'{MEDIA_ROOT}'+'/'+'data.csv', index=False)

    fileobj=process(no)

    renderobj = pagination(req)
    return redirect('pagination')

    

def pagination(req):
    arrayRows=[]
    with open(f'{MEDIA_ROOT}'+'/'+'data.csv','r') as f:
        fileObj=csv.reader(f,delimiter=',')
        linCount=0
        for row in fileObj:
            if linCount==0:
                headerInfo=row
                linCount +=1
            else:
                arrayRows.append(row)
    
    if req.GET.get('pageNo') == None:
        pageNO=1
    else:
        pageNO=req.GET.get('pageNo')
    if req.GET.get('noOfElements') == None:
        noOfElements=10
    else:
        noOfElements=req.GET.get('noOfElements')
    pagC=Paginator(arrayRows,noOfElements)
    pacgObj=pagC.page(pageNO)
    data=pacgObj.object_list
    context={'data':data,'headerInfo':headerInfo,'noOfPages':list(pagC.page_range)}
    return render(req,'pagination.html',context)

def download(req):
    response = FileResponse(open(f'{MEDIA_ROOT}'+'/'+'data.csv', 'rb'),as_attachment=True)

    return response    