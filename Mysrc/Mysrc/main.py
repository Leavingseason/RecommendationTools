
import datetime
from RecFactory import *
from IDTransformers import *
from EarlyJobs import *

'''

'''

if __name__ == '__main__':
	
	
	# ID mapping 
	IdTrans = IDTransformers()	
	'''
	IdTrans.GenUserItemIdMap(
		r'D:\competitions\MS_RecSys\data\hackathon-test-data.csv',
		r'D:\competitions\MS_RecSys\data\my\user2showcnt.csv',
		r'D:\competitions\MS_RecSys\data\my\item2showcnt.csv',
		r'D:\competitions\MS_RecSys\data\my\IdMap\user_mapid.csv',
		r'D:\competitions\MS_RecSys\data\my\IdMap\item_mapid.csv'
	) 	
	IdTrans.MapMapid2OriIds(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\prediction.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\prediction_recovery.tsv',
		r'D:\competitions\MS_RecSys\data\my\IdMap\user_mapid.csv',
		r'D:\competitions\MS_RecSys\data\my\IdMap\item_mapid.csv'
	) 
	IdTrans.MapOriId2Mapids(
		r'D:\competitions\MS_RecSys\data\my\features\product\user_item_ratings_train_20160315.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_train_20160315.tsv',
		r'D:\competitions\MS_RecSys\data\my\IdMap\user_mapid.csv',
		r'D:\competitions\MS_RecSys\data\my\IdMap\item_mapid.csv'
	) 
	'''
	
	
	#formatting for MyMediaLite 
	'''
	AppendTimestamp(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete_timestamp.tsv',
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		0,1,2,timeformat="%Y-%m-%d %H:%M:%S"
	)
	AppendTimestamp(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_train_20160310.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_train_20160310_timestamp.tsv',
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		0,1,2,timeformat="%Y-%m-%d %H:%M:%S"
	)	
	AppendTimestamp(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\prediction.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\prediction_timestamp.tsv',
		r'D:\competitions\MS_RecSys\data\hackathon-test-data.csv',
		1,6,3,timeformat="%m/%d/%Y"
	)
	AppendTimestamp(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_train_20160315.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_train_20160315_timestamp.tsv',
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		0,1,2,timeformat="%Y-%m-%d %H:%M:%S"
	)
	'''
	
	
	recFactory = RecFactory()
	
	'''
	recFactory.RemoveSearchInstances(
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\user_item_ratings_train_enrich.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature\pos_only\user_item_ratings_train_enrich.tsv'
	)
	''' 
	
	'''
	user_profile,item_profile = recFactory.LoadMappedUserItemProfile(
		r'D:\competitions\MS_RecSys\data\hackathon-user-profile-demographics.csv',
		r'D:\competitions\MS_RecSys\data\hackathon-user-profile-qas.csv',
		r'D:\competitions\MS_RecSys\data\hackathon-movie-profile.csv'
	) 	
	recFactory.FormatAttributeFileMyMediaLite(
		user_profile,
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\user_profile.dat'
	)
	recFactory.FormatAttributeFileMyMediaLite(
		item_profile,
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\RatingPrediction\bin\Debug\data\item_profile.dat'
	)
	'''
	
	'''
	recFactory.Format2ClassificationFeature(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part02.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part02_featured_MF_SVD2.csv',
		user_profile,item_profile,
		r'D:\competitions\MS_RecSys\data\my\features\tlc\0.instsmallset.part02.txt',
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature_traintest\pred_small_d128_ite50_part02.txt',
		r'D:\competitions\MS_RecSys\data\my\features\SVDFeature_traintest\pred_enrich_small_d128_ite50_part02.txt'
	)
	'''
	
	'''
	recFactory.Split2TrainTest(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_train_20160310.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part01.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part02.tsv'
	)
	'''
	
	'''
	recFactory.ExtractUserItemRatingsFromTestFile(
		r'D:\competitions\MS_RecSys\data\hackathon-test-data.csv',
		r'D:\competitions\MS_RecSys\data\my\features\product\prediction.tsv'
	)
	'''
	
	'''
	recFactory.Format2PosOnlyFile(
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\ItemRecommendation\bin\Debug\data\prediction_timestamp.tsv',
		r'D:\tools\recsys\MyMediaLite-master\MyMediaLite-master\src\Programs\ItemRecommendation\bin\Debug\data\prediction_timestamp_itemrec.tsv',
		test_mode=True
	)
	'''
	
	'''
	recFactory.Format2SVDFeature(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part01.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\SVDFeature\train-test\user_item_ratings_train_20160310_part01.tsv'
	)
	recFactory.Format2SVDFeature(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part02.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\SVDFeature\train-test\user_item_ratings_train_20160310_part02.tsv'
	)	 
	
	user_profile,item_profile = recFactory.LoadMappedUserItemProfile(
		r'D:\competitions\MS_RecSys\data\hackathon-user-profile-demographics.csv',
		r'D:\competitions\MS_RecSys\data\hackathon-user-profile-qas.csv',
		r'D:\competitions\MS_RecSys\data\hackathon-movie-profile.csv'
	)
	recFactory.Format2SVDFeature2(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part01.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\SVDFeatureWithProfile\train-test\user_item_ratings_train_20160310_part01.tsv',
		user_profile,item_profile
	)
	recFactory.Format2SVDFeature2(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\train-test\user_item_ratings_train_20160310_part02.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\SVDFeatureWithProfile\train-test\user_item_ratings_train_20160310_part02.tsv',
		user_profile,item_profile
	)
	'''
	 
	
	
	'''
	
	recFactory.SelectPostiveInstanceOnly(
		r'D:\competitions\MS_RecSys\data\my\features\user_item_ratings_train.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\user_item_ratings_train_posonly.tsv',
		test_mode=True
	)
	
	recFactory.SelectPostiveInstanceOnly(
		r'D:\competitions\MS_RecSys\data\my\features\user_item_ratings_test_complete.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\user_item_ratings_test_complete_posonly.tsv',
		test_mode=True
	)
	'''
	
	'''
	recFactory.ExtractUserItemRatings(
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		r'D:\competitions\MS_RecSys\data\my\features\product\user_item_ratings_train_20160310.tsv',
		datetime.datetime(2015,12,10), #2015,12,10
		datetime.datetime(2016,3,10),#2016,3,10
		negative_ratio=0.8,
		search_ratio = 0.1
	)
	''' 
	
	'''
	recFactory.ExtractUserItemRatings(
		r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',
		r'D:\competitions\MS_RecSys\data\my\features\product\user_item_ratings_train_20160315.tsv',
		datetime.datetime(2015,12,10), #2015,12,10
		datetime.datetime(2016,3,15),#2016,3,10
		negative_ratio=0.8,
		search_ratio = 0.1
	)
	'''
	
	 
	'''
	recFactory.ReplaceSearchScore(
		r'D:\competitions\MS_RecSys\data\my\features\mapped\search_1\SVDFeature\user_item_ratings_train_20160315_enrich.tsv',
		r'D:\competitions\MS_RecSys\data\my\features\mapped\search_1\SVDFeature\user_item_ratings_train_20160315_enrich_s4.tsv'
	) 	 
	'''

	
	'''
	myRecEngine =  MyTinyRecEngine()
	myRecEngine.LoadRatings(r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_train_20160310.tsv')
	myRecEngine.WriteTrianFile4Ranking(r'D:\competitions\MS_RecSys\data\my\features\SVDFeatureRanking\user_item_ratings_train_20160310.txt')
	myRecEngine.WriteTestFile4Ranking(r'D:\competitions\MS_RecSys\data\my\features\mapped\prediction.tsv',r'D:\competitions\MS_RecSys\data\my\features\SVDFeatureRanking\prediction.txt')
	myRecEngine.WriteTestFile4Ranking(r'D:\competitions\MS_RecSys\data\my\features\mapped\user_item_ratings_test_complete.tsv',r'D:\competitions\MS_RecSys\data\my\features\SVDFeatureRanking\user_item_ratings_test_complete.txt')
	
	'''
	
	
	ValidTest(
		datetime.datetime(2016,3,10),
		datetime.datetime(2016,3,11)
		)
	
	ValidTest(
		datetime.datetime(2016,3,11),
		datetime.datetime(2016,3,12)
		)
	ValidTest(
		datetime.datetime(2016,3,12),
		datetime.datetime(2016,3,13)
		)
	ValidTest(
		datetime.datetime(2016,3,13),
		datetime.datetime(2016,3,14)
		)
	ValidTest(
		datetime.datetime(2016,3,14),
		datetime.datetime(2016,3,15)
		)
	
	
	
	PrepareSubmission()
	
	
	'''
	CountBasicStatistics(r'D:\competitions\MS_RecSys\data\hackathon-click-search-train-data-all.csv',r'D:\competitions\MS_RecSys\data\my\basic_statistics.csv')
	'''
	