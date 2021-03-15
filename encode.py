import requests
from bs4 import BeautifulSoup
import bs4
import pandas as pd
import numpy as np
import pandas as pd
from io import StringIO
from tabulate import tabulate
import json
import download
import os


def start_encode():
    """ high level function that retrives experiments from a biosample on ENCODE
    Parameters
    ----------
    biosample_id: string
    keyword: biosample keyword

    returns
    ------
    True: if there is no experiment the function returns True
    """

    #Start searching keyword on ENCODE
    keyword=input("Keyworld to search on ENCODE:")
    html=search_term(keyword)
    soup=parse_html(html)
    dic_biosample=search_biosample(soup)
    df_biosample=pd.DataFrame.from_dict(dic_biosample,orient='index')
    #Print the biosamples found on ENCODE
    print(tabulate(df_biosample, headers='keys', tablefmt='psql'))

    #Choose whether to save CSV files
    while True:
        instruction= input("Download all the biosamples to CSV file (yes) or enter enquiry mode(no) ? YES / NO: ")
        if instruction in ["no", "No", "NO", "nO","n","N"]:
            break
        #Save all the information related to the keyword
        elif instruction in ["yes", "Yes", "YES", "y","Y"]:
            df_biosample.to_csv("biosample_{}.csv".format(keyword))
            break

    #Choose a biosample ID for downloading experiments
    while True:
        biosample_id=input("Which biosample to download? (ID/ALL/QUIT)")
        if biosample_id in ["ALL",'All','A','all']:
            for i in df_biosample.index:
                get_experiments_fromsamples(biosample_id=i,keyword=keyword)
        elif biosample_id in ["quit","Quit","Q","q","QUIT"]:
            print("Program quit")
            return
        else:
            #if the biosample ID is in the index
            if biosample_id not in df_biosample.index:
                print("The biosample is not listed. Please try again.")
            else:
                get_experiments_fromsamples(biosample_id,keyword=keyword)





def experiment_downloader():
    """ Download experiment from ENCODE

    """

    while True:
        experiment=input("Which experiment to download (Experiment ID/QUIT)?")
        if experiment in ['Quit','quit','Q','q','QUIT']:
            print("Program quit")
            break

        else:
            try:
                df_experiment=get_experiment(experiment)
                download_experiment(df_experiment)
            except:
                print("Download error, check your experiment ID")


def get_HTMLText(url):
    """ Acquire a HTML page given a url
    Parameters
    ----------
    url: string

    returns
    ------
    r.text: str
    """
    try:
        kv = {'user-agent':'Mozilla/5.0'}
        r = requests.get(url, timeout=30)
        r.raise_for_status() # if not 200, raise HTTPError
        r.encoding = r.apparent_encoding #set encoding
        return r.text # return content
    except:
        return "getHTMLText error"

def search_term(term):
    """ search a biosample relevant to a term on ENCODE
    Parameters
    ----------
    term: string

    returns
    ------
    html: str
    """
    try:
        html=get_HTMLText("https://www.encodeproject.org/search/?searchTerm={}&type=Biosample&limit=all".format(term))

        return html # return content
    except:
        return "search_term error"


