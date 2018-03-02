
# coding: utf-8

# In[3]:


import pandas as pd
import dateutil.parser
import re

# creating dummy email address when not present first name_last name@noemail.com
def fixEmail(row):
    myEmail = row['Email Address']
    #print(myval)
    if re.search('@',str(myEmail)):
        toReturn = row['Email Address']
    else:
        toReturn = row['First Name'] +'_'+ row['Last Name'] + '@noemail.com'
        
    return toReturn.lower()

#Cleaning up position data as one designation could be expressed in multiple way.
def CleanPosition(inVal):
    inVal = str(inVal).upper()
    inVal = re.sub('SENIOR|SR|\.|-|(|)','',inVal)
    inVal = re.sub('\s+',' ',inVal).strip()
    inVal = re.sub('VICE PRESIDENT','VP',inVal)
    inVal = re.sub('CHIEF OPERATING OFFICER','COO',inVal)

    if re.search('HEADHUNTING|TALENT ACQUISITION|RECRUITER|SOURCER|RECRUITING|RECRUITMENT|SOURCING MANAGER|HEADHUNTER|TALENT SPECIALIST',inVal):
        inVal = 'RECRUITER'
    elif re.search('CHIEF EXECUTIVE OFFICER|CO-CEO|CHAIRMAN',inVal):
        inVal = re.sub('CHIEF EXECUTIVE OFFICER|CO-CEO|CHAIRMAN','CEO',inVal).strip()
    elif re.search('FOUNDER',inVal):
        inVal = 'FOUNDER'
    elif re.search('PROFESSOR',inVal):
        inVal = 'PROFESSOR'
    elif re.search('EXECUTIVE ASSISTANT',inVal):
        inVal = 'EXECUTIVE ASSISTANT'
    elif re.search('MANAGER',inVal):
        inVal = 'MANAGER'
        
    return inVal
 

# A person can be responsib
def SplitPosition(row):
    
    myPosition = row['Position']
    myPosition = str(CleanPosition(myPosition))
    if myPosition == '':
        returnVal = ['NoPositon']
    else:
        returnVal = SplitPositionHelper(myPosition)
        
    return returnVal

def SplitPositionHelper(inVal):
    
    inVal = str(CleanPosition(inVal))
    returnList = []
    if re.search(' AND ',inVal):
        tempList = inVal.split(' AND ')
    elif re.search('&',inVal):
        tempList = inVal.split('&')
    elif re.search(' OF ',inVal):
        tempList = inVal.split('OF')
    elif re.search(',',inVal):
        tempList = inVal.split(',')
    elif re.search('/',inVal):
        tempList = inVal.split('/')
    elif re.search('|',inVal):
        tempList = inVal.split('|')
    else:
        tempList = [inVal]
        
        
    for value in tempList:
        if re.search(' AND |&| OF |,|/|\|',value):
            returnList.extend(SplitPositionHelper(value))
        else:
            returnList.append(value) 
            
    #Return the list after processing
    return returnList



df = pd.read_csv('./data/Connections.csv',encoding ='utf8')
df['Email Address'] = df.apply(fixEmail,axis=1)
df['Position_List'] = df.apply(SplitPosition,axis=1)
df['doman'] = df['Email Address'].apply(lambda x: str(x).split('@')[1])
df['ConnectedOnDate'] = df['Connected On'].apply(lambda x: dateutil.parser.parse(x))
df['year'] = df['ConnectedOnDate'].dt.year
df['month'] = df['ConnectedOnDate'].dt.month
df['monthstr'] = df['ConnectedOnDate'].dt.strftime('%b')
df['day'] = df['ConnectedOnDate'].dt.day
df['dated'] = df['ConnectedOnDate'].dt.date
df['hour'] = df['ConnectedOnDate'].dt.hour
#df['year'] = df['ConnectedOnDate'].dt.weekday
df['weekday'] = df['ConnectedOnDate'].dt.strftime('%A')
df['hourAP'] = df['ConnectedOnDate'].dt.strftime('%I %p')
df['counter'] = 1
df.to_csv('./output/allData.tsv',sep='\t',index=False,header=True,encoding ='utf8')
# Get the job Relationships
mydata = []
for index, row in df[['Email Address','Position_List']].iterrows():
    mydata.extend(list(zip([row['Email Address']]* len(row['Position_List']),row['Position_List'] )))
    
dfemailPosition = pd.DataFrame(mydata,columns = ['email','single_position'])
dfemailPosition['single_position'] = dfemailPosition['single_position'].apply(lambda x: re.sub('\s+',' ',x).strip())
dfemailPositionSelfJoin = dfemailPosition.merge(dfemailPosition, on = 'email')
dfemailPositionSelfJoin = dfemailPositionSelfJoin[(dfemailPositionSelfJoin.single_position_x != '') & (dfemailPositionSelfJoin.single_position_y != '')]
#dfemailPositionSelfJoin = dfemailPositionSelfJoin[dfemailPositionSelfJoin.single_position_x != 'RECRUITER']
dfemailPositionSelfJoin.columns = ['email','main','supporting']
dfemailPositionSelfJoin[dfemailPositionSelfJoin.main != 'RECRUITER'].drop_duplicates().to_csv('./output/positionAnalytics.tsv',sep='\t',index=False,header=True,encoding ='utf8')
dfemailPositionSelfJoin[dfemailPositionSelfJoin.main != 'RECRUITER'].drop_duplicates().to_csv('./dc/positionAnalytics.tsv',sep='\t',index=False,header=True,encoding ='utf8')

#dfemailPositionSelfJoin[dfemailPositionSelfJoin.single_position_x == 'RECRUITER'].to_csv('./output/recruterAnalytics.tsv',sep='\t',index=False,header=True)


dfRecruters = df.merge(dfemailPositionSelfJoin[dfemailPositionSelfJoin.main == 'RECRUITER'][['email']], how='inner', left_on=['Email Address'], right_on=['email'])
dfRecruters.to_csv('./output/recruiterOnly.tsv',sep='\t',index=False,header=True,encoding ='utf8')

#D3js
dfbar = df.groupby(['hour','hourAP'])['counter'].count().reset_index()

dfbar = dfbar[['hourAP','counter']]
dfbar.columns = ['dayhour','connections']
dfbar.to_csv('./output/timeofday.csv',sep=',',header=True,index=False,encoding ='utf8')

df.dtypes

