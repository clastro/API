##Naver papago API 호출

def get_translate(text):
    client_id = "****"
    client_secret = "****"

    data = {'text' : text,
            'source' : 'ko',
            'target': 'en'}

    
    url = "https://naveropenapi.apigw.ntruss.com/nmt/v1/translation"
    
    header = {"X-NCP-APIGW-API-KEY-ID":client_id,
             "X-NCP-APIGW-API-KEY":client_secret}

    response = requests.post(url, headers=header, data=data)
    rescode = response.status_code

    if(rescode==200):
        send_data = response.json()
        trans_data = (send_data['message']['result']['translatedText'])
        return trans_data
    else:
        print("Error Code:" , rescode)
        
##DataBase 연결

class FetchTable:
    
    def __init__(self,
                 host = "ip address",
                 port = "port number",
                 user = "user",
                 password = "password",
                 db = "db"):
        
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        
        conn  = pymysql.connect(host=self.host,
                                port=self.port,
                                user=self.user,
                                passwd=self.password,
                                db=self.db)  #데이터베이스 연결
        self.cursor = conn.cursor()
        conn.set_charset('utf8')
        
    def df_select_query(self,table):
        
        sql = "SELECT * FROM " + table 
        self.cursor.execute(sql)
        df_channel = pd.DataFrame(self.cursor.fetchall(),columns=[item[0] for item in self.cursor.description])
        
        return df_channel
    
    def df_insert_table(self,insert_df,table_name):
        
        engine = create_engine("mysql+mysqldb://"+self.user+":"+self.password+"@"+self.host+":"+str(self.port)+"/hifen?charset=utf8", encoding='utf-8')
        conn2 = engine.connect()
        insert_df.drop_duplicates().to_sql(name=table_name, con=engine, if_exists='append',index=False)
        conn2.close()
        
    
db_conn = FetchTable()
YT_channel_cate = db_conn.df_select_query('YT_video_lists')
YT_channel_cate2 = YT_channel_cate[YT_channel_cate['title'].str.len()>15]
YT_video_title = YT_channel_cate2[['title','video_id','channel_id']]
YT_ko_video_title = YT_video_title[YT_video_title['title'].str.contains('[가-힣]',regex=True)]
YT_ko_video_title['pre_title'] = [re.sub('[^A-Za-z0-9가-힣\s+]', '', s) for s in YT_ko_video_title['title']]
data = YT_ko_video_title['pre_title'][300000:400000]
numpy_data = data.to_numpy()

with ThreadPoolExecutor(max_workers=5) as executor:
    future = executor.map(get_translate,numpy_data)
    
listData = list(future)    
df_data = YT_ko_video_title[300000:400000]
df_data['en_title'] = listData
insert_df = df_data[['video_id','channel_id','en_title']]
insert_df.columns = ['video_id','channel_id','title']

db_conn.df_insert_table(insert_df,'YT_en_video_lists')