def parse_html(html):
    """ convert html into a tree structure with beautifulsoup
    Parameters
    ----------
    html: str

    returns
    ------
    soup: bs4.BeautifulSoup
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def search_biosample(soup):
    """ search biosample information on the given html soup
    Parameters
    ----------
    soup: bs4.BeautifulSoup

    returns
    ------
    dic_biosample: a dictionary of biosamples
    """
    biosamples=soup.find_all("a","result-item__link")
    dic_biosample={}
    for node in biosamples:
        href=node.attrs.get("href")
        href=href.split("/")[-2]#trim other components of hrefs
        dic_biosample[href]=biosample_info(node)+biosample_summary(node)#use function biosample_info
    #Convert the dictionary to dataframe

    return dic_biosample


def biosample_info(node):
    """ search biosample information from a given node
    Parameters
    ----------
    node: bs4.element.Tag

    returns
    ------
    information: list
    """
    information =[]
    #the biosample are saved in the children of the given node
    n=0
    for i in node.children:

        string_temp=i.string
        string_temp=string_temp.strip()

        if n==0:
            string_temp=string_temp[:-1]
            string_temp=string_temp.strip()
        elif n==2:
            string_temp=string_temp[1:-1]
            string_temp=string_temp.strip()
        information.append(string_temp) # retrive the string from the children node
        n=n+1
    return information #information is a list


def biosample_summary(node):
    """ search biosample summary from a given node
    Parameters
    ----------
    node: bs4.element.Tag

    returns
    ------
    list_biosample_summary: list
    """
    list_biosample_summary=[]
    #the summary of the samples is stored at the next_sibling
    for i in node.next_sibling.strings:
        #skip the header of each section
        list_header=["Summary:" ,"Type:","Culture harvest date:","Source:"]
        i=i.strip()
        if i in list_header :
            continue
        else:
            if i:
                list_biosample_summary.append(i)
    return list_biosample_summary




def search_id(search_detail,folder):
    """ Search a biosample from ENCODE and return a uuid that directs to the experiments of the biosample
    Parameters
    ----------
    search_detail: string ; id of the biosample

    returns
    ------
    uuid: str
    """
    f=open(folder+"biosample.txt","a")

    print("------------------------------------------------------------------------------")
    f.write("------------------------------------------------------------------------------"+"\n")
    sample_id=search_detail

    #get the html of the biosample
    html=get_HTMLText("https://www.encodeproject.org/biosamples/"+sample_id)
    #parse the html to a tree structure
    soup = BeautifulSoup(html, 'html.parser')

    #Get the summary of the sample ID from dt tags
    dt = soup.find_all('dt')
    dic={}

    for i in dt:
        dic[i.string]=i.next_sibling.getText()

    for i in dic:
        print(i+': '+dic[i])
        f.write(i+': '+dic[i]+"\n")

    #The uuid of the experiments is stored at script tag in the form of json
    js=soup.find_all("script", type="application/json")[0].string
    #use json package to parse the json content stored in html
    newDictionary=json.loads(js)
    #select the uuid of the biosample
    uuid = newDictionary['uuid']
    f.close()
    return uuid




def get_experiment(experiment):

    """ retrive the experiment information from ENCODE and save the information into a pandas dataframe
    Parameters
    ----------
    experiment: string; experiment id

    returns
    ------
    df: pandas.DataFrame ;
    """
    print("------------------------------------------------------------------------------")
    #try to pull down the html of the experiment page
    try:
        print("accessing https://www.encodeproject.org/experiments/{}/".format(experiment))
        html=get_HTMLText("https://www.encodeproject.org/experiments/{}/".format(experiment))
        soup=parse_html(html)
        #print(soup)

    except:
        print("get_experiment error")


    #extract files from the json element in the html
    js=soup.find_all("script",type="application/json")[0].string
    newDictionary=json.loads(js)

    df=pd.DataFrame(newDictionary["files"])

    #useful features
    columns= ["accession",'title','file_format','date_created','file_size','output_type','assembly', 'status',
    'output_category','assay_term_name','read_length', 'run_type',"href"
    ]

    href_list=[]
    for accession in newDictionary["files"]:
        href=accession['href']
        href="https://www.encodeproject.org"+href
        #print(href)
        href_list.append(href)

    #filter the df to include the columns
    df=df[df.columns[df.columns.isin(columns)]]

    df["href"]=href_list
    #convert the file size to mb
    df['file_size']=round(df['file_size']/(1024**2),1)
    return df

def download_experiment(df_files):
    """ download the files in a dataframe from ENCODE
    Parameters
    ----------
    df_files: pandas.DataFrame

    returns
    ------

    """
    print("------------------------------------------------------------------------------")
    n=1 # initialize a counter

    for i in df_files.index:
        #get the url of experiment
        href=df_files.loc[i,"href"]
        #get md5 for validation
        #md5=df_files.loc[i,"md5sum"]
        #make up the address of experiment
        #address="https://www.encodeproject.org"
        #file_address=address+href
        #extract file name
        file_address=href
        file_name=href.split('/')[-1]

        print("File {}:".format(n),file_name)

        #download all the files listed in df
        download.download_file(file_address,file_path=file_name,show_progress=True,md5_hash=None)

        n=n+1


def biosample_to_experiment(uuid, path):
    """ extract the experiment ids from a biosample id
    Parameters
    ----------
    uuid: string; uuid of the biosample
    path: directory to save the txt file
    returns
    ------

    """
    f=open(path+"biosample.txt", "a")

    print("------------------------------------------------------------------------------")
    f.write("------------------------------------------------------------------------------"+"\n")
    #get the html of the experiments page of the sample
    html=get_HTMLText("https://www.encodeproject.org/search/?type=Experiment&replicates.library.biosample.uuid={}&status=released&status=submitted&status=in+progress&limit=all".format(uuid))
    soup = BeautifulSoup(html, 'html.parser')
    #extract json section that includes the experiments from html
    js=soup.find_all("script", type="application/json")[0].string
    newDictionary=json.loads(js)
    # get experiments information
    keys=['accession',
          'status',
          'biosample_summary',
          'dbxrefs',
          'assay_term_name',
          'assay_title',
          'target']

    #print the experiment information
    experiment_ids=[]
    for i in range(len(newDictionary['@graph'])):
        print("------------------------------------------------------------------------------")
        f.write("------------------------------------------------------------------------------"+"\n")
        for key in keys:

            try:
                line = newDictionary['@graph'][i][key]
                if type(line) == dict:
                    print(line['label'])
                    f.write(line['label']+ "\n")
                    print("saved")

                else:
                    print(line)
                    f.write(line+"\n")
                    print("saved")
                    #extract experiment ID
                    if len(line)==11 and line[0]=='E':
                        experiment_ids.append(line)
            except:
                continue
            else:
                continue
    f.close()
    return experiment_ids



def input_searchID(df):
    """ input_searchID takes a dataframe to search for detail
    Parameters
    ----------
    df: pandas.DataFrame

    returns
    ------

    """

    while True:
        search_detail= input("Search for detail? Sample ID/no:")

        if search_detail in ["no", "No", "NO", "nO"]:
            print("Quit search")
            break

        #if the tissue of interest is not in
        elif search_detail not in df.index:
            print("Wrong input")

        else:
            uuid = search_id(search_detail)
            biosample_to_experiment(uuid)

            break

def filter_species(df_biosample):
    """ search for tissue of interested and return a dataframe containing the samples of the tissue
    Parameters
    ----------
    df_biosample: pandas.DataFrame

    returns
    ------
     df: list #dataframe of the samples of specific tissues
    """

    if len(df_biosample[1].unique())!=0:
        print("Species: ")
        for i in df_biosample[1].unique():
            print ("\t"+i)
    else:
        print("No tissue information")

    #Select the tissue of interest by user
    while True:
        tissue= input("Species of interest:")

        if tissue not in df_biosample[1].unique():
            print("The tissue of interest is not in the data")
        else:
            break

    #dataframe of the tissue of interest
    df=df_biosample[df_biosample[1]==tissue]

    #print a formulated table of biosample
    print(tabulate(df_biosample[df_biosample[1]==tissue], headers='keys', tablefmt='psql'))

    return df




def filter_tissue(df_biosample):
    """ search for tissue of interested and return a dataframe containing the samples of the tissue
    Parameters
    ----------
    df_biosample: pandas.DataFrame

    returns
    ------
    df: list #dataframe of the samples of specific tissues
    """

    if len(df_biosample[0].unique())!=0:
        print("Tissue types: ")
        for i in df_biosample[0].unique():
            print ("\t"+i)
    else:
        print("No tissue information")

    #Select the tissue of interest by user
    while True:
        tissue= input("Tissue of interest:")

        if tissue not in df_biosample[0].unique():
            print("The tissue of interest is not in the data")
        else:
            break
    df=df_biosample[df_biosample[0]==tissue]
    print(tabulate(df_biosample[df_biosample[0]==tissue], headers='keys', tablefmt='psql'))
    return df




def get_experiments_fromsamples(biosample_id,keyword):
    """ retrive experiments from a biosample on ENCODE
    Parameters
    ----------
    biosample_id: string
    keyword: biosample keyword

    returns
    ------
    True: if there is no experiment the function returns True
    """
    try:
        dirc=keyword+"_"+biosample_id+"_biosample/"

        if not os.path.exists(dirc):
            os.makedirs(dirc)

        uuid = search_id(biosample_id,dirc)
        experiment_ids=biosample_to_experiment(uuid,dirc)

        for experiment in experiment_ids:
                get_experiment(experiment).to_csv(dirc+"{}.csv".format(experiment))

    except:
        print("No experiment available")
        return True
