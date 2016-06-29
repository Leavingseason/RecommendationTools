
import math
import datetime
import random
from RecFactory import *



def AppendTimestamp(infile,outfile,rawfile,uid_idx,iid_idx,time_idx, timeformat="%Y-%m-%d %H:%M:%S"):
	'''
	MyMediaLite file format is: userid::itemid::score::seconds_since_1970
	this function could generate MyMediaLite format from rawfile
	'''
	idhelper = IDTransformers();
	useridmap ,_  = idhelper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\IdMap\user_mapid.csv')
	itemidmap , _  = idhelper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\IdMap\item_mapid.csv')
	base_date =  datetime.datetime(1970,01,01)
	
	user_item_score = dict()
	user_item_time = dict()
	
	rd = open(infile,'r')
	while True:
		line = rd.readline()
		if not line:
			break 
		words = line[:-1].split('\t')
		score = words[0]
		uid = words[1]
		iid = words[2]
		if not uid in user_item_score:
			user_item_score[uid]=dict()
		user_item_score[uid][iid]=score			
	rd.close()
	
	
	rd = open(rawfile,'r')
	rd.readline()
	cnt = 0 
	while True:
		line = rd.readline()
		if not line:
			break 
		cnt +=1 
		if cnt % 100000 == 0:
			print cnt
		words = line[:-1].split(',')
		uid = words[uid_idx]
		iid = words[iid_idx]
		if not uid in useridmap or not iid in itemidmap:
			continue
		uid = useridmap[words[uid_idx]]
		iid = itemidmap[words[iid_idx]]
		if uid in user_item_score and iid in user_item_score[uid]:
			ctime = datetime.datetime.strptime(words[time_idx],timeformat)
			seconds = (ctime-base_date).days*24*3600
			if not uid in user_item_time:
				user_item_time[uid]=dict()
			user_item_time[uid][iid] = seconds	
	rd.close()
	
	
	rd = open(infile,'r')
	wt = open(outfile,'w')
	while True:
		default_date = datetime.datetime(2016,2,1)
		line = rd.readline()
		if not line:
			break 
		words = line[:-1].split('\t')
		score = words[0]
		uid = words[1]
		iid = words[2]
		if uid in user_item_time and iid in user_item_time[uid]:
			seconds = user_item_time[uid][iid]
		else:
			seconds = (default_date-base_date).days*24*3600
		wt.write('%s::%s::%s::%s\n' %(uid,iid,score,str(seconds)))
	rd.close()
	wt.close()

def SelectValidSet(infile,outfile,start_date,end_date):
	
	rd = open(infile,'r')
	wt = open(outfile,'w')
	
	line = rd.readline()
	
	cnt=0
	while True:
		line = rd.readline()
		if not line:
			break
			
		cnt+=1
		if cnt % 10000 == 0:
			print cnt,'\t',words[len(words)-1]
		 
		words = line.split(',')
		
		try:
			curtime = datetime.datetime.strptime(words[2],"%Y-%m-%d %H:%M:%S")
		except:
			print 'unexpected error:', sys.exc_info()[0]
		
		event_type = words[3].lower()
		
		if curtime>=start_date and curtime < end_date and event_type == 'carousel':
			wt.write(line)
		
	rd.close()
	wt.close()

def FakeSubmission(infile,outfile):
		
	rd = open(infile,'r')
	wt = open(outfile,'w')
	
	line = rd.readline()
	wt.write(line)
	
	while True:
		line = rd.readline()
		if not line:
			break;
		words = line.replace('\r\n','').split(',')
		
		 
		pos = int(words[1])
		if pos > 5:
			pos = 5
		wt.write(words[0]+','+str(pos)+'\n')
		
	rd.close()
	wt.close()


def StatItemPopularity(infile,start_date,end_date, weighted=False, outfile =None):
	checkpoint = datetime.datetime(2016,03,21)
	rd = open(infile,'r')
	
	item2clickcnt = dict()
	item2showcnt = dict()
	item2totalshowcnt = dict()
	item2totalclickcnt = dict()
	
	rd.readline()
	
	cnt=0
	while True:
		line = rd.readline()
		if not line :
			break
		cnt+=1
		if cnt % 100000 == 0:
			print cnt 
			
		#if cnt > 1000000 :
		#	break ##--
		words = line[:-1].split(',')
		
		event_type = words[3].lower() 
		
		if event_type == 'carousel': 
			curtime = datetime.datetime.strptime(words[2],"%Y-%m-%d %H:%M:%S")
			if curtime<start_date or curtime >= end_date:
				continue
			click = int(words[6])
			
			if weighted:
				wshow = math.pow(0.98,(checkpoint-curtime).days)
			else :
				wshow=1
			if words[1] in item2showcnt:
				item2showcnt[words[1]]+=wshow
				item2totalshowcnt[words[1]]+=1
			else:
				item2showcnt[words[1]]=wshow
				item2totalshowcnt[words[1]]=1
			
			if click == 1:
				if weighted:
					#click = 1.0/(1+math.exp(-1.0*(checkpoint-curtime).days/80))
					click = math.pow(0.98,(checkpoint-curtime).days)
				if words[1] in item2clickcnt:
					item2clickcnt[words[1]]+=click
					item2totalclickcnt[words[1]]+=1
				else:
					item2clickcnt[words[1]]=click 
					item2totalclickcnt[words[1]]=1
	
	rd.close()
	
	
	if outfile is not None:
		wt = open(outfile,'w')
		wt.write('sid,wclickcnt,wctr,wshowcnt,clickcnt,showcnt,ctr\n')
		for key,value in item2clickcnt.items():
			wt.write(str(key)+','+str(value)+ ','+ str(value*1.0/item2showcnt[key]) +',' + str(item2showcnt[key]) + ',' + str(item2totalclickcnt[key]) +','+ str(item2totalshowcnt[key]) +',' +str(item2totalclickcnt[key]*1.0/item2totalshowcnt[key]) +'\n')
		wt.close()
	
	return item2clickcnt

	
