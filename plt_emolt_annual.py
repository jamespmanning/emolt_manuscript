# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:28:34 2013
Making annual mean temperature plot
working with the output from "getemolt"
@author: jmanning

Modified in Oct 2014 to work with ERDDAP data
Modified in Mar 2025 to deal with WH and BB dockside temps
"""
import numpy as np
import matplotlib
from dateutil.parser import parse
#from pydap.client import open_url
from pandas import DataFrame,read_csv,to_datetime,concat
from matplotlib.dates import num2date
from matplotlib import pyplot as plt
from datetime import datetime as dt
from datetime import timedelta as td
import matplotlib.dates as dates
import sys
#sys.path.append('mygit/modules')
from conversions import c2f,fth2m
from dateutil import tz
import pytz

###### HARDCODES #########
maxnumyr=2 # maximum number of years needed to include (ie don't bother otherwise)
minnumdays=182
lincol=['red','blue','green','black','yellow','cyan','magenta','gray']
aveperiod='Decadal' # or Annual

#depmean=[183,10,28,63,22,20,31]
#sites=['JS02','BD01','MC02','JT04','AG01','BN01','WD01']
#depmean=[25,22,63]
#sites=['CJ01','AG01','JT04']
depmean=[25,20]
depmean=[1,1]

sites=['DJ02']
sites=['BT01']
sites=['JA01']
sites=['OD08']
sites=['BC02']
sites=['JS02','JS06']
sites=['JC01']
sites=['CP01']
sites=['GS01']
sites=['AC02']
sites=['BT01']
sites=['BI03']
sites=['MF02']
sites=['DMF2']
sites=['BN01']
sites=['JS02']
sites=['TS02']
sites=['BF02']
sites=['CJ01','BN01']
sites=['RA01']
sites=['BF01']
sites=['DK01']
sites=['AG01']
sites=['JT04']
sites=['WHAQ','BBHR']

newfile='output/JA01m60271701.dat'
newfile='output/BS02m60332202.dat'
newfile='output/DJ02m49139902.dat'
newfile='output/JA01m91121801.dat'
newfile='output/OD08m60321308.dat'
newfile='output/BC02m87861102.dat'
newfile='output/JS06m60482606.dat'
newfile='output/JC01m91062301.dat'
newfile='output/CP01m87881801.dat'
newfile='output/GS01m60402101.dat'
newfile='output/AC02m60051502.dat'
newfile='output/BT01m91071801.dat'
newfile='output/BI03m60311103.dat'
newfile='output/MF02m60092002.dat'
newfile='output/BN01m60462101.dat'
newfile='output/JS02m49112802.dat'
newfile='output/TS02m91001302.dat'
newfile='output/BF02m87870602.dat'
newfile=['output/CJ01m60422501.dat','output/BN01m60462101.dat']
newfile=['output/RA01m91042001.dat']
newfile=['output/BF01m48662201.dat']
newfile=['output/DK01m60252401.dat']
newfile=['output/AG01m60374501.dat']
newfile=['output/AG01m60374501.dat']
newfile=['/home/user/emolt/output/WHAQm879099aq.dat']

sitelabel="".join(sites)
#leg=['Sprague Downeast','Alley Mid-Coast','Brown Mass Bay']
#leg=['Carter','Gamage','Tripp']
leg=['']
####################################
depmin,depmax=[],[] # this defines a range of acceptable depths for this site
for k in range(len(depmean)):
  depmin.append(int(fth2m(depmean[k])-0.10*fth2m(depmean[k]))) #meters
  depmax.append(int(fth2m(depmean[k])+0.10*fth2m(depmean[k]))) #meters
  if depmin[k]==depmax[k]:
     depmin[k]=depmin[k]-2
     depmax[k]=depmax[k]+2

def getsite_latlon(site):
    df=read_csv('/home/user/emolt/emolt_site.csv')
    df1=df[df['SITE']==site]
    return df1['LAT_DDMM'].values[0],df1['LON_DDMM'].values[0]

def getobs_tempdepth_latlon(lat,lon):
    """
    Function written by Jim Manning to get emolt data from url, return datetime, depth, and temperature.
    this version needed in early 2023 when "site" was no longer served via ERDDAP
    Modified 10/27/2024 to allow for more precise lat/lon
    """
    #url = 'https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&latitude='+str(lat)+'&longitude='+str(lon)+'+&orderBy(%22time%22)'
    url='https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT_historic_non-realtime_bottom_temperatures.csvp?time%2Clatitude%2Clongitude%2Cdepth%2Csea_water_temperature&latitude%3E'+str(lat-0.03)+'&latitude%3C'+str(lat+0.03)+'&longitude%3E'+str(lon-0.03)+'&longitude%3C'+str(lon+0.03)+'+&orderBy(%22time%22)'
    df=read_csv(url,skiprows=[1])
    df['time']=df['time (UTC)']
    temp=1.8 * df['sea_water_temperature (degree_C)'].values + 32 #converts to degF
    depth=df['depth (m)'].values
    time=[];
    for k in range(len(df)):
            time.append(parse(df.time[k]))
    print('using erddap')            
    dfnew=DataFrame({'temp':temp,'Depth':depth},index=time)
    return dfnew


def getemolt_by_site_depth(site,depthw):
    """
    Function written by Jim Manning
    borrowed from Huanxin's functions in "getemolt" package
    site: is the 4-digit string like "BD01"
    depth: includes bottom depth and surface depth,like: [80,0].
    Modified Feb 2020 to accept eMOLT.csv file as extracted earlier when ERDDAP is down.
    """
    try:
        url='https://comet.nefsc.noaa.gov/erddap/tabledap/eMOLT.csvp?time,depth,sea_water_temperature&SITE=%22'+str(site)+'%22&orderBy(%22time%22)'
        #url='eMOLT.csv'
        #print url
        df=read_csv(url,skiprows=[1])
        df=df[(df['depth (m)']>=depthw[0]) & (df['depth (m)']<=depthw[1])]# gets only those depths requested
        time,temp=[],[]
        tempc=df['sea_water_temperature (degree_C)'].values
        for k in range(len(df)):
          #print df['time (UTC)'][k]
          time.append(parse(df['time (UTC)'].values[k])) # added ".values" feb 5, 2018
          #temp.append(c2f(df.sea_water_temperature[k])) # needed to convert to degF comply with old code below
          temp.append(c2f(tempc[k])) # needed to convert to degF comply with old code below
    except: # case of ERDDAP being down
        df=read_csv('../sql/eMOLT.csv',header=None,delimiter='\s+') # use this option when the ERDDAP-read_csv-method didn't work
        temp=df[3].values
        #print 'converting to datetime'
        time=to_datetime(df[0]+" "+df[1])
    tso=DataFrame(temp,index=time) 
    #tso.sort_index(inplace=True)
    return tso

fig=plt.figure()
#matplotlib.rcParams.update({'font.size': 18})
matplotlib.rc('xtick', labelsize=10)
matplotlib.rc('ytick', labelsize=10)
ax=fig.add_subplot(111)
for j in range(len(sites)):
  if sites[j]=='WHAQ':
      #tso=getemolt_by_site_depth(sites[j],[depmin[j],depmax[j]])
      [lat,lon]=getsite_latlon(sites[j])# started using this on 25 May 2023 when NEFSC took away "site" from ERDDAP
      tso=getobs_tempdepth_latlon(lat,lon)
      #tso=tso[tso['Depth']>5]# added this Feb 2025 to remove surface values from AG01 case
      # Here's where we add extra year(s) that are not yet in the database
      if j==0: # only checks for new file when j=0
       if len(newfile[j])>0:
          dfnow=read_csv(newfile[j],header=None)
          dfnow.columns=['SITE','SN','PS','TIME','YD','temp','SALT','Depth']
          del dfnow['SITE'];del dfnow['SN'];del dfnow['PS'];del dfnow['YD'];del dfnow['SALT'];
          dfnow['TIME']=to_datetime(dfnow['TIME']).dt.tz_localize(tz.tzutc())#,utc=True)
          dfnow.set_index('TIME',inplace=True)
          #dfnow22=dfnow[dfnow.index<np.datetime64(dt(2023,1,1,0,0,0,pytz.UTC))]
          timezone = pytz.timezone('UTC')
          dfnow22=dfnow[dfnow.index<timezone.localize(to_datetime('01-01-2025'))]#.dt.tz_localize(tz.tzutc())]
          tso = concat([tso,dfnow22])
  elif sites[j]=='BBHR':
      tso=read_csv('MaineDMR_Boothbay_Harbor_Sea_Surface_Temperatures.csv')#,parse_dates=['COLLECTION_DATE'],date_parser=dateparse)
      tso['Time UTC'] = to_datetime(tso['COLLECTION_DATE'])
      del tso['SEA_SURFACE_TEMP_MAX_C'];del tso['SEA_SURFACE_TEMP_MIN_C'];del tso['ObjectId'];del tso['COLLECTION_DATE']
      tso.rename(columns={'SEA_SURFACE_TEMP_AVG_C':'temp'},inplace=True)
      tso['temp']=tso['temp']*1.8+32
      tso= tso.set_index('Time UTC')
      tso=tso.sort_values(by='Time UTC',ascending=True)
      #tso=tso.sort_index(axis=1)#, inplace=True)
  yr,day=[],[]
  for kk in range(len(tso)):
      yr.append(tso.index[kk].year)
      day.append(tso.index[kk].dayofyear)
  tso['Year']=yr
  tso['Day']=day    
  tso1=tso.groupby(['Day','Year']).mean().unstack()
  ts=0
  te=366
  #dfa=tso['temp'].resample('YE-JUN').mean().dropna().plot(ax=ax,label=sites[j]+' annual')
  if len(list(set(tso['Year'].values)))>maxnumyr:
    for k in list(np.sort(list(set(tso['Year'].values)))):
      tso12=tso1['temp'][k].dropna() # series for this year
      print(str(k),min(tso12.index),max(tso12.index))
      tmi=min(tso12.index) #minimum yearday for this year
      if tmi<te:
        if tmi>ts:
          ts_temp=tmi  #new start yearday
      t=max(tso12.index) #maximum yearday of this year
      if t>ts:
        if t<=te:
          te_temp=t #new max yearday
      if te_temp-ts_temp>minnumdays: #if greater than so many days include it
        ts=ts_temp
        te=te_temp

    tso2=tso[tso.index.to_series().apply(lambda x: x.dayofyear)>ts]
    tso3=tso2[tso2.index.to_series().apply(lambda x: x.dayofyear)<te]
    #tso3.index.tz=None
    tso3=tso3.astype('float64')
    #tso_a=tso3['temp'].resample('A',how=['count','mean','median','min','max','std'])#,loffset=td(days=-365))# assumes the mean is at the end of the year so I had to fix the x-axis date
    tso_a=tso3['temp'].resample('A').mean()#.ohlc_dict()
    tso_ac=tso3['temp'].resample('A').count()
    tso_a=tso_a[tso_ac.values!=0]
    
    # here is where we get decadal averages
    # Extract the decade from the datetime index
    if aveperiod=='Decadal':
        decade = tso_a.index.year // 10 * 10
        decadal_average = tso_a.groupby(decade).mean()
        #ax.plot(to_datetime(decadal_average.index,format=('%Y'))+td(days=365*5),decadal_average.values,color=lincol[j],linewidth=5,label=sites[j]+' dockside')
        ax.plot(tso_a.index-td(days=182),tso_a.values,color=lincol[j],linewidth=1,label=sites[j]+' dockside')
    else:
        ax.plot(tso_a.index-td(days=182),tso_a.values,color=lincol[j],linewidth=3,label=sites[j]+' dockside')#+' '+chr(0x2191))# note the "182" making it mid-year point

    # do linear regression taking from https://www.geo.fu-berlin.de/en/v/soga-py/Advanced-statistics/time-series-analysis/Trends-and-seasonal-effects/Linear-trend-estimation/index.html
    t = np.arange(0, len(tso_a))
    z = np.polyfit(t, tso_a.values.flatten(), 1)
    p = np.poly1d(z)
    fitpts=p(t)
    t=[tso_a.index[0]-td(days=182),tso_a.index[-1]-td(days=182)]
    y=[fitpts[0],fitpts[-1]]
    #ax.plot(tso_a.index-td(days=182),fitpts,'--',color=lincol[j],linewidth=6,label=sites[j]+' '+chr(0x2191)+'%0.2f' % z[0]+' degF/year')
    
    if z[0]>0:
        ax.plot(t,y,':',color=lincol[j],linewidth=6,label=chr(0x2191)+'%0.2f' % z[0]+' degF/year')
    else:
        ax.plot(t,y,':',color=lincol[j],linewidth=6,label=chr(0x2193)+'%0.2f' % z[0]+' degF/year')
       
    if aveperiod=='Decadal':
        for jj in np.unique(decade):
            tso_a1=tso_a[(tso_a.index.year>=jj) & (tso_a.index.year<jj+10)]
            t = np.arange(0, len(tso_a1))
            z = np.polyfit(t, tso_a1.values.flatten(), 1)
            p = np.poly1d(z)
            fitpts=p(t)
            t=[tso_a1.index[0]-td(days=182),tso_a1.index[-1]-td(days=182)]
            y=[fitpts[0],fitpts[-1]]
            ax.plot(t,y,':',color=lincol[j],linewidth=1)#,label='%0.2f' % z[0]+' degF/year')
            timestamp_values = [ts.timestamp() for ts in t]
            mean_timestamp_value = np.mean(timestamp_values)
            meant=dt.fromtimestamp(mean_timestamp_value)
            if j==0:
                ax.text(meant,np.max(y)+3,'%0.2f' % z[0])
            else:
                ax.text(meant,np.min(y)-3,'%0.2f' % z[0])
                
    
ax.legend(loc='best',fontsize=10)# "2" for upper left
plt.ylabel('Annual Mean Temperature (degF)',fontsize=14)
ax2=ax.twinx()
ax2.set_ylabel('celsius',fontsize=14)
#ax2.set_ylim((np.nanmin(tso_a['mean'].values)-32)/1.8,(np.nanmax(tso_a['mean'].values)+-32)/1.8)
degFrange=ax.get_ylim()  
ax2.set_ylim((degFrange[0]-32)/1.8,(degFrange[1]-32)/1.8)  
ax2.set_xlabel('Year',fontsize=16)
if 'WHAQ' in sites:
    ax.xaxis.set_major_locator(dates.YearLocator(10))
else:
    ax.xaxis.set_major_locator(dates.YearLocator(2)) 
ax.xaxis.set_major_formatter(dates.DateFormatter('%Y'))  
plt.ylabel('Annual Mean Temperature (degC)',fontsize=14)
plt.xlabel('Year',fontsize=18)

if depmin!=0:
    plt.title('For instrument depths ='+"%0.0f" % fth2m(depmean[0])+' meters')#rounds to nearest integer depth
    plt.title('Depth ='+"%0.0f" % depmean[0] +' fathoms (~'+"%0.0f" % fth2m(depmean[0])+' meters)')#rounds to nearest integer depth
    #plt.title('eMOLT lobsterman, Jon Carter, off Bar Harbor in '+"%0.0f" % depmean[0] +' fathoms (~'+"%0.0f" % fth2m(depmean[0])+' meters)',fontsize=10)
fig.autofmt_xdate()
plt.show()
plt.savefig(sitelabel+'_annual.png')
