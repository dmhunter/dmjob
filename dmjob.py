# -*- coding: utf-8 -*-
import sys
reload(sys)
import urllib2
import urllib
import bs4
import xmllib
import lxml
sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
from lxml import etree
from lxml import html
import gzip
import zlib
import StringIO
import selenium
from selenium import webdriver
from selenium import common
from selenium import selenium
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import remote
from selenium.webdriver.remote import webelement
from selenium.webdriver.remote.webelement import WebElement 
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import MySQLdb

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-Agent' : user_agent }

#中国人才热线爬虫内容抓取－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
print "开始抓取中国人才热线网站\n"
cjolurl = 'http://s.cjol.com/l2008-kw-%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98/?SearchType=3&KeywordType=5'
cjolrequest=urllib2.Request(cjolurl,headers=headers)
cjolres=urllib2.urlopen(cjolrequest).read()
cjolresponse=etree.HTML(cjolres)	
jobs=[]	
n=0
cjolf=open('人才热线数据挖掘.doc','w')
#	print response.xpath('/html/head/title/text()')[0]  #表达式返回的是一个列表
for a in cjolresponse.xpath("/html//ul[@class='results_list_box']"):	
	b=['']
	for i in range(len(a.xpath("li[2]//text()"))): #获取每个工作条目信息：由于前一个注释的地方已说明时列表，因此需遍历
		b[0]+=a.xpath("li[2]//text()")[i]
 #由于源码中职位信息各个条目结构并不完全一样，但均在li[2]下，因此将获取的文本逐一添加到列表再合并
	jobdetailrequest=urllib2.Request(a.xpath('li[2]/h3/a/@href')[0].encode('utf-8'),headers=headers)
	jobdetailresponse=urllib2.urlopen(jobdetailrequest)
	detail=BeautifulSoup(jobdetailresponse)
	d={'jobtitle':b[0].encode('utf-8'),'jobdetaillink':a.xpath('li[2]/h3/a/@href')[0].decode('utf-8'),'company':a.xpath('li[3]//text()')[0].decode('utf-8'),'salary':a.xpath('li[8]//text()')[0].decode('utf-8'),'updatime':a.xpath('li[9]//text()')[0].decode('utf-8'),'jobdetail':detail.find('div',class_='positionstatement clearfix').get_text().decode('utf-8'),'from':'cjol'}
	jobs.append(d)
	content="职位："+jobs[n]['jobtitle']+"	"+"职位链接:"+jobs[n]['jobdetaillink']+"	"+"公司名:"+jobs[n]['company']+"\n"+"工资："+jobs[n]['salary']+"	"+"更新时间："+jobs[n]['updatime']+"\n"+"职位描述:"+jobs[n]['jobdetail']+"\n********************************************************************************\n"
	cjolf.write(content)
	n+=1
print '中国人才热线网站已爬完,抓取了',n,'条工作信息\n'

#智联招聘网站爬虫内容抓取－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
print "开始抓取智联招聘网站\n"
zlzpiniturl='http://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E6%B7%B1%E5%9C%B3&kw=%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98&sm=0&p='
zlzpinitrequest=urllib2.Request(zlzpiniturl+'1',headers=headers)
zlzpinitresponse=urllib2.urlopen(zlzpinitrequest)
zlzpinitdetail=BeautifulSoup(zlzpinitresponse)
zlzpresultsnums=int(zlzpinitdetail.find('span',class_='search_yx_tj').em.get_text()) #搜索结果总数量，用于计算总共有多少结果页面需要遍历
print "智联招聘网站共有",zlzpresultsnums,"条信息可爬取\n"
if zlzpresultsnums%40==0:
	zlzppagenums=zlzpresultsnums/40
else:
	zlzppagenums=1+zlzpresultsnums/40
