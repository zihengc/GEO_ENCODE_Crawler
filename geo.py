import requests
from bs4 import BeautifulSoup
import bs4
import pandas as pd
import numpy as np
import pandas as pd
from io import StringIO
from tabulate import tabulate
#from IPython.core.display import HTML
import json
import download
#import re
from Bio import Entrez
from encode import *
from tqdm.autonotebook import tqdm


Entrez.email = "liqiming1914658215@gmail.com"
Entrez.api_key = "c80ce212c7179f0bbfbd88495a91dd356708"


def start_geo():
    """
    start_geo is a high level function that starts search on geo
    """
    database="gds"
    keywords=input("Keywords to search on GEO?")
    geo_info(database, keywords)

def batch_download():
    """
    batch_download is a high level function that start batch downloads
    """
    while True:
        file_path = input("csv file name?")

        if os.path.exists(file_path):

            path_geo=file_path
            link_file_name="geo_links"+".csv"
            auto_downloadgeo(path_geo,link_file_name)

            break
        else:
            print("Directory does not exist")



def geo_info(database, keywords):
    """
    get_info takes a database name and keywords to search and save all the information found on geo

    Parameters
    ----------
    database: string
    keywords: string

    returns
    ------

    """
    count, idlist = search(database, keywords)

    flag = 0
    with open("idlist.txt", "w", encoding="utf-8") as f:
        f.write(str(idlist))

    df_allsamples=pd.DataFrame()
    df_allgeos=pd.DataFrame()
    print("Getting detials of each entry")
        #loop every entry related to the keyword
    desc = "Retriving"
    n_download=int(input ("{} entries are available, how many to download?".format(count)))
    pbar = tqdm(
        total=int(n_download),
        initial=0,
        unit=" entry",
        unit_scale=False,
        desc=desc,
            )

    for id in idlist[0:n_download]:
        flag += 1
        geo_id, title, summary,link,df_samples, df_geo = get_summary(database, id)
        df_allsamples=df_allsamples.append(df_samples,ignore_index=True)
        df_allgeos=df_allgeos.append(df_geo,ignore_index=True)
        pbar.update(1)

     #save csv files
    print("Saving all GEO entries")
    df_allgeos.to_csv("geos_{}.csv".format(keywords))

    print("Saving all samples")
    df_allsamples.to_csv("geosamples_{}.csv".format(keywords))



def auto_downloadgeo(path_geo,link_file_name):
    """ high level function that retrives experiments from a biosample on ENCODE
    Parameters
    ----------
    path_geo

    returns
    ------

    """
    df= get_geofile_links(path_geo,link_file_name)
    download_geo(df)

def get_geofile_links(path_geo,link_file_name):
    """
    get_geofile_links takes the path of geo and save the linkes of the files to the current folder

    Parameters
    ----------
    path_geo: string; the path of a csv file
    link_file_name: string; name of the csv file to save

    returns
    ------

    """

    #take a csv file that contains all geo entry you want to download
    df_geo=pd.read_csv(path_geo)
    accessions=df_geo['Accession'].to_list()
    geofile_links=pd.DataFrame()
    for entry in accessions:
        geofile_links=geofile_links.append(GEO_file(entry),ignore_index=True)
    #save a csv file that contains all the links
    geofile_links.to_csv(link_file_name)
    return geofile_links

