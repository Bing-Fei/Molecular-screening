from requests import get
import pandas as pd
import json

'''
    用于第一次下载PubChemQC中的数据
    下载pccdb_id从1到1000的分子数据
'''

#下载pccdb_id从start到end(包括end)的分子的数据
def download(start,end,df = pd.DataFrame()):
    count = 0
    for pccdb_id in range(start,end+1):
        try:
            #使用get方法会返回一个包含了分子相关性质的json文件
            dataJson = get(f'http://pccdb.org/search_pubchemqc/get_basic_property/ver0.2/{pccdb_id}').text
        except Exception as err:
            print(f"{pccdb_id}",err)
            continue

        #处理一些异常情况
        if dataJson == 'null\n':continue #跳过空数据
        if '<h1>Too Many Requests</h1>' in dataJson:
            #今天的下载达到最大值
            print('maximum requests')
            return df
        
        #若无异常，则将新的数据添加到df中行末中
        dataDict = json.loads(dataJson)
        dataDataframe = pd.DataFrame(dataDict,index=[pccdb_id])
        df = pd.concat([df, dataDataframe], ignore_index=True) 
        print(f"{pccdb_id} downloaded")
        #每下一百条数据自动保存
        count +=1
        if count%100 == 0:   df.to_csv('data_raw.csv',index=False)
    return df

download(3046,3500,pd.read_csv('data_raw.csv')).to_csv('data_raw.csv',index=False)

# python是为伪多线程，使用多线程下载并不提速，因此下面的代码报废了 :(

# #创建一个列表存储结果
# threads_ret = [None]*10

# #多线程下载
# def thread_func(start,end,thread_No):
#     threads_ret[thread_No] = download(start,end)

# #创建十个线程进行下载，每个线程下载100条数据
# threads = [threading.Thread(target=thread_func,args=(i*100,(i+1)*100-1,i)) for i in range(0,10)]

# #开启线程
# for thread in threads:
#     thread.start()

# #等待线程结束
# for thread in threads:
#     thread.join()

# #拼接每一个线程的结果
# ret = pd.concat(threads_ret,ignore_index=True)

# #保存ret
# ret.to_csv('data.csv', index=False)