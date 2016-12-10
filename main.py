__author__ = 'nweat'

try:
    import json
except ImportError:
    import simplejson as json

import data_manager,sys,getopt,codecs,tweepy,yaml,os,os.path

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

    """
    GLOBAL VARIABLES
    """
    path = os.path.join(os.getcwd(), "data_manager/data/seed_nodes.txt")

    if len(argv) == 0:
        print 'You must pass some parameters'
        return

    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        api = tweepy.API(auth, wait_on_rate_limit = True, wait_on_rate_limit_notify = True)
        myStreamListener = data_manager.manager.TwitterStreamListener(500, path) # pass file and limit of sample normal user candidates to write to file
        myStream = tweepy.Stream(auth = api.auth, listener = myStreamListener)

        helper_obj = data_manager.manager.HelperManager()
        stas_obj = data_manager.manager.StatsManager(api)
        normal_user_obj = data_manager.manager.NormalUsersManager(api, myStream)
        
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

        if stats and illness:
            # python main.py --ifile data_manager/data/diagnosed_users_in.csv --stats 1 --illness anxiety --ofile data_manager/data/out.json
            inputFile = codecs.open(ifile, 'r', encoding = "utf-8")
            outputFile = codecs.open(ofile, "w+", "utf-8")
            print "\n******Extracting twitter users who made diagnosis statements******"    
            diagnosed_users = stas_obj.extractDiagnosedUsers(inputFile)
            if diagnosed_users:
                print "Done extracting users..."
                inputFile.close()

            print "\n******Generating stats for twitter users who made diagnosis statements******"
            processed_diagnosed_users = stas_obj.generate_stats(illness, diagnosed_users)
            outputFile.write(json.dumps(processed_diagnosed_users, sort_keys = True, indent=4, ensure_ascii=False, separators=(',', ':'), default = helper_obj.myconverter))
            print '\n%s Results added to file\n' % len(processed_diagnosed_users)
            outputFile.close()
        elif normalusers and ofile:
           outputFile = codecs.open(ofile, "w+", "utf-8")

           print '\n******Retrieving sample twitter users******'
           normal_user_obj.selectSampleTwitterUsers()
           if os.path.exists(path):
            print "Done writing to file..."

           print '\n******Retrieving random seed nodes from file******'
           seed_node = normal_user_obj.selectRandomSeedNodes(path, 10)
           print seed_node

           print '\n***Conducting breadthTraversal to retrieve random number of filtered followers based on limit and depth **'
           normal_user_obj.breadthTraversal(seed_node, outputFile, 100, 4, 1)
           outputFile.close()

    except arg:
        print 'Arguments parser error ' + arg
    except KeyboardInterrupt:
        print '\nGoodbye!'

    finally:
        print 'All done.. Goodbye!!'


if __name__ == '__main__':
    main(sys.argv[1:])