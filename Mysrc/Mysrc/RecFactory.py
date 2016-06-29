import datetime
import random
import math
from IDTransformers import *

class MyTinyRecEngine(object):
	'''
	knn implementation
	'''
	def __init__(self):
		self.item2userset = dict()
		self.user2itemset = dict() 
		self.debug = True
		self.user2posset = dict()
		self.user2negset = dict()
		self.user2searchset = dict()
	
	def WriteTrianFile4Ranking(self,outfile):
		user2neglist = dict()
		user2searchlist = dict()
		for uid,s in self.user2negset.items():
			user2neglist[uid]=list(s)
		for uid,s in self.user2searchset.items():
			user2searchlist[uid]=list(s)	
			
		wt = open(outfile,'w')
		for uid,s in self.user2posset.items():
			for iid in s:
				
				if uid in user2searchlist:
					idx = random.randrange(0,len(user2searchlist[uid]))
					wt.write('0.5 0 1 2 %s:1 %s:1 %s:-1\n' %(uid,iid,user2searchlist[uid][idx]))
				
				if uid in user2neglist:
					idx = random.randrange(0,len(user2neglist[uid]))
					wt.write('1.0 0 1 2 %s:1 %s:1 %s:-1\n' %(uid,iid,user2neglist[uid][idx]))
				if uid in user2neglist and uid in user2searchlist:
					idx01 = random.randrange(0,len(user2searchlist[uid]))
					idx02 = random.randrange(0,len(user2neglist[uid]))
					wt.write('0.5 0 1 2 %s:1 %s:1 %s:-1\n' %(uid,user2searchlist[uid][idx01],user2neglist[uid][idx02]))
		wt.close()
	
	def WriteTestFile4Ranking(self,infile,outfile):
		rd = open(infile,'r')
		wt = open(outfile,'w')
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			score = words[0]
			uid = words[1]
			iid = words[2]
			wt.write('1.0 0 1 1 %s:1 %s:1\n' %(uid,iid))
		wt.close()
		rd.close()
		
	def LoadRatings(self,infile):
		rd = open(infile,'r')
		self.item2userset = dict()
		self.user2itemset = dict() 
		cnt = 0 
		while True:
			line = rd.readline()
			if not line:
				break 
			cnt +=1 
			if cnt%10000 == 0 :
				print cnt 
			words = line[:-1].split('\t')
			score = words[0]
			uid = words[1]
			iid = words[2]
			if score == '5':
				if not iid in self.item2userset:
					self.item2userset[iid]=set()
				self.item2userset[iid].add(uid)
				if not uid in self.user2itemset:
					self.user2itemset[uid]=set()
				self.user2itemset[uid].add(iid)
				
				if not uid in self.user2posset:
					self.user2posset[uid]= set()
				self.user2posset[uid].add(iid)
			elif score =='0':
				if not uid in self.user2negset:
					self.user2negset[uid]= set()
				self.user2negset[uid].add(iid)
			else:
				if not uid in self.user2searchset:
					self.user2searchset[uid]= set()
				self.user2searchset[uid].add(iid)
				
		rd.close()
	
	def PredictItemBasedScore(self,uid,iid, k):
		if not iid in self.item2userset or not uid in self.user2itemset:
			return 0 
		item_sim_list = []
		history_item_set = self.user2itemset[uid]
		for history_item in history_item_set:
			item_sim_list.append([history_item,self.CalcSim(self.item2userset[history_item],self.item2userset[iid])])
		item_sim_list.sort(cmp = lambda x,y: 1 if y[1]>x[1] else -1 if y[1]!=x[1] else 0)
		score = 0  
		cnt = min(len(item_sim_list),k) 
		for i in range(cnt):
			score += item_sim_list[i][1] 
		score /= cnt 
		return score 
		
	def PredictUserBasedScore(self,uid,iid, k):
		if not iid in self.item2userset or not uid in self.user2itemset:
			return 0 
		user_sim_list = []
		history_user_set = self.item2userset[iid]
		for history_user in history_user_set:
			user_sim_list.append([history_user,self.CalcSim(self.user2itemset[history_user],self.user2itemset[uid])])
		user_sim_list.sort(cmp = lambda x,y: 1 if y[1]>x[1] else -1 if y[1]!=x[1] else 0)
		if self.debug:
			self.debug = False 
			print user_sim_list
		score = 0  
		cnt = min(len(user_sim_list),k) 
		for i in range(cnt):
			score += user_sim_list[i][1] 
		score /= cnt 
		return score 
			
	def CalcSim(self, set01,set02):
		cnt = 0 
		for id in set01:
			if id in set02:
				cnt +=1 
		return cnt*1.0/math.sqrt(len(set01)*len(set02))
		
	def PredictFile(self,infile,outfile):
		rd = open(infile,'r')
		wt = open(outfile,'w')
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			uid = words[1]
			iid = words[2] 
			score01 = self.PredictUserBasedScore(uid,iid,10)
			score02 = self.PredictItemBasedScore(uid,iid,10)
			wt.write('%f\t%f\n' %(score01,score02))
		wt.close()
		rd.close()
		
