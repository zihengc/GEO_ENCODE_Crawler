import sys

def main():
    print("Welcome! Please type encode/geo/textrank as argv[1], inquire/download/csv_file_name as argv[2] ")
    #Two input instructions
    database=sys.argv[1]
    instruction=sys.argv[2]
    #GEO
    if database=="geo":
        import geo
        if instruction == "inquire":
            geo.start_geo()
            return
        elif instruction == "download":
            geo.batch_download()
            return
    #ENCODE
    elif database=="encode":
        import encode
        if instruction == "inquire":
            encode.start_encode()
        elif instruction == "download":
            encode.experiment_downloader()
        return
    #natural language processing
    elif database=="nlp":

        #TextRank
        if instruction == "textrank":
            print("Natural language processing: TextRank")
            import text_rank
            text_rank.text_rank()
        #WordCloud
        elif instruction == "wordcloud":
            print("Natural language procesing: WordCloud")
            import wc
            wc.start_word()
        #LDA topic model
        elif instruction == "lda":
            print("Natural language processing: LDA topic model")
            import lda
            lda.start_lda()


if __name__ =="__main__":
    main()