def PourOneSession(wt,rowids,itemids,item2clickcnt):
	item_id_cnt = list()
	for item in itemids:
		if item in item2clickcnt:
			item_id_cnt.append([item,item2clickcnt[item]])
		else:
			item_id_cnt.append([item,0])
	item_id_cnt_sorted = sorted(item_id_cnt, cmp=lambda x,y: -x[1]+y[1] )##--
	item2sortedidx = dict([(w[0],i+1) for i,w in enumerate(item_id_cnt_sorted)])
	for i in range(len(rowids)):
		wt.write(rowids[i]+','+ str(item2sortedidx[item_id_cnt[i][0]])+'\n')
		
	return item_id_cnt_sorted

	
def PourOneSession(wt,rowids,itemids,idx2itemid):
	item_rank = list()
	for idx,itemid in idx2itemid.items():
		item_rank.append([itemid,idx])
	item_rank_sorted = sorted(item_rank, cmp=lambda x,y: x[1]-y[1] )##--
	item2sortedrank = dict([(w[0],i+1) for i,w in enumerate(item_rank_sorted)])
	for i in range(len(rowids)):
		wt.write(rowids[i]+','+ str(item2sortedrank[itemids[i]])+'\n')
	return item2sortedrank

def WriteSubmisionFile(carouse2pred,testfile,outfile):
	rd = open(testfile,'r')
	wt = open(outfile,'w')

	rowids = list()
	itemids = list()
	last_carouse = "-1" 
	
	rd.readline()
	wt.write('RowId,ModelPosition\n')
	
	flag = True
	
	while True:
		line = rd.readline()
		if not line:
			break 
		words = line[:-1].split(',')
		cur_carouse = words[4]
		if last_carouse!=cur_carouse and last_carouse!="-1":
			pred = PourOneSession(wt,rowids,itemids,carouse2pred[last_carouse])
			rowids=[]
			itemids=[]
			if flag:
				for b in pred:
					print b
				flag=False
		last_carouse = cur_carouse
		rowids.append(words[0])
		itemids.append(words[6]) 
		
		
	if len(rowids) > 0:
		PourOneSession(wt,rowids,itemids,carouse2pred[last_carouse])
	
	rd.close()
	wt.close()

	
def PredctByPopularity(testfile,outfile,trainfile,start_date,end_date):
	
	item2clickcnt = StatItemPopularity(trainfile,start_date,end_date)
	#item2clickcnt = LoadItemClickcnt(r'D:\competitions\MS_RecSys\data\my\item_click_cnt_20151210_20160310.csv')	
	
	'''
	wt = open(r'D:\competitions\MS_RecSys\data\my\item_click_cnt_20151210_20160314.csv','w')
	wt.write('sid,clickcnt\n')
	for key,value in item2clickcnt.items():
		wt.write(str(key)+','+str(value)+'\n')
	wt.close()
	'''
	
	rd = open(testfile,'r')
	wt = open(outfile,'w')

	rowids = list()
	itemids = list()
	last_carouse = "-1" 
	
	rd.readline()
	wt.write('RowId,ModelPosition\n')
	
	flag = True
	
	while True:
		line = rd.readline()
		if not line:
			break 
		words = line[:-1].split(',')
		cur_carouse = words[4]
		if last_carouse!=cur_carouse and last_carouse!="-1":
			pred = PourOneSession(wt,rowids,itemids,item2clickcnt)
			rowids=[]
			itemids=[]
			if flag:
				for b in pred:
					print b
				flag=False
		last_carouse = cur_carouse
		rowids.append(words[0])
		itemids.append(words[6]) 
		
		
	if len(rowids) > 0:
		PourOneSession(wt,rowids,itemids,item2clickcnt)
	
	rd.close()
	wt.close()

def LoadCarousel2User(infile):
	carousel2user = dict()
	rd = open(infile,'r')
	rd.readline()
	while True:
		line = rd.readline()
		if not line:
			break 
		words = line[:-1].split(',')
		carousel2user[words[4]]=words[1]
	rd.close()
	return carousel2user
	
def LoadGroundtruth(validfile,start_date,end_date):
	
	carouse2user = dict()

	carouse2clicked = dict()
	
	rd = open(validfile,'r')
	
	cnt = 0 
	while True:
		line = rd.readline()
		if not line:
			break
		cnt += 1 
		if cnt % 100000 == 0:
			print cnt 
			
		words = line[:-1].split(',')
		curtime = datetime.datetime.strptime(words[2],"%Y-%m-%d %H:%M:%S")
		
		carouse2user[words[4]] = words[0]
		
		if curtime<start_date or curtime>=end_date:
			continue;
		
		event_type = words[3].lower()		
		
		if event_type == 'carousel':					
			click = int(words[6])
			if click==1:
				if not words[4] in carouse2clicked:
					carouse2clicked[words[4]] = set()
				carouse2clicked[words[4]].add(words[1])		
	
	rd.close()
	
	return carouse2clicked,carouse2user

