######################################################################################
crawler: Python package for retrieving metadata and downloading datasets from ENCODE/GEO and conducting natural language proecessing on the metadata
######################################################################################

The program was tested on Python 3.7 +

Link to the demonstration (need andrew id to access the google drive): https://drive.google.com/file/d/18-O1GkruHvokf-TW6kR-EMK2sE4Cljvn/view?usp=sharing 

To run the program, firstly cd the program folder and run "python setup.py" to install dependent packages:
    "numpy","matplotlib","pandas","requests","beautifulsoup4","download","biopython","tabulate","tqdm", "requests_ftp","nltk","networkx", "scikit-learn", "wordcloud"

The TextRank function depends on "glove.6B.100d.txt" file, so please check if the file is in the program folder.


To retrieve genomic data on ENCODE run:
    1. "python main.py enquire inquire"
    2. input a keyword of interest

To retrieve genomic data on GEO run:
    1. "python main.py geo inquire"
    2. Input a keyword of interest

To download genomic data on ENCODE run:
    1. "python main.py encode download"
    2. input a experiment ID of interest

To download genomic data on ENCODE run:
    1. "python main.py geo download"
    2. Input "geos_keyword.csv", in which the csv file is from the program folder

To perform natural language processing on GEO entry titles:
    To rank text:
        1. "python main.py nls textrank"
        2. Input "geos_keyword.csv", in which the csv file is from the program folder; It takes a long time to run if the csv file has several thousand entries

    To generate WordCloud:
        1. "python main.py nls wordcloud"
        2. Input "geos_keyword.csv", in which the csv file is from the program folder

    To generate topics:
        1. "python main.py nls lda"
        2. Input "geos_keyword.csv", in which the csv file is from the program folder
