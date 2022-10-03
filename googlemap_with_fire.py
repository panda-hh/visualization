#서울시 구별 인구밀도와 소방서의 화재진압 정보 시각화
import googlemaps
import googlemap_key
import pandas as pd
import folium
import json
fire=pd.read_csv("C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/fire_number.txt",sep='\t',usecols=[1,2],encoding='utf-8')
fire.drop([0],inplace=True)#서울시 구별 화재발생 데이터 읽기

station_name=[]
gu_name=[]
for name in fire['자치구']:
    station_name.append(str(name)+'소방서')#구별 소방서 리스트 만들기


gmaps=googlemaps.Client(key=googlemap_key.gmaps_key)
station_addr=[]
station_lat=[]
station_lng=[]
for name in station_name:
	tmp=gmaps.geocode(name, language='ko')
	station_addr.append(tmp[0].get('formatted_address'))
	tmp_loc=tmp[0].get('geometry').get('location')
	station_lat.append(tmp_loc['lat'])
	station_lng.append(tmp_loc['lng'])#소방서 위치 위도,경도 리스트에 넣기

gu_name=[]
for name in station_addr:
    tmp=name.split()
    for word in tmp:
	    if word[-1]=='구':
		    gu_name.append(word)
		    break#소방서 위치정보에서 구 정보만 추출하여 추가하기

fire['구별']=gu_name
fire['위도']=station_lat
fire['경도']=station_lng#위도와 경도 구 정보 추가하기
people=pd.read_csv("C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/person.txt",sep='\t',usecols=[1,4],encoding='utf-8')
people['인구밀도(명/㎢)']=people['인구밀도(명/㎢)'].astype(float)
people.drop([0],inplace=True)#서울시 구별 인구밀도 자료불러오고 타입 object에서  float타입으로 바꾸기
fire.rename(columns={'자치구':'관서명'},inplace=True)
fire.rename(columns={'합계':'화재발생'},inplace=True)
fire['화재발생']=fire['화재발생'].astype(float)
fire.set_index('구별',inplace=True)
people.rename(columns={'지역':'구별'},inplace=True)
people.set_index('구별',inplace=True)
result=pd.merge(fire,people,on='구별',how='left')
result.rename(columns={'인구밀도(명/㎢)':'인구밀도'},inplace=True)#fire과 people의 index명 정확히 변경해주고 index'구별'로 묶기


result.to_csv("C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/result.csv", encoding='euc-kr')#중간저장

#서울 지도를 서울시청 중심으로 가져오기
tmp=gmaps.geocode('서울특별시청',language='ko')
tmp_loc=tmp[0].get('geometry').get('location')
Seoul_loc=[tmp_loc['lat'],tmp_loc['lng']]
Seoul_map=folium.Map(location=Seoul_loc,zoom_start=11)

station_geo=result.loc[:,['관서명','위도','경도']]
station_geo.set_index('관서명',inplace=True)

#소방서 위치 지도위에 표시하기
for n in station_geo.index:
    folium.Marker([station_geo['위도'][n],station_geo['경도'][n]], popup=n+' 소방서').add_to(Seoul_map)
Seoul_map.save("C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/Seoul_with_fire.html")
result.to_csv('C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/result.csv',encoding='UTF-8')

#소방서의 화재발생 데이터를 원형모형으로 지도위에 나타내기
for n in result.index:
    folium.CircleMarker([result['위도'][n],result['경도'][n]], radius=result['화재발생'][n]/10,fill=True).add_to(Seoul_map)
Seoul_map.save("C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/Seoul_with_fire_circle.html")

#서울시 구별 경계선을 표시하고 구별 인구밀도수를 표현하기
geo_str=json.load(open("C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/Seoul_geo.txt",encoding='euc-kr'))
Seoul_map.choropleth(geo_data=geo_str,data=result['인구밀도'],columns = [result.index, result['인구밀도']],fill_color='YlOrRd',key_on='feature.id')
Seoul_map.save('C:/Users/panda/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Python 3.6/Seoul_with_fire_final.html')