def PredictByPosition(validfile, carouse_idx = 4, position_idx = 5, sid_idx = 1, hasheader=False):

	carouse2pred = dict()
	
	rd = open(validfile,'r')
	if hasheader:
		rd.readline()
		
	cnt = 0 
	while True:
		line = rd.readline()
		if not line:
			break
			
		cnt += 1 
		#if cnt % 100000 == 0:
		#	print cnt 
			
		words = line[:-1].split(',')
 
		if not words[carouse_idx] in carouse2pred:
			carouse2pred[words[carouse_idx]] = dict()
		position = int(words[position_idx])
		#if position in carouse2pred[words[carouse_idx]]:
		#	print 'position %s already for carouse %s  movie %s'  %(position,words[carouse_idx],words[sid_idx])
		carouse2pred[words[carouse_idx]][position] = words[sid_idx]	
	
	rd.close()
	
	carouse2pred = CompactPosition(carouse2pred)
	
	return carouse2pred

def CompactPosition(carouse2pred):
	res = dict()
	for carouse in carouse2pred:
		res[carouse] = dict()
		
		idx_item_list = []
		for key,value in carouse2pred[carouse].items():
			idx_item_list.append([key,value])
		
		idx_item_list = sorted(idx_item_list, cmp = lambda a,b: a[0]-b[0])
		#print idx_item_list
		for i in range(len(idx_item_list)):
			res[carouse][i]=idx_item_list[i][1]
		
	return res	
	
def AdjustByPopulairty(carouse2pos,item2clickcnt, ASC=True):
	carouse2pred = dict()	
	for carouse in carouse2pos:
		item_cnt_list = []
		for key,value in carouse2pos[carouse].items():
			if value in item2clickcnt:
				item_cnt_list.append([value, item2clickcnt[value],key])
				#print 'yes'
			else:
				item_cnt_list.append([value, 0, key])
		#random.shuffle(item_cnt_list)
		if ASC:
			item_cnt_list_sorted = sorted(item_cnt_list, cmp = lambda b,a: (1 if b[1]-a[1]>0 else -1) if a[1]!=b[1] else int(a[0]) - int(b[0]))  ##-- ASC
		else:
			item_cnt_list_sorted = sorted(item_cnt_list, cmp = lambda a,b: (1 if b[1]-a[1]>0 else -1) if a[1]!=b[1] else int(a[0]) - int(b[0]))  ##-- DESC
		#print item_cnt_list_sorted
		carouse2pred[carouse] = dict()
		for i in range(len(item_cnt_list_sorted)):
			carouse2pred[carouse][i]=item_cnt_list_sorted[i][0]
	
	return carouse2pred

	
def AdjustByRandomly(carouse2pos):

	carouse2pred = dict()
	
	for carouse in carouse2pos:
		item_cnt_list = []
		for key,value in carouse2pos[carouse].items():
			item_cnt_list.append([value,random.random(),key])
			
		item_cnt_list_sorted = sorted(item_cnt_list, cmp = lambda b,a: (1 if b[1]-a[1]>0 else -1) if a[1]!=b[1] else int(a[0]) - int(b[0]))  
		
		carouse2pred[carouse] = dict()
		for i in range(len(item_cnt_list_sorted)):
			carouse2pred[carouse][i]=item_cnt_list_sorted[i][0]
	
	return carouse2pred
	
def AdjustByMFPred(carouse2pos,carouse2user,user_item_score):

	carouse2pred = dict()
	
	for carouse in carouse2pos:
		userid = carouse2user[carouse]
		item2score = user_item_score[userid] if userid in user_item_score else dict()
		item_cnt_list = []
		for key,value in carouse2pos[carouse].items():
			if value in item2score:
				item_cnt_list.append([value, item2score[value],key])
				#print 'yes'
			else:
				item_cnt_list.append([value, 0, key])
		#random.shuffle(item_cnt_list)
		item_cnt_list_sorted = sorted(item_cnt_list, cmp = lambda a,b: (1 if b[1]-a[1]>0 else -1) if a[1]!=b[1] else int(a[0]) - int(b[0]))   
		#print item_cnt_list_sorted
		carouse2pred[carouse] = dict()
		for i in range(len(item_cnt_list_sorted)):
			carouse2pred[carouse][i]=item_cnt_list_sorted[i][0]
	
	return carouse2pred

	
def PredictByPopularity(validfile,item2clickcnt):
	carouse2pos = PredictByPosition(validfile)
	carouse2pred = AdjustByPopulairty(carouse2pos,item2clickcnt)	
	
	return carouse2pred
	
