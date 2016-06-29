
class IDTransformers(object):
	
	
	def GenUserItemIdMap(self,testfile,usershowcntfile,itemshowcntfile,usermapfile,itemmapfile):	
		'''
			load <user,record_count> from usershowcntfile
			load <item,record_count> from itemshowcntfile
			filter out users and items whose record_count is less than 40 and not appear at all in test file 
			in the remaining user / item set, map the user_id/item_id into range [0, N] and output to id mapping relation to usermapfile/itemmapfile
		'''	
		userset,itemset = self.LoadTestUserItemIdSet(testfile)
		user2showcnt = self.LoadId2Cnt(usershowcntfile)
		item2showcnt = self.LoadId2Cnt(itemshowcntfile)
				 
		usercnt = 0
		itemcnt=0
		usermap = dict()
		itemmap = dict()
		  
		
		for userid,showcnt in user2showcnt.items():				  
			if userid in userset or showcnt>=40:
				usermap[userid]=usercnt				
				usercnt+=1
				
		for itemid,showcnt in item2showcnt.items():
			if itemid in itemset or showcnt>=40:
				itemmap[itemid]=itemcnt 
				itemcnt+=1 
		
		wt = open(usermapfile,'w')
		wt.write('id,mappedid\n')
		for userid,id in usermap.items():
			wt.write('%s,%d\n' %(userid,id))
		wt.close()
		
		wt = open(itemmapfile,'w')
		wt.write('id,mappedid\n')
		for itemid,id in itemmap.items():
			wt.write('%s,%d\n' %(itemid,id))
		wt.close()
		
	def LoadIdAndMapId(self,infile):
		id2mapid = dict()
		mapid2id = dict()
		
		rd = open(infile,'r')
		rd.readline()
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split(',')
			id2mapid[words[0]] = words[1]
			mapid2id[words[1]] = words[0]
		rd.close()
		return id2mapid, mapid2id

	def LoadId2Cnt(self,infile):
		id2cnt = dict()
		rd = open(infile,'r')
		rd.readline()
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split(',')
			id2cnt[words[0]]=int(words[1])
		rd.close()
		return id2cnt
	
	
	def LoadTestUserItemIdSet(self,infile):
		userset = set()
		itemset = set()
		rd = open(infile,'r')
		rd.readline()
		while True:	
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split(',')
			userset.add(words[1])
			itemset.add(words[6])
		rd.close()
		return userset,itemset
	
	
	
	def MapMapid2OriIds(self,infile,outfile,useridmapfile,itemidmapfile):
		'''
		change the mapped user id and item id from infile into original id 
		write the changed records into outfile
		'''
		_, useridmap   = self.LoadIdAndMapId(useridmapfile)
		_, itemidmap   = self.LoadIdAndMapId(itemidmapfile)
		
		rd = open(infile,'r')
		wt = open(outfile,'w')
		
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			
			if words[1] not in useridmap or words[2] not in itemidmap:
				continue 
			wt.write('%s\t%s\t%s\n' %(words[0],useridmap[words[1]],itemidmap[words[2]]))
		
		wt.close()
		rd.close()

	
	
	def MapOriId2Mapids(self,infile,outfile,useridmapfile,itemidmapfile):
		'''
		change the user id and item id from infile into mapped id 
		write the mapped records into outfile
		'''
		useridmap , _ = self.LoadIdAndMapId(useridmapfile)
		itemidmap , _ = self.LoadIdAndMapId(itemidmapfile)
		
		rd = open(infile,'r')
		wt = open(outfile,'w')
		
		while True:
			line = rd.readline()
			if not line:
				break 
			words = line[:-1].split('\t')
			
			if words[1] not in useridmap or words[2] not in itemidmap:
				continue 
			wt.write('%s\t%s\t%s\n' %(words[0],useridmap[words[1]],itemidmap[words[2]]))
		
		wt.close()
		rd.close()
	