def GEO_file(entry):
    """
    GEO_file takes a geo entry id and retrive the download links associated with the entry

    Parameters
    ----------
    entry: string; geo id

    returns
    ------
    df: pandas.DataFrame
    """
    #Access GEO html
    try:
        if entry !=np.nan:
            print("accessing https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={}".format(entry))
            html=get_HTMLText("https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={}".format(entry))
            soup=parse_html(html)
    except:
        print ("get_geo error")
        return

    #find all of the links
    links=soup.find_all('td', bgcolor="#DEEBDC")

    ftp_http = {}
    ftp_http['GEO_entry_ID']=entry

    #extract download links from GEO
    n=None
    for i in links:

        try:
            if i.string[0]=="G":
                file_name=i.string
                ftp_http['file_name']=file_name
                n=1
            elif n==1:
                file_size=i.string
                ftp_http['file_size']=file_size
                n+=1
            elif n==2:
                for children in i.children:
                    href=children.attrs.get("href")
                    if href[0:3]=="ftp":
                        ftp_http['ftp']=href
                    elif href[0:4]=="/geo":
                        href='https://www.ncbi.nlm.nih.gov'+href
                        ftp_http['http']=href
                n+=1
            elif n==3:
                file_type=i.string
                ftp_http['file_type']=file_type
                n+=1

        except:
            if n==2:
                try:
                    for children in i.children:

                        href=children.attrs.get("href")

                        if href[0:3]=="ftp":
                            ftp_http['ftp']=href
                        elif href[0:4]=="/geo":
                            href='https://www.ncbi.nlm.nih.gov'+href
                            ftp_http['http']=href
                    n+=1
                except:
                    print("no download link found for {}".format(entry))
            continue

    #save links to a dataframe
    df=pd.DataFrame()
    df=df.append(ftp_http,ignore_index=True)

    return df # return content

def download_geo(df):
    """
    download_geo takes a dataframe and start batch download

    Parameters
    ----------
    df: pandas.DataFrame

    returns
    ------

    """

    for row in df.index:
        http = df.loc[row]["http"]
        GEO_entry = df.loc[row]["GEO_entry_ID"]
        file_name = df.loc[row]["file_name"]
        print("-------------------------------------------------------------------------")
        print("GEO: "+GEO_entry+''+"File: "+ str(file_name))
        try:
            if http!='https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=nan':
                download.download_file(str(http),str(file_name),show_progress=True)
        except:
            print("The file is not available")
            continue


def search(database, keywords):
    """
    search function takes a given database and keywords to search on a API.

    Parameters
    ----------
    database: string
    keywords: string

    returns
    ------
    count: int; number of entries
    IdList: list; list of entries
    """
    print("Start searching keywords")
    handle = Entrez.esearch(db=database, term=keywords, retmax=13001)
    record = Entrez.read(handle)

    return record["Count"], record["IdList"]


def get_summary(database, geo_id):
    """
    get_summary takes a name of a database and geo_id of the entry and return infomration about the entry

    Parameters
    ----------
    database: string
    geo_id: string

    returns
    ------
    record[0]["Id"]: string
    record[0]["title"]: string
    record[0]["summary"]: string
    record[0]['FTPLink']: string
    df_samples: pandas.DataFrame
    df_geo: pandas.DataFrame

    """

    #print("Getting details of the ")
    handle = Entrez.esummary(db=database, id=geo_id)
    record = Entrez.read(handle)

    df_geo=pd.DataFrame()
    df_samples=pd.DataFrame(record[0]["Samples"])
    df_samples['Title']=record[0]['title']
    df_samples['File type']=record[0]['suppFile']
    df_samples['Taxon']=record[0]['taxon']
    df_samples['ID']=record[0]['Id']
    df_samples['GEO accession']=record[0]['Accession']

    df_geo=df_geo.append(get_GEOdf(record))

    return record[0]["Id"], record[0]["title"], record[0]["summary"],record[0]['FTPLink'],df_samples,df_geo


def save_text(geo_id, title, summary,link):
    """
    Save_text saves formated geo information to a txt tile

    """
    filename = path + geo_id + ".txt"
    print(filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("geo_id:\n\r"+geo_id+"\n\rTitle:\n\r"+title+"\n\rSummary:\n\r"+summary+"\n\rFTPLink:\n\r"+link)


def get_GEOdf(record):
    """
    Save_text saves formated geo information to a dataframe

    """
    df=pd.DataFrame()
    dic={}
    for key in record[0]:
        if key in ['Id','Accession','title','summary','entryType','taxon','PDAT','FTPLink']:
            dic[key]=record[0][key]


    df=df.append(dic,ignore_index=True)
    return df