def CalcNDCG(carouse2clicked,carouse2pred):	
	scores = 0.0 
	n = 0 	
	for carouse in carouse2clicked:
		dcg_star = 0
		dcg = 0
		true_len = len(carouse2clicked[carouse])
		for i in range(5):
			if i < true_len:
				dcg_star += 1.0/ math.log(i+2,2)
			dcg += (1.0 if i in carouse2pred[carouse] and carouse2pred[carouse][i] in carouse2clicked[carouse] else 0.0) / math.log(i+2,2)
		
		ndcg = 0
		if dcg_star>0:
			ndcg = dcg / dcg_star 
		
		scores += ndcg 
		n+=1
	
	scores = scores / n 	
	return scores


def CalcNDCG2(carouse2clicked,carouse2pred):
	
	scores = 0.0 
	n = 0 
	
	for carouse in carouse2pred:
		dcg_star = 0
		dcg = 0
		
		
		if not carouse in carouse2clicked:
			n+=1 
			continue
		
		true_len = len(carouse2clicked[carouse])
		
		for i in range(5):
			if i < true_len:
				dcg_star += 1.0/ math.log(i+2,2)
			dcg += (1.0 if i in carouse2pred[carouse] and carouse2pred[carouse][i] in carouse2clicked[carouse] else 0.0) / math.log(i+2,2)
		
		ndcg = 0
		if dcg_star>0:
			ndcg = dcg / dcg_star 
		
		scores += ndcg 
		n+=1
	
	scores = scores / n 
	
	return scores


def LoadItemClickcnt(infile,value_idx=1):
	item2cnt = dict()
	rd = open(infile,'r')
	rd.readline()
	while True:
		line = rd.readline()
		if not line:
			break 
		words = line[:-1].split(',')
		item2cnt[words[0]]=float(words[value_idx])
	rd.close()
	return item2cnt