zlzpn=0
jishu=0
zlzpjobs=[]
zlzpf=open("智联招聘数据挖掘.doc","w")
for zlzppage in range(1,zlzppagenums+1):
	zlzpurls=zlzpiniturl+str(zlzppage)
	zlzprequest=urllib2.Request(zlzpurls,headers=headers)
	zlzpres=urllib2.urlopen(zlzprequest).read()
	zlzpresponse=etree.HTML(zlzpres)
	for zlzpsel in zlzpresponse.xpath("//table[@class='newlist']")[2:]: #xpath表达式返回的是一个列表，观察源码，我们可以发现每页有４１个class为newlist的table，均为并列关系，我们需要抓取的内容位于从第２个开始直到第41个，因此这里用了[2:]		
		zlzpjobdetailrequest=urllib2.Request(zlzpsel.xpath('tr[1]/td[1]/div/a/@href')[0].decode('utf-8'),headers=headers)
		zlzpjobdetailresponse=urllib2.urlopen(zlzpjobdetailrequest)
		zlzpjobdetail=BeautifulSoup(zlzpjobdetailresponse)
		zlzpjobname=[''] 
		for zlzpj in range(len(zlzpsel.xpath('tr[1]/td[1]/div/a//text()'))):#有的职位名在多个标签下，需要合并处理
			zlzpjobname[0]+=zlzpsel.xpath('tr[1]/td[1]/div/a//text()')[zlzpj]
		
#测试		print 'jobtitle:',zlzpjobname[0].encode('utf-8')
#测试		print 'jobdetaillink:'zlzpsel.xpath('tr[1]/td[1]/div/a/@href')		
#测试		print 'company:',zlzpsel.xpath('tr[1]/td[3]/a/text()')[0].decode('utf-8')
#测试		print 'salary:',zlzpsel.xpath('tr[1]/td[4]/text()')[0].decode('utf-8')	
#测试		print 'updatime:',zlzpsel.xpath('tr[1]/td[6]/span/text()')[0].decode('utf-8')			
		zlzpjobiterm={'jobtitle':zlzpjobname[0].encode('utf-8'),'jobdetaillink':zlzpsel.xpath('tr[1]/td[1]/div/a/@href')[0],'company':zlzpsel.xpath('tr[1]/td[3]/a/text()')[0].decode('utf-8'),'salary':zlzpsel.xpath('tr[1]/td[4]/text()')[0].decode('utf-8'),'updatime':zlzpsel.xpath('tr[1]/td[6]/span/text()')[0].decode('utf-8'),'jobdetail':zlzpjobdetail.find('div',class_='tab-inner-cont').get_text().decode('utf-8'),'from':'zlzp'}
		zlzpjobs.append(zlzpjobiterm)
		zlzpjobcontent="职位："+zlzpjobs[zlzpn]['jobtitle']+"	"+"职位链接："+zlzpjobs[zlzpn]['jobdetaillink']+"	"+"公司名："+zlzpjobs[zlzpn]['company']+"\n"+"	"+"更新时间："+zlzpjobs[zlzpn]['updatime']+"\n"+"职位描述："+zlzpjobs[zlzpn]['jobdetail']+"\n******************************************************************************\n"
		zlzpn+=1
		zlzpf.write(zlzpjobcontent)
	jishu+=1
	print	"第",jishu,"页已抓取\n"	
print '智联招聘网站已爬完，共抓取了',zlzpn,'条工作信息'

#前程无忧网站爬虫内容抓取－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
print "开始抓取前程无忧网站\n"
qcwyjobs=[]
#获取结果页数
qcwylefthalfurl="http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=040000%2C00&district=000000&funtype=0000&industrytype=00&issuedate=9&providesalary=99&keyword=%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98&keywordtype=0&curr_page="
qcwyrighthalfurl="&lang=c&stype=2&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&list_type=0&fromType=14&dibiaoid=0&confirmdate=9"
qcwypagenum="1"
qcwyiniturl=qcwylefthalfurl+qcwypagenum+qcwyrighthalfurl
#"Accept-Encoding":"gzip, deflate, sdch",
liepinheaders={"Accept":"*/*","Accept-Encoding":"gzip, deflate, sdch","Accept-Language":"en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4","Cache-Control":"max-age=0","Connection":"keep-alive","Host":"js.51jobcdn.com","If-Modified-Since":"Sat, 04 Jul 2015 15:10:34 GMT","If-None-Match":"5597f76a-1a93","Referer":"http://search.51job.com/jobsearch/search_result.php?fromJs=1&jobarea=040000%2C00&district=000000&funtype=0000&industrytype=00&issuedate=9&providesalary=99&keyword=%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98&keywordtype=0&curr_page=1&lang=c&stype=2&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&list_type=0&fromType=14&dibiaoid=0&confirmdate=9","User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/45.0.2454.101 Chrome/45.0.2454.101 Safari/537.36"}
qcwyinitrequest=urllib2.Request('http://search.51job.com/list/040000%252C00,000000,0000,00,9,99,%25CA%25FD%25BE%25DD%25CD%25DA%25BE%25F2,0,1.html?lang=c&stype=2&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&list_type=0&confirmdate=9&fromType=14&dibiaoid=0',headers=liepinheaders)

