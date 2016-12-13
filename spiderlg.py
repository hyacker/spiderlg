#!/usr/bin/env python
#coding=UTF-8
import requests
import json
import time
import MySQLdb


SERCHKEY = '爬虫' #your special keyword

url = 'https://www.lagou.com/jobs/positionAjax.json?'

headers = {'Accept':'application/json, text/javascript, */*; q=0.01', \
           'Accept-Encoding':'gzip, deflate, br', \
	   'Accept-Language':'zh-CN,zh;q=0.8', \
	   'Content-Length':'38', \
	   'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8', \
	   'Host':'www.lagou.com', \
	   'Origin':'https://www.lagou.com', \
           'Referer':'https://www.lagou.com/jobs/list_%E7%88%AC%E8%99%AB?px=default&city=%E5%85%A8%E5%9B%BD', \
	   'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36', \
	   'X-Anit-Forge-Code':'0', \
	   'X-Anit-Forge-Token':'None', \
           'X-Requested-With':'XMLHttpRequest'}


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('UTF-8')
    else:
        return input

def json_loads_byteified(json_text):
    return byteify(
        json.loads(json_text, object_hook=byteify)
    )

def json_load_byteified(file_handle):
    return byteify(
        json.load(file_handle, object_hook=byteify)
    )


def create_params(isfrist,pagenum,keydes):
	if isfrist :
		paradata = {'px':'default','needAddtionalResult':'false',' first':'true','pn':'1','kd':keydes}
		return paradata
	else:
		tempn = str(pagenum)
		paradata = {'px':'default','needAddtionalResult':'false',' first':'false','pn':tempn,'kd':keydes}
		return paradata

def load_field(itedict):
	
	"""
	insertValue =[positionId,lastLogin,city,companyShortName,formatCreateTime,createTime]
	"""
	if itedict.get('industryField'):
		industry = '|'.join(itedict.get('industryField'))
		print industry
	else:
		industry = '0'
	if itedict.get('businessZones'):
		bizZone = '|'.join(itedict.get('businessZones'))
		print bizZone
	else:
		bizZone = '0'
	if itedict.get('companyLabelList'):
		comLabel = '|'.join(itedict.get('companyLabelList'))
		print comLabel
	else:
		comLabel = '0'
	
	resValue = [ \
		    itedict.get('positionId'), \
		    itedict.get('companyId'), \
		    itedict.get('lastLogin'), \
		    itedict.get('firstType'), \
		    #itedict.get('industryField'), \
		    #industry ,\
		    itedict.get('education'), \
		    itedict.get('workYear'), \
		    itedict.get('city'), \
		    itedict.get('salary'), \
		    itedict.get('positionName'), \
		    itedict.get('companySize'), \
		    itedict.get('companyShortName'), \
		    itedict.get('companyFullName'), \
		    itedict.get('financeStage'), \
		    itedict.get('jobNature'), \
		    itedict.get('formatCreateTime'), \
		    itedict.get('createTime'), \
		    itedict.get('district'), \
		    #itedict.get('businessZones'), \
		    #bizZone , \		
		    #itedict.get('companyLabelList'), \
		    #comLabel , \
		    #itedict.get('imState'), \
		   ]

	return resValue

def table_insert_string():
	#return 'insert into S_lg_Result(positionId,companyId,lastLogin,firstType,industryField,education,workYear,city,salary,positionName,companySize,companyShortName,companyFullName,financeStage,jobNature,formatCreateTime,createTime,district,businessZones,companyLabelList) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
	return 'insert into S_lg_Result(positionId,companyId,lastLogin,firstType,education,workYear,city,salary,positionName,companySize,companyShortName,companyFullName,financeStage,jobNature,formatCreateTime,createTime,district) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

def load_page_field(input,pagesize):
	index = 0
	loadlist = []
	while index < pagesize:
		tmpline = input[index]
		loadedfield = load_field(tmpline)
		loadlist.append(loadedfield)
		index+=1
		
	return loadlist


try:
	conn = MySQLdb.connect(host=[yourhostname],user=[yourusername],passwd=[yourpasswd],charset='utf8',db=[yourdb],port=3306)
	cur  = conn.cursor()

	#first request

	params = create_params(True,1,SERCHKEY)

	res = requests.post(url,headers=headers,data=params)

	resultdict = json_loads_byteified(res.text)

	repsize = int(resultdict.get('content').get('pageSize'))

	recount = int(resultdict.get('content').get('positionResult').get('totalCount'))


	pagetotal = recount/repsize + 1


	ResultList = load_page_field(resultdict.get('content').get('positionResult').get('result'),int(resultdict.get('content').get('positionResult').get('resultSize')))
	
	InsertString = table_insert_string()
	cur.executemany(InsertString,ResultList)


	
	pagenum =1 
	while pagenum <pagetotal:
		time.sleep(5)
		pagenum+=1
		params = create_params(False,pagenum,SERCHKEY)
		res = requests.post(url,headers=headers,data=params)
		resultdict = json_loads_byteified(res.text)


		TempResult = load_page_field(resultdict.get('content').get('positionResult').get('result'),int(resultdict.get('content').get('positionResult').get('resultSize')))
		
		cur.executemany(InsertString,TempResult)



	conn.commit()
	cur.close()
	conn.close()
except MySQLdb.Error,e:
	print "MySQL Error %d: %s" % (e.args[0],e.args[1])
	