def ValidTest(start_date,end_date):
	'''
	do cross validation
	try different models
	'''
	
	print 'validing ',start_date,' ',end_date
	
	carouse2clicked, carouse2user = LoadGroundtruth(r'D:\competitions\MS_RecSys\data\my\ValidSet_testusers.csv',start_date,end_date)
	carouse2pred = PredictByPosition(r'D:\competitions\MS_RecSys\data\my\ValidSet_testusers.csv')
	score_1  =  CalcNDCG(carouse2clicked,carouse2pred)
	#score2 = CalcNDCG2(carouse2clicked,carouse2pred)	
	print 'clicked carouse cnt : ', str(len(carouse2clicked))
	print 'prediction carouse cnt : ', str(len(carouse2pred))	
	print 'position score: ',score_1 
	#print score2
	
	########  random prediction  used as a baseline
	carouse2pred5 = AdjustByRandomly(carouse2pred)
	score_5 = CalcNDCG(carouse2clicked,carouse2pred5)
	print 'random: ', score_5 , '   relative : ', score_1*1.0/score_5
	
	'''
	item2clickcnt = StatItemPopularity(
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		datetime.datetime(2015,10,10),datetime.datetime(2016,3,10),
		weighted=True,
		outfile=r'D:\competitions\MS_RecSys\data\my\item_click_weighted_cnt_20151210_20160310.csv')
	'''	 	
	item2clickcnt = LoadItemClickcnt(r'D:\competitions\MS_RecSys\data\my\item_click_weighted_cnt_20151210_20160310.csv',value_idx=1)	
	 
	
	#########  popularity
	carouse2pred_pop = AdjustByPopulairty(carouse2pred,item2clickcnt)
	score_3  =  CalcNDCG(carouse2clicked,carouse2pred_pop)
	print 'popularity: ',score_3 ,'   relative: ', score_1*1.0/score_3	
	
	carouse2pred_pop_desc = AdjustByPopulairty(carouse2pred,item2clickcnt,ASC=False)
	score_3  =  CalcNDCG(carouse2clicked,carouse2pred_pop_desc)
	print 'popularity desc: ',score_3 ,'   relative: ', score_1*1.0/score_3	
	
	#carouse2pred3 = AvgPrediction(carouse2pred,carouse2pred2)
	carouse2pred3 = AvgPredictionArray([carouse2pred,carouse2pred_pop],[0.6,0.4])
	score_2  =  CalcNDCG(carouse2clicked,carouse2pred3) 
	print 'avg pos+pop : ',score_2 ,  '  relative : ', score_1*1.0/score_2
	   
	carouse2pred3 = AvgPredictionArray([carouse2pred,carouse2pred_pop_desc],[0.6,0.4])
	score_2  =  CalcNDCG(carouse2clicked,carouse2pred3) 
	print 'avg pos+pop desc : ',score_2 ,  '  relative : ', score_1*1.0/score_2
	
	#########   TLC MF
	rec_helper = RecFactory()	
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\tlc\0.inst.valid.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		mode_dup = False
	)
	carouse2pred4 = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_4  =  CalcNDCG(carouse2clicked,carouse2pred4)
	print 'MF: ', score_4 , '   relative : ', score_1*1.0/score_4	
	
	carouse2pred41 = AvgPredictionArray([carouse2pred,carouse2pred4],[0.6,0.4])
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'MF + pos: ', score_41 , '   relative : ', score_1*1.0/score_41
	
	######## classification train-test ##########
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\tlc\0.inst.smallset.valid.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		mode_dup = False
	)
	carouse2pred_MF_smallset = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_MF_smallset  =  CalcNDCG(carouse2clicked,carouse2pred_MF_smallset)
	print 'MF small: ', score_MF_smallset , '   relative : ', score_1*1.0/score_MF_smallset
	
	
	########  SVD Feature 	
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\pred_128.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv'
	)
	carouse2pred_svd = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_svd  =  CalcNDCG(carouse2clicked,carouse2pred_svd)
	print 'SVD feature: ', score_svd , '   relative : ', score_1*1.0/score_svd
	
	
	carouse2pred_svd_avg = AvgPredictionArray([carouse2pred,carouse2pred_svd],[0.6,0.4])
	score_svd_avg  =  CalcNDCG(carouse2clicked,carouse2pred_svd_avg)
	print 'SVD + pos: ', score_svd_avg , '   relative : ', score_1*1.0/score_svd_avg
 
	 
	########  SVD feature 	with profile	
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\pred_enrich_d128_ite50.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv'
	)
	carouse2pred_svd_enrich = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_svd  =  CalcNDCG(carouse2clicked,carouse2pred_svd_enrich)
	print 'SVD enrich feature: ', score_svd , '   relative : ', score_1*1.0/score_svd 
	
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\pos_only\pred_enrich_128_valid.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv'
	)
	carouse2pred_svd_posonly = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_svd  =  CalcNDCG(carouse2clicked,carouse2pred_svd_posonly)
	print 'SVD enrich no search: ', score_svd , '   relative : ', score_1*1.0/score_svd
	

	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature_search4\pred_128_enrich_s4_valid_i100.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv'
	)
	carouse2pred_svd_enrich_search4 = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_svd  =  CalcNDCG(carouse2clicked,carouse2pred_svd_enrich_search4)
	print 'SVD enrich search4 i100: ', score_svd , '   relative : ', score_1*1.0/score_svd	
	#######################
	
	
	#######################
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\TLC\FT.small.valid.txt',
		#r'D:\competitions\MS_RecSys\data\my\features\user_item_ratings_test_complete.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		mode_dup = False,
		score_idx=4
	)
	carouse2pred_FTwithMF = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_4  =  CalcNDCG(carouse2clicked,carouse2pred_FTwithMF)
	print 'FT: ', score_4 , '   relative : ', score_1*1.0/score_4
	
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\TLC\FT.small.valid.withoutMF.txt',
		#r'D:\competitions\MS_RecSys\data\my\features\user_item_ratings_test_complete.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		mode_dup = False,
		score_idx=4
	)
	carouse2pred_FT_noMF = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_4  =  CalcNDCG(carouse2clicked,carouse2pred_FT_noMF)
	print 'FT: ', score_4 , '   relative : ', score_1*1.0/score_4
	#######################
	 

	##########################
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\TLC\FT.MFSVD.small.valid.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		mode_dup = False,
		score_idx=4
	)
	carouse2pred_FT_mfsvd = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_4  =  CalcNDCG(carouse2clicked,carouse2pred_FT_mfsvd)
	print 'FT_mfsvd: ', score_4 , '   relative : ', score_1*1.0/score_4
	
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\TLC\LR.MFSVD.small.valid.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		mode_dup = False,
		score_idx=4
	)
	carouse2pred_LR_mfsvd = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	score_4  =  CalcNDCG(carouse2clicked,carouse2pred_LR_mfsvd)
	print 'LR_mfsvd: ', score_4 , '   relative : ', score_1*1.0/score_4
	
	carouse2pred41 = AvgPredictionArray(
	[carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly],
	[0.4,0.1,0.1,0.2,0.2,0.05],
	keep_special=True)
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'pos + MF + SVD2 + FT + svd_nosearch: ', score_41 , '   relative : ', score_1*1.0/score_41
	########################
	
	############## MyMediaLite #############
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\valid_output\valid_biasedMF.pred-it-20',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		value_idx=2
	)
	carouse2pred_mylite = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	scores  =  CalcNDCG(carouse2clicked,carouse2pred_mylite)
	print 'MyMediaLite 20: ', scores , '   relative : ', score_1*1.0/scores 
	
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\valid_output\valid.biasedMF.profile.pred-it-20',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		value_idx=2
	)
	carouse2pred_mylite_profile = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	scores  =  CalcNDCG(carouse2clicked,carouse2pred_mylite_profile)
	print 'MyMediaLite profile 20: ', scores , '   relative : ', score_1*1.0/scores 
	
		
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\valid_output\valid_svd++.pred-it-20',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		value_idx=2
	)
	carouse2pred_mylite_svd = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	scores  =  CalcNDCG(carouse2clicked,carouse2pred_mylite_svd)
	print 'MyMediaLite SVD++ 20: ', scores , '   relative : ', score_1*1.0/scores 
	
	################  my user/item based rec 
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\valid_output\valid_svd++.pred-it-20',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		value_idx=0
	)
	carouse2pred_mytiny01 = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	scores  =  CalcNDCG(carouse2clicked,carouse2pred_mytiny01)
	print 'Mytiny01: ', scores , '   relative : ', score_1*1.0/scores 
	
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\valid_output\valid_svd++.pred-it-20',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		value_idx=1
	)
	carouse2pred_mytiny02 = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	scores  =  CalcNDCG(carouse2clicked,carouse2pred_mytiny02)
	print 'Mytiny02: ', scores , '   relative : ', score_1*1.0/scores 
	
	
	##########  SVD ranking   
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeatureRanking\pred_ranking_valid_i100.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		value_idx=0
	)
	carouse2pred_ranking = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	scores  =  CalcNDCG(carouse2clicked,carouse2pred_ranking)
	print 'SVDRanking 100: ', scores , '   relative : ', score_1*1.0/scores 
		
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeatureRanking\pred_ranking_valid_i100_hassearch.txt',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_recovery.tsv',
		value_idx=0
	)
	carouse2pred_ranking0 = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	scores  =  CalcNDCG(carouse2clicked,carouse2pred_ranking0)
	print 'SVDRanking 100 has search: ', scores , '   relative : ', score_1*1.0/scores 
	
	
	carouse2pred41 = AvgPredictionArray(
	[carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly,carouse2pred_mylite,carouse2pred_mylite_svd],
	[0.45,0.1,0.1,0.2,0.2,0.05,0.05,0.05]) # [0.4,0.15,0.15,0.15,0.15]
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'pos+MF+...+MyMLite&svd:  ', score_41 , '   relative : ', score_1*1.0/score_41
	
	carouse2pred41 = AvgPredictionArray(
	[carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4],
	[0.5,0.1,0.1,0.2,0.2,0.05,0.05,0.05,0.1]) # [0.4,0.15,0.15,0.15,0.15]
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'pos+MF+...+MyMLite&svd+s4:  ', score_41 , '   relative : ', score_1*1.0/score_41
	
	
	carouse2pred41 = AvgPredictionArray(
	[carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly,carouse2pred_pop,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4,carouse2pred_ranking],
	[0.5,0.1,0.1,0.2,0.2,0.05,0.05,0.075,0.075,0.1,0.075]) # [0.4,0.15,0.15,0.15,0.15]
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'ALL asc:  ', score_41 , '   relative : ', score_1*1.0/score_41
	
	carouse2pred41 = AvgPredictionArray(
	[carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly,carouse2pred_pop_desc,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4,carouse2pred_ranking],
	[0.5,0.1,0.1,0.2,0.2,0.05,0.05,0.075,0.075,0.1,0.075]) # [0.4,0.15,0.15,0.15,0.15]
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'ALL desc  ', score_41 , '   relative : ', score_1*1.0/score_41	
	############## BEST  ##########
	'''
	carouse2pred41 = AvgPredictionArray([carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly,carouse2pred_pop],[0.45,0.1,0.1,0.2,0.2,0.05,0.05]) # [0.4,0.15,0.15,0.15,0.15]
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'Best so far: ', score_41 , '   relative : ', score_1*1.0/score_41
	
	
	carouse2pred41 = AvgPredictionArray(
	[carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly,carouse2pred_pop,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4],
	[0.5,0.1,0.1,0.2,0.2,0.05,0.05,0.075,0.075,0.1]) # [0.4,0.15,0.15,0.15,0.15]
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'Best so far: ', score_41 , '   relative : ', score_1*1.0/score_41
	'''
	carouse2pred41 = AvgPredictionArray(
	[carouse2pred,carouse2pred4,carouse2pred_svd,carouse2pred_svd_enrich,carouse2pred_FTwithMF,carouse2pred_svd_posonly,carouse2pred_pop,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4,carouse2pred_ranking],
	[0.5,0.1,0.1,0.2,0.2,0.05,0.05,0.075,0.075,0.1,0.075]) # [0.4,0.15,0.15,0.15,0.15]
	score_41  =  CalcNDCG(carouse2clicked,carouse2pred41)
	print 'Best so far: ', score_41 , '   relative : ', score_1*1.0/score_41
	