driverinit=webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
driverinit.get('http://search.51job.com/list/040000%252C00,000000,0000,00,9,99,%25CA%25FD%25BE%25DD%25CD%25DA%25BE%25F2,0,1.html?lang=c&stype=2&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&list_type=0&confirmdate=9&fromType=14&dibiaoid=0')
driverinit.refresh()
#print driverinit.find_elements_by_xpath("//p[@class='t1']")
pagetext=driverinit.find_elements_by_xpath("//span[@class='td']")[0].text
pagenum=int(pagetext[1])
print "结果共有",pagenum,"页"
qcwyn=0
qcwyf=open("前程无忧数据挖掘工作.doc","w")
for qcwypage in range(1,pagenum+1):
	driverinit.get(qcwylefthalfurl+str(qcwypage)+qcwyrighthalfurl)
	for qcwysel in driverinit.find_elements_by_xpath("//div[@class='el']")[13:]:
#		print qcwysel.find_element_by_xpath("p[@class='t1']/a").text
#		print qcwysel.find_element_by_xpath("p[@class='t1']/a").get_attribute('href')
#		print qcwysel.find_element_by_xpath("span[@class='t2']/a").text
#		print qcwysel.find_element_by_xpath("span[@class='t4']").text
#		print qcwysel.find_element_by_xpath("span[@class='t5']").text
		qcwyjobdetailre=urllib2.Request(qcwysel.find_element_by_xpath("p[@class='t1']/a").get_attribute('href'),headers=headers)
		qcwyn+=1
		qcwyjobdetailpage=urllib2.urlopen(qcwyjobdetailre).read()
		qcwyjobdetailpagebs=BeautifulSoup(qcwyjobdetailpage)
		if qcwyjobdetailpagebs.find('div',class_='tCompany_text'):		
			qcwyjobdetail=qcwyjobdetailpagebs.find('div',class_='tCompany_text').ul.get_text()
		else:
			qcwyjobdetail='已暂停招聘'
		qcwyjobiterm={"jobtitle":qcwysel.find_element_by_xpath("p[@class='t1']/a").text,"jobdetaillink":qcwysel.find_element_by_xpath("p[@class='t1']/a").get_attribute('href'),"company":qcwysel.find_element_by_xpath("span[@class='t2']/a").text,"salary":qcwysel.find_element_by_xpath("span[@class='t4']").text,"updatime":qcwysel.find_element_by_xpath("span[@class='t5']").text,'jobdetail':qcwyjobdetail,'from':'qcwy'}
		qcwyjobs.append(qcwyjobiterm)
		qcwucontent="职位名："+qcwysel.find_element_by_xpath("p[@class='t1']/a").text+"	"+"职位链接："+qcwysel.find_element_by_xpath("p[@class='t1']/a").get_attribute('href')+"	"+"公司名："+qcwysel.find_element_by_xpath("span[@class='t2']/a").text+"\n"+"工资："+qcwysel.find_element_by_xpath("span[@class='t4']").text+"	"+"更新时间："+qcwysel.find_element_by_xpath("span[@class='t5']").text+"\n"+"工作描述："+qcwyjobdetail+"\n**************************************************************************\n"
		qcwyf.write(qcwucontent)
	print "第",qcwypage,"页已爬完！"