class RecFactory(object):
	
	## 2016-06-27  for search measurement 2
	def ExtractUserItemRatingsMapped(self,infile,outfile,start_date,end_date,negative_ratio,search_ratio):
		
		search_score = 1
		
		idhelper = IDTransformers();
		userid2mapid , _ = idhelper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\IdMap\user_mapid.csv')
		itemid2mapid , _ = idhelper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\IdMap\item_mapid.csv')
		
		print 'usercnt','\t',str(len(userid2mapid))
		
		
		rd = open(infile,'r')
		
		rd.readline()
		cnt = 0

		user_item_rating = dict()
		
		while True:
			line = rd.readline()
			if not line:
				break
			cnt+=1
			if cnt % 100000 == 0:
				print cnt
				
			#if cnt > 500000	:
			#	break
				
			words = line[:-1].split(',')	 
			
			userid = words[0]
			itemid = words[1]
			
			if not userid in userid2mapid or not itemid in itemid2mapid :
				continue 
			
			userid = userid2mapid[userid]
			itemid = itemid2mapid[itemid]
			
			curtime = datetime.datetime.strptime(words[2],'%Y-%m-%d %H:%M:%S')
			if curtime < start_date or curtime >= end_date:
				continue
			
			event_type = words[3].lower()
			
			
			if event_type == 'carousel':
				rating = int(words[6]) * 5				
			else:
				rating = search_score 
				#continue
				
			if not userid in user_item_rating:
				user_item_rating[userid]=dict()
			if not itemid in user_item_rating[userid]:
				user_item_rating[userid][itemid]=rating 
			else:
				if rating > user_item_rating[userid][itemid]:
					user_item_rating[userid][itemid] = rating
					
		rd.close()
		
		wt = open(outfile,'w')
		
		for userid in user_item_rating:
			for itemid,rating in user_item_rating[userid].items():
				ran_r = random.random()
				if rating > search_score or (rating == 0 and ran_r<negative_ratio) or (rating ==search_score and ran_r<search_ratio):
					wt.write('%d\t%s\t%s\n' %(rating,userid,itemid))
		
		wt.close()
	
	def ExtractUserItemRatings(self,infile,outfile,start_date,end_date,negative_ratio,search_ratio):
		'''
		id_helper = IDTransformers()
		userid2mapid, _ = id_helper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\user_mapid.csv')
		itemid2mapid, _ = id_helper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\item_mapid.csv')
		
		print 'usercnt','\t',str(len(userid2mapid))
		'''
		
		rd = open(infile,'r')
		
		rd.readline()
		cnt = 0

		user_item_rating = dict()
		
		while True:
			line = rd.readline()
			if not line:
				break
			cnt+=1
			if cnt % 100000 == 0:
				print cnt
				
			#if cnt > 500000	:
			#	break
				
			words = line[:-1].split(',')			
			'''
			userid = userid2mapid[words[0]]
			itemid = itemid2mapid[words[1]]
			'''
			userid = words[0]
			itemid = words[1]
			
			curtime = datetime.datetime.strptime(words[2],'%Y-%m-%d %H:%M:%S')
			if curtime < start_date or curtime >= end_date:
				continue
			
			event_type = words[3].lower()
			
			
			if event_type == 'carousel':
				rating = int(words[6]) * 5				
			else:
				rating = 3 
				#continue
				
			if not userid in user_item_rating:
				user_item_rating[userid]=dict()
			if not itemid in user_item_rating[userid]:
				user_item_rating[userid][itemid]=rating 
			else:
				if rating > user_item_rating[userid][itemid]:
					user_item_rating[userid][itemid] = rating
					
		rd.close()
		
		wt = open(outfile,'w')
		
		for userid in user_item_rating:
			for itemid,rating in user_item_rating[userid].items():
				ran_r = random.random()
				if rating > 3 or (rating == 0 and ran_r<negative_ratio) or (rating ==3 and ran_r<search_ratio):
					wt.write('%d\t%s\t%s\n' %(rating,userid,itemid))
		
		wt.close()
		
	def LoadTLCMFResult(self,instfile,rawfile,mode_dup=False,score_idx=2):
		user_item_score = dict()
		rd_pred = open(instfile,'r')
		rd_raw = open(rawfile,'r')
		rd_pred.readline()
		
		while True:
			line = rd_pred.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			score = float(words[score_idx])
			
			if mode_dup:
				if rd_pred.readline()[:-1].split('\t')[1]!= '0':
					print 'error : is duplicate mode?'
			
			line = rd_raw.readline()
			words = line[:-1].split('\t')
			
			userid = words[1]
			itemid = words[2]
			
			if not userid in user_item_score:
				user_item_score[userid] = dict()
			user_item_score[userid][itemid] = score
		
		rd_pred.close()
		rd_raw.close()
		
		return user_item_score
	
	def LoadSVDFeatureResult(self,svdresultfile,rawfile,value_idx = 0):
		user_item_score = dict()
		rd_pred = open(svdresultfile,'r')
		rd_raw = open(rawfile,'r')
		
		while True:
			line = rd_pred.readline()
			if not line:
				break 
			word = line[:-1].split('\t')[value_idx]
			score = float(word)
			 
			line = rd_raw.readline()
			words = line[:-1].split('\t')
			
			userid = words[1]
			itemid = words[2]
			
			if not userid in user_item_score:
				user_item_score[userid] = dict()
			user_item_score[userid][itemid] = score
		
		rd_pred.close()
		rd_raw.close()
		
		return user_item_score
	
	def ExtractUserItemRatingsFromTestFile(self,infile,outfile):
		rd = open(infile,'r')
		wt= open(outfile,'w')
		rd.readline()
		
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split(',')
			wt.write('0\t'+words[1]+'\t'+words[6]+'\n')
			
		wt.close()
		rd.close()
		
	def SelectPostiveInstanceOnly(self,infile,outfile,test_mode=False):
		rd = open(infile,'r')
		wt = open(outfile,'w')
		
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			if words[0]=='5':
				wt.write('1\t%s\t%s\n' %(words[1],words[2]))
			if words[0]=='0' and test_mode:
				wt.write('0\t%s\t%s\n' %(words[1],words[2]))
		
		wt.close()
		rd.close()
	
	def Format2LibMF(self,infile,outfile):
		rd = open(infile,'r')
		wt = open(outfile,'w')
		while True:
			line = rd.readline()
			if not line:
				break
			words = line[:-1].split('\t')
			wt.write('%s %s %s\n' %(words[1],words[2],words[0]))
		wt.close()
		rd.close()
	
	def FormatAttributeFileMyMediaLite(self,profile,outfile):
		'''
		generate attribute file for MyMediaLite
		'''
		feature_len = 0 
		cnt=1000
		for uid,dic in profile.items():
			c_len = len(dic)
			if c_len>feature_len:
				feature_len=c_len
			cnt-=1
			if cnt<=0:
				break 
		wt = open(outfile,'w')
		for key,features in profile.items():
			for fe,fv in features.items():
				if fv>=1:
					wt.write('%s\t%s\n' %(key,fe))
		wt.close()
		
	def Format2ItemRecommendationMyMLite(self,infile,outfile):
		user2itemscore = dict()
		rd = open(infile,'r')
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('::')
			uid = words[0]
			iid = words[1]
			score = words[2]
			if not uid in user2itemscore:
				user2itemscore[uid]=[]
				
			user2itemscore[uid].append(iid+':'+score)
			
		rd.close()
		
		wt = open(outfile,'w')
		for uid,ul in user2itemscore.items():
			wt.write('%s\t[%s]\n' %(uid,','.join(ul)))
		wt.close()
	
	def Format2SVDFeature(self,infile,outfile):
		rd = open(infile,'r')
		wt = open(outfile,'w')
		while True:
			line = rd.readline()
			if not line:
				break
			words = line[:-1].split('\t')
			wt.write('%s 0 1 1 %s:1 %s:1\n' %(words[0],words[1],words[2]))
		wt.close()
		rd.close()
	
	def Format2ClassificationFeature(self,infile,outfile,userprofile,itemprofile,MFpredfile,SVDpredfile01,SVDpredfile02):
		'''
		generate featured file for classification
		the output format is :   label,id,MF_score,SVD_score,SVD_Score2,many_user_features,many_item_features
		'''
		rd01 = open(infile,'r')
		rd02 = open(MFpredfile,'r')
		rd02.readline()
		
		rd_svd01 = open(SVDpredfile01,'r')
		rd_svd02 = open(SVDpredfile02,'r')
		
		wt = open(outfile,'w')
		
		user_feature_len = 0 
		item_feature_len = 0 
		for uid,dic in userprofile.items():
			user_feature_len = len(dic)
			break 
		for iid,dic in itemprofile.items():
			item_feature_len = len(dic) 
			break 
		print 'user feature len: ', user_feature_len
		print 'item feature len: ', item_feature_len
		
		wt.write('label,id,mfscore,svdscore01,svdscore02')
		for i in range(user_feature_len):
			wt.write(',uf'+str(i))
		for i in range(item_feature_len):
			wt.write(',if'+str(i))
		wt.write('\n')
		
		while True:	
			line = rd01.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			userid = words[1]
			itemid = words[2]
			label = words[0] 
			
			line = rd02.readline()
			MF_score = line[:-1].split('\t')[2]
			
			line_svd01 = rd_svd01.readline()[:-1]
			line_svd02 = rd_svd02.readline()[:-1]
			
			if label == '5':
				label = '1'
			if label =='0' or label == '1':
				wt.write(label+','+userid+':'+itemid+','+MF_score+','+line_svd01+','+line_svd02)
				if userid in userprofile and len(userprofile[userid])==user_feature_len:
					for idx,value in userprofile[userid].items():
						wt.write(','+str(value))
				else:
					for i in range(user_feature_len):
						wt.write(',0')
						
				if itemid in itemprofile and len(itemprofile[itemid])==item_feature_len:
					for idx,value in itemprofile[itemid].items():
						wt.write(','+str(value))
				else:
					for i in range(item_feature_len):
						wt.write(',0')
				
				wt.write('\n')
				
		
		wt.close()
		rd02.close()
		rd01.close()
		rd_svd01.close()
		rd_svd02.close()
	
	def Format2SVDFeature2(self,infile,outfile,userprofile,itemprofile):	
		'''
		generate SVDFeature file format with user/item profile 
		'''
		print 'formatting ', infile 
		rd = open(infile,'r')
		wt = open(outfile,'w')
		cnt = 0 
		while True:
			line = rd.readline()
			if not line:
				break
			cnt += 1 
			if cnt % 10000 == 0:
				print cnt
			words = line[:-1].split('\t')
			userfeature=words[1]+':1'
			userfeaturecnt = 1
			if words[1] in userprofile:
				for idx,value in userprofile[words[1]].items():
					if value>0:
						userfeaturecnt+=1
						userfeature+=' '+str(500000+idx)+':'+str(value)
			itemfeature=words[2]+':1'
			itemfeaturecnt = 1
			if words[2] in itemprofile:
				for idx,value in itemprofile[words[2]].items():
					if value>0:
						itemfeaturecnt+=1 
						itemfeature+=' '+str(60000+idx)+':'+str(value)
			wt.write('%s 0 %d %d %s %s\n' %(words[0],userfeaturecnt,itemfeaturecnt,userfeature,itemfeature))
		wt.close()
		rd.close()
			
	def LoadMappedUserItemProfile(self,userdemofile,userqasfile,itemprofile):
		idhelper = IDTransformers();
		useridmap , _ = idhelper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\IdMap\user_mapid.csv')
		itemidmap , _ = idhelper.LoadIdAndMapId(r'D:\competitions\MS_RecSys\data\my\IdMap\item_mapid.csv')
		
		user2featuredict = dict()
		
		#####  loading user profile
		print 'loading user demo profile...'
		rd = open(userdemofile,'r')
		rd.readline()
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split(',')
			if not words[0] in useridmap:
				continue
			mapped_userid = useridmap[words[0]]
			
			if not mapped_userid in user2featuredict:
				user2featuredict[mapped_userid]=dict()
			for i in range(0,7):
				if len(words[i+1])<=0 or 'NULL' in words[i+1]: 
					continue
				user2featuredict[mapped_userid][i]=float(words[i+1])
		rd.close()
		
		print 'loading user qas profile...'
		rd = open(userqasfile,'r')
		headers = rd.readline()[:-1].split(',')
		col_cnt = len(headers)
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
			if not words[0] in useridmap:
				continue
			mapped_userid = useridmap[words[0]]
			
			if not mapped_userid in user2featuredict:
				user2featuredict[mapped_userid]=dict()
			for i in range(1,col_cnt-1):
				if len(words[i])<=0 or 'NULL' in words[i]: 
					continue
				cvalue = float(words[i]) 
				if cvalue>1:
					cvalue = 1
				user2featuredict[mapped_userid][6+i]=cvalue
		rd.close()
		#####  finish loading user profile
	  	
		
	 
		print 'loading item profile...'
		item2featuredict = dict()
		
		rd = open(itemprofile,'r')
		headers = rd.readline()[:-1].split(',')
		col_cnt = len(headers)
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split(',')
			if not words[0] in itemidmap:
				continue
			mapped_itemid = itemidmap[words[0]]
			
			if not mapped_itemid in item2featuredict:
				item2featuredict[mapped_itemid]=dict()
			for i in range(0,col_cnt-1):
				if len(words[i+1])<=0 or 'NULL' in words[i+1]: 
					continue
				item2featuredict[mapped_itemid][i]=float(words[i+1])
		rd.close()
		 
		return user2featuredict,item2featuredict
	
	def Split2TrainTest(self,infile,outfile01,outfile02):
				
		rd = open(infile,'r')
		wt01 = open(outfile01,'w')
		wt02 = open(outfile02,'w')
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			if random.random()<0.8:
				wt01.write(line)
			else:
				wt02.write(line)
		wt02.close()
		wt01.close()
		rd.close()
		
	def ReplaceSearchScore(self,infile,outfile,pre_score='1',new_score='4'):
		rd = open(infile,'r')
		wt = open(outfile,'w')
		cnt = 0 
		while True:
			line = rd.readline()
			if not line:
				break 
			cnt+=1 
			if cnt % 10000 == 0 :
				print cnt 
			words = line[:-1].split(' ')
			value = words[0]
			if value == pre_score:
				words[0] = new_score
				
			wt.write(' '.join(words)+'\n')	
		wt.close()
		rd.close()
		
	def RemoveSearchInstances(self,infile,outfile):
		'''
		remove search records in infile  
		search records has a score of '3' 
		outfile only contains click and unclick records with score 1 and o separately 
		'''
		rd = open(infile,'r')
		wt = open(outfile,'w')
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split(' ')
			value = words[0]
			if value == '3':
				continue
			if value == '5':
				words[0] = '1'
			wt.write(' '.join(words)+'\n')	
		wt.close()
		rd.close()
		
	def Format2PosOnlyFile(self,infile,outfile,test_mode=False):		
		rd = open(infile,'r')
		wt = open(outfile,'w')
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('::')
			uid = words[0]
			iid = words[1]
			score = words[2]
			if score =='5' or test_mode:
				wt.write('%s\t%s\n' %(uid,iid))
		wt.close()		
		rd.close()
	
	
		