def AvgPrediction(carouse2pred,carouse2pred2):
	res = dict()
	for carouse in carouse2pred:
		res[carouse] = dict()
		dict1 = carouse2pred[carouse]
		dict2 = carouse2pred2[carouse]
		len1 = len(dict1)
		len2 = len(dict2)
		if (len1 != len2):
			print 'len1 <> len2'
		item2rank = dict()
		
		for idx,id in dict1.items():
			if idx == 1: ##-- 1
				item2rank[id]=-100
			else:
				item2rank[id]=idx*0.6 ##--
		for idx,id in dict2.items():
			item2rank[id] += idx * 0.4
		
		item_rank_list = list()
		for item,rank in item2rank.items():
			item_rank_list.append([item,rank])
		item_rank_list = sorted(item_rank_list, cmp= lambda x,y: 1 if x[1]-y[1]>0 else -1)
		#print item_rank_list
		for i in range(len(item_rank_list)):
			res[carouse][i] = item_rank_list[i][0]
	return res

def AvgPredictionArray(carouse2preds,weights, keep_special = True):
	res = dict()
	base_predictor_len = len(carouse2preds)
	
	for carouse in carouse2preds[0]:
		res[carouse] = dict()
		dict1 = carouse2preds[0][carouse]
				 
		item2rank = dict() 
		
		for idx,id in dict1.items():
			if keep_special:
				if idx == 1 : ##-- 1
					item2rank[id]=-1 #-100  #-2
				elif idx == 0:
					item2rank[id]=0
				else:
					item2rank[id]=idx*weights[0] ##--
			else:				
				item2rank[id]=idx*weights[0] ##--
				
		for i in range(1,base_predictor_len):			
			for idx,id in carouse2preds[i][carouse].items():
				item2rank[id] += idx * weights[i]
		
		item_rank_list = list()
		for item,rank in item2rank.items():
			item_rank_list.append([item,rank])
		item_rank_list = sorted(item_rank_list, cmp= lambda x,y: 1 if x[1]-y[1]>0 else -1)
		#print item_rank_list
		for i in range(len(item_rank_list)):
			res[carouse][i] = item_rank_list[i][0]
	return res

	