driverinit.close()
print "前程无忧网站已爬完,共抓取了",qcwyn,"条工作信息\n"


#猎聘网站爬虫内容抓取	
print "开始抓取猎聘网\n"
liepinpagenums=0
liepininiturl='http://www.liepin.com/zhaopin/?pubTime=30&salary=&jobKind=&clean_condition=&searchType=1&init=-1&searchField=1&key=%E6%95%B0%E6%8D%AE%E6%8C%96%E6%8E%98&industries=&jobTitles=&dqs=050090&compscale=&compkind=&ckid=79c7a556033032d0&curPage='
#通过观察首页源码中末页链接，找出末页页码规律，获取结果页总数量
liepininitrequest=urllib2.Request(liepininiturl+str(liepinpagenums),headers=headers)
liepinitres=urllib2.urlopen(liepininitrequest).read()
liepinitres=etree.HTML(liepinitres)
lastpagelink=liepinitres.xpath("//a[@class='last']/@href")[0]
lastpagenum=int(lastpagelink[-1])
print "结果有",lastpagenum,"页"
liepinjobs=[]
liepinn=0
liepinf=open("猎聘网数据挖掘.doc","w")
for liepinpage in range(lastpagenum):
	liepinurl=liepininiturl+str(liepinpage)
	liepinrequest=urllib2.Request(liepinurl,headers=headers)
	liepinres=urllib2.urlopen(liepinrequest).read()
	liepinresponse=etree.HTML(liepinres)
	for liepinsel in liepinresponse.xpath("//div[@class='sojob-item-main clearfix']"):
		liepinjobdetailrequest=urllib2.Request(liepinsel.xpath("a/@href")[0],headers=headers)
		liepinjobdetailres=urllib2.urlopen(liepinjobdetailrequest).read()
		liepinjobdetailresponse=BeautifulSoup(liepinjobdetailres)		
#		print '职位名：',liepinsel.xpath("a/h3/span/text()")[0]
#		print '职位链接：',liepinsel.xpath("a/@href")[0]		
#		print '公司名：',liepinsel.xpath("div/a/p[1]/text()")[0]	
#		print '工资：',liepinsel.xpath("a/p[1]/span[1]/text()")[0]
#		print '学历：',liepinsel.xpath("a/p[1]/span[3]/text()")[0]
#		print '经验：',liepinsel.xpath("a/p[1]/span[4]/text()")[0]		
#		print '职位描述：',liepinjobdetailresponse.find('div',class_='content content-word').get_text()	
#		print '更新时间：',liepinsel.xpath("a/p[2]/time/text()")[0]	
		liepinjobiterm={"jobtitle":liepinsel.xpath("a/h3/span/text()")[0],"jobdetaillink":liepinsel.xpath("a/@href")[0],"company":liepinsel.xpath("div/a/p[1]/text()")[0],"salary":liepinsel.xpath("a/p[1]/span[1]/text()")[0],"updatime":liepinsel.xpath("a/p[2]/time/text()")[0],"jobdetail":liepinjobdetailresponse.find('div',class_='content content-word').get_text(),'from':'liepin'}
		liepinjobs.append(liepinjobiterm)
		liepinjobcontent="职位名："+liepinjobs[liepinn]['jobtitle']+"	"+"职位链接："+liepinjobs[liepinn]['jobdetaillink']+"	"+"公司名："+liepinjobs[liepinn]['company']+"\n"+"工资："+liepinjobs[liepinn]['salary']+"	"+"\n"+"工作职责："+liepinjobs[liepinn]['jobdetail']+"\n*******************************************************\n"
		liepinf.write(liepinjobcontent)
		liepinn+=1
	print '第',liepinpage+1,'页已抓取完！'
print "猎聘网已抓取完毕！共抓取了",liepinn,"条工作信息"

