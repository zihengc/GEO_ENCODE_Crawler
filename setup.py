"""Install required packages"""
import os
#install packages
libs = {"numpy","matplotlib","pandas","requests","beautifulsoup4","download","biopython","tabulate","tqdm", "requests_ftp","nltk","networkx", "scikit-learn", "wordcloud"}

try:
     for lib in libs:
        print(lib)
        os.system("pip install "+lib)
     print("Successful")

except:
     print("Failed Somehow")