def PrepareSubmission():
	trainfile = r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv'
	testfile = r'D:\competitions\MS_RecSys\data\hackathon-test-data.csv'
	outfile = r'D:\competitions\MS_RecSys\data\my\submission\ensemble.csv'
	start_date = datetime.datetime(2015,12,10)
	end_date = datetime.datetime(2016,3,14)
	
	#item2clickcnt = StatItemPopularity(trainfile,start_date,end_date,weighted=True,outfile=r'D:\competitions\MS_RecSys\data\my\item_click_weighted_cnt_20151210_20160314.csv')
	item2clickcnt = LoadItemClickcnt(r'D:\competitions\MS_RecSys\data\my\item_click_weighted_cnt_20151210_20160314.csv',value_idx=1)	
	
	
	carouse2pred = PredictByPosition(
		r'D:\competitions\MS_RecSys\data\hackathon-test-data.csv',
		carouse_idx = 4, position_idx = 5, sid_idx = 6, hasheader=True
		)
	
	'''	
	carouse2pred2 = AdjustByPopulairty(carouse2pred,item2clickcnt)	
	ensemble = AvgPrediction(carouse2pred,carouse2pred2)
	'''
	
	########### popularity 
	carouse2pred_pop = AdjustByPopulairty(carouse2pred,item2clickcnt)
	
	
	########### MF
	refer_file = r'D:\competitions\MS_RecSys\data\my\features\mapped\prediction_recovery.tsv'
	carouse2user = LoadCarousel2User(testfile)
	rec_helper = RecFactory()	
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\tlc\0.inst.submit.txt',
		#r'D:\competitions\MS_RecSys\data\my\features\product\prediction.tsv',
		refer_file,
		mode_dup = False
	)	 
	carouse2predMF = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	############### SVD 2
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\pred_128_submit.txt',
		refer_file
	)
	carouse2predSVD = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\pred_enrich_d128_ite50_submit.txt',
		refer_file
	)
	carouse2predSVD_enrich = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	################ FT
	user_item_score = rec_helper.LoadTLCMFResult(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\TLC\FT.small.submit.txt',
		#r'D:\competitions\MS_RecSys\data\my\features\product\prediction.tsv',
		refer_file,
		mode_dup = False
	)	 
	carouse2predFT = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	
	############  svd no search
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\pos_only\pred_enrich_128_submit.txt',
		refer_file
	)
	carouse2pred_svd_nosearch = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	 
	########### SVD feature search 4 
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature_search4\pred_128_enrich_s4_submit_i100.txt',
		refer_file
	)
	carouse2pred_svd_enrich_search4 = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	
	########  My media lite
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\submit_output\submit.pred-it-20',
		refer_file,
		value_idx=2
	)
	carouse2pred_mylite = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\submit_output\submit_SVD++.pred-it-20',
		refer_file,
		value_idx=2
	)
	carouse2pred_mylite_svd = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	######### ranking 
	user_item_score = rec_helper.LoadSVDFeatureResult(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeatureRanking\pred_ranking_submit_i100.txt',
		refer_file,
		value_idx=0
	)
	carouse2pred_ranking = AdjustByMFPred(carouse2pred,carouse2user,user_item_score)
	
	ensemble = AvgPredictionArray([carouse2pred,carouse2predMF,carouse2predSVD,carouse2predSVD_enrich,carouse2predFT,carouse2pred_svd_nosearch,carouse2pred_pop,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4,carouse2pred_ranking],[0.5,0.1,0.1,0.2,0.2,0.05,0.1,0.075,0.075,0.1,0.075]) 	
	#           AvgPredictionArray([carouse2pred,carouse2predMF,carouse2predSVD,carouse2predSVD_enrich,carouse2predFT],[0.4,0.15,0.15,0.15,0.15])
	#Best 2016-06-26	AvgPredictionArray([carouse2pred,carouse2predMF,carouse2predSVD,carouse2predSVD_enrich,carouse2predFT,carouse2pred_svd_nosearch,carouse2pred_pop],[0.4,0.1,0.1,0.2,0.2,0.05,0.05]) 
	#Best 2016-06-26 0.5675    AvgPredictionArray([carouse2pred,carouse2predMF,carouse2predSVD,carouse2predSVD_enrich,carouse2predFT,carouse2pred_svd_nosearch,carouse2pred_pop,carouse2pred_mylite],[0.45,0.1,0.1,0.2,0.2,0.05,0.05,0.075]) 
	#0.569327  AvgPredictionArray([carouse2pred,carouse2predMF,carouse2predSVD,carouse2predSVD_enrich,carouse2predFT,carouse2pred_svd_nosearch,carouse2pred_pop,carouse2pred_mylite,carouse2pred_mylite_svd],[0.45,0.1,0.1,0.2,0.2,0.05,0.05,0.075,0.075]) 
	#0.570611  AvgPredictionArray([carouse2pred,carouse2predMF,carouse2predSVD,carouse2predSVD_enrich,carouse2predFT,carouse2pred_svd_nosearch,carouse2pred_pop,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4],[0.5,0.1,0.1,0.2,0.2,0.05,0.05,0.075,0.075,0.1]) 
	#0.570869  AvgPredictionArray([carouse2pred,carouse2predMF,carouse2predSVD,carouse2predSVD_enrich,carouse2predFT,carouse2pred_svd_nosearch,carouse2pred_pop,carouse2pred_mylite,carouse2pred_mylite_svd,carouse2pred_svd_enrich_search4,carouse2pred_ranking],[0.5,0.1,0.1,0.2,0.2,0.05,0.05,0.075,0.075,0.1,0.075]) 	
	
	WriteSubmisionFile(ensemble,testfile,outfile)

	