print "开始整理汇总……\n"
#去除重复的工作信息，将工作信息保存至数据库（标明每条工作信息来自哪个网站）以及doc文件
#已爬取到中国人才网的cjol数组，智联招聘网的zlzpjob数组，前程无忧网站的qcwyjobs,猎聘网的liepinjobs四个数组，每个数组内部条目均不相同，但各数组间可能有重复条目，我们先将条目最多的作为基准，看其他数组中是否有不同的条目，如果有，则将其添加进去，如果没有则遍历下一条。不同条目之间相同与否的确定：如果职位名与公司名均相同，则客认为两条信息相同
if len(jobs)==max(len(jobs),len(zlzpjobs),len(qcwyjobs),len(liepinjobs)):
	base=jobs[:]
elif len(zlzpjobs)==max(len(jobs),len(zlzpjobs),len(qcwyjobs),len(liepinjobs)):
	base=zlzpjobs[:]
elif len(qcwyjobs)==max(len(jobs),len(zlzpjobs),len(qcwyjobs),len(liepinjobs)):
	base=qcwyjobs[:]
else:
	base=liepinjobs[:]
sumset=[]
#将几个列表合并起来
for daoruj in range(len(jobs)):
	sumset.append(jobs[daoruj])
for daoruz in range(len(zlzpjobs)):
	sumset.append(zlzpjobs[daoruz])
for daoruq in range(len(qcwyjobs)):
	sumset.append(qcwyjobs[daoruq])
for daorul in range(len(liepinjobs)):
	sumset.append(liepinjobs[daorul])
#遍历合并的sumset列表，将其逐一与base列表每条信息比对，如果jobtitle与company均相同，则比对下一条记录。这里使用一个参数bijiaon，如果sumset列表中记录与base中某条记录相同则将其乘以０，如果不等则乘以１，这样遍历完之后如果bijiaon为０，则说明sumset中的记录已经存在于base列表中，无需添加记录，如果bijiaon为１，则说明base列表中没有与该sumset记录相同的，应将其加入base列表。
for sumseti in sumset:
	bijiaon=1
	for baseitem in base:
		if sumseti['jobtitle']==baseitem['jobtitle'] and sumseti['company']==baseitem['company']:
			bijiaon*=0
		else:
			bijiaon*=1
	if bijiaon!=0:
		base.append(sumseti)
	else:
		break			
huizongf=open("四大主流网站数据挖掘工作汇总.doc",'w')
db=MySQLdb.connect(host='localhost',user='root',passwd='hsj123',db='train',charset='utf8')
cursor=db.cursor()
createsql="create table if not exists dmjobs(jobtitle text(100),company varchar(100),jobdetaillink varchar(100),salary varchar(40),fromweb varchar(20),updatime varchar(40),jobdetail varchar(2000))"
cursor.execute(createsql)
basek=0
def insertsql(base,basei):
	insertsql="insert into dmjobs values ('%s','%s','%s','%s','%s','%s','%s')" % (base[basei]['jobtitle'],base[basei]['company'],base[basei]['jobdetaillink'],base[basei]['salary'],base[basei]['updatime'],base[basei]['from'],str(base[basei]['jobdetail']).replace('\\n',''))
	cursor.execute(insertsql)
	db.commit()

for basei in range(len(base)):
	basecontent="职位名："+base[basei]['jobtitle']+"	"+"职位链接:"+base[basei]['jobdetaillink']+"	"+"公司名："+base[basei]['company']+"\n"+"来自："+base[basei]['from']+"职位描述："+base[basei]['jobdetail']+"\n***************************************************************************\n"
	huizongf.write(basecontent)
	try:
#		insertsql="insert into dmjobs values ('%s','%s','%s','%s','%s','%s','%s')" % (base[basei]['jobtitle'],base[basei]['company'],base[basei]['jobdetaillink'],base[basei]['salary'],base[basei]['updatime'],base[basei]['from'],str(base[basei]['jobdetail']).replace('\\n',''))
#		cursor.execute(insertsql)
#		db.commit()
		insertsql(base,basei)
		basek+=1
	except:
		print base[basei]['from'],"网站第",basek,"条记录插入异常！"
		continue
db.close()	
huizongf.close()
print "汇总完毕,并存储在doc和数据库中。共删除了",len(jobs)+len(zlzpjobs)+len(qcwyjobs)+len(liepinjobs)-len(base),"条重复信息，共筛选出",len(base),"条信息\n"
