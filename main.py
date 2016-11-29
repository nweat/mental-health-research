__author__ = 'nweat'

try:
    import json
except ImportError:
    import simplejson as json

import data_manager,sys,getopt,codecs,tweepy,yaml

def main(argv):
    ifile = ''
    ofile = ''
    stats = ''
    normalusers = ''
    illness = ''
    processed_diagnosed_users = []

    config = open('config.yaml')
    dataMap = yaml.safe_load(config)
    ACCESS_TOKEN = dataMap['TwitterCredentials']['ACCESS_TOKEN']
    ACCESS_SECRET = dataMap['TwitterCredentials']['ACCESS_SECRET']
    CONSUMER_KEY = dataMap['TwitterCredentials']['CONSUMER_KEY']
    CONSUMER_SECRET = dataMap['TwitterCredentials']['CONSUMER_SECRET']
    config.close()
    
    if len(argv) == 0:
        print 'You must pass some parameters'
        return

    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)

        obj = data_manager.manager.StatsManager(api) #twitter_stream
        helper = data_manager.helpers.Helpers()

        opts, args = getopt.getopt(argv, "", ("ifile=","ofile=","stats=","illness=","normalusers="))
                
        for opt,arg in opts:
            if opt == '--ifile':
                ifile = arg
            elif opt == '--ofile':
                ofile = arg
            elif opt == '--stats':
                stats = arg
            elif opt == '--illness':
                illness = arg
            elif opt == '--normalusers':
                normalusers = arg

        inputFile = codecs.open(ifile, 'r', encoding = "utf-8")
        outputFile = codecs.open(ofile, "w+", "utf-8")

        if stats and illness:   
            #outputFile.write('screenName;created;location;geoEnabled;description;diagnosisMade;diagnosisStatement;NumTweetsYrUpToDiagnosis;NumTweetsPosted;Retweets;numFavorites;numFollowers;numFriends;AdvocateRefDesc;DiseaseRefDiagnosis;DepressionRefDesc;DepressionRefDiagnosis;SurvivorRefDesc')
            
            print "\n******Extracting twitter users who made diagnosis statements******"
            diagnosed_users = obj.extractDiagnosedUsers(inputFile)
            if diagnosed_users:
                print "Done..."

            print "\n******Generating stats for twitter users who made diagnosis statements******"
            processed_diagnosed_users = obj.generate_stats(illness, diagnosed_users)
            outputFile.write(json.dumps(processed_diagnosed_users, sort_keys = True, indent=4, ensure_ascii=False, separators=(',', ':'), default = helper.myconverter))
            
            #print processed_diagnosed_users
            #outputFile.flush()
        
    except arg:
        print 'Arguments parser error ' + arg
    finally:
        inputFile.close()
        outputFile.close()
        print '\n%s Results added to file\n' % len(processed_diagnosed_users)


if __name__ == '__main__':
    main(sys.argv[1:]) #1: refers to parameters needed to be supplied