def CountBasicStatistics(infile,outfile):
	search_log_set = set()
	carousel_log_set = set()
	
	date2carouselcnt = dict()
	date2searchcnt = dict()
	
	rd = open(infile,'r')	
	pos2clickcnt = dict()	
	pos2showcnt = dict()
	rd.readline()	
	cnt=0
	while True:
		line = rd.readline()
		if not line :
			break
		cnt+=1
		if cnt % 100000 == 0:
			print cnt 
			
		#if cnt > 1000000 :
		#	break ##--
		
		words = line[:-1].split(',')
		
		event_type = words[3].lower() 
		
		log_id = words[0]+':'+words[1]
		
		curtime = datetime.datetime.strptime(words[2],"%Y-%m-%d %H:%M:%S")
		cur_date_str = curtime.strftime('%Y-%m-%d')
		
		if event_type == 'carousel': 
			
			click = int(words[6])
			if True:
				position =  int(words[5])
				if position in pos2clickcnt:
					pos2clickcnt[position]+=click
					pos2showcnt[position]+=1
				else:
					pos2clickcnt[position]=click
					pos2showcnt[position]=1
			if not log_id in carousel_log_set:		
				carousel_log_set.add(log_id)
				if not cur_date_str in date2carouselcnt:
					date2carouselcnt[cur_date_str]=1 
				else:
					date2carouselcnt[cur_date_str]+=1
		else:
			if not log_id in search_log_set:
				search_log_set.add(log_id)
				if not cur_date_str in date2searchcnt:
					date2searchcnt[cur_date_str]=1 
				else:
					date2searchcnt[cur_date_str]+=1
				
	
	rd.close()
	
	pos2ctr = dict()
	for position in pos2showcnt:
		pos2ctr[position] = pos2clickcnt[position]*1.0/pos2showcnt[position]
	
	wt = open(outfile,'w')
	wt.write('position,ctr,showcnt\n')
	for position,ctr in pos2ctr.items():
		wt.write('%d,%f,%d\n' %(position,ctr,pos2showcnt[position]))
	
	wt.write('date,searchcnt,carouselcnt\n')
	for date,cnt in date2searchcnt.items():
		carouselcnt = date2carouselcnt[date] if date in date2carouselcnt else 0 
		wt.write('%s,%d,%d\n' %(date,cnt,carouselcnt))
	
	
	
	wt.close()
	
	return  pos2ctr
	

def StatUserItemShowCnt(infile,outfile_user,outfile_item)	:
	user2cnt = dict()
	item2cnt = dict()
	
	rd = open(infile,'r')
	rd.readline()
	cnt = 0 
	while True:	
		line = rd.readline()
		if not line:
			break 
		cnt+=1 
		if cnt % 100000 == 0:
			print cnt 
			#break
		words = line[:-1].split(',')
		if not words[0] in user2cnt:
			user2cnt[words[0]]=1 
		else:
			user2cnt[words[0]]+=1 
		if not words[1] in item2cnt:
			item2cnt[words[1]]=1 
		else:
			item2cnt[words[1]]+=1 
	rd.close()
	
	WriteFile(outfile_user,user2cnt)
	WriteFile(outfile_item,item2cnt)


	
def WriteFile(outfile, id2cnt):
	wt = open(outfile,'w')
	wt.write('id,cnt\n')
	for id,value in id2cnt.items():
		wt.write(str(id)+','+str(value)+'\n')
	wt.close()
	
if __name__ == '__main__':

	'''
	start_date = datetime.datetime(2016,3,10)
	end_date = datetime.datetime(2016,3,15)	
	SelectValidSet(r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-test-users.csv',r'D:\competitions\MS_RecSys\data\my\ValidSet_testusers.csv',start_date,end_date)
	'''	
	
	
	'''
	PredctByPopularity(r'D:\competitions\MS_RecSys\data\hackathon-test-data.csv',
		r'D:\competitions\MS_RecSys\data\my\item_popularity_pred.csv',
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		datetime.datetime(2015,12,10),
		datetime.datetime(2016,3,14)
		)
	'''
	
	
	
	
	'''
	PrepareSubmission()
	'''
	
	'''
	StatPositionClickCount(
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		r'D:\competitions\MS_RecSys\data\my\position_ctr.csv'
	)
	'''