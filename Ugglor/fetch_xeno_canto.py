#!/usr/bin/env python3

import argparse, json, os, requests
from urllib.request import urlretrieve

def download(url:str, infile:str, outfile:str, species:str, sex:str, verbose:bool)->bool:
    os.makedirs(species, exist_ok=True)
    tdir = f"{species}/{sex}"
    os.makedirs(tdir, exist_ok=True)
    os.chdir(tdir)
    success = True
    try:
        if verbose:
            print(f"Will download {url} as {outfile}")
        urlretrieve(url, outfile)
    except:
        print(f"File {url} not found") 
        success = False
    os.chdir("../..")
    return success

def fetch(species:str, exclude:list, mykey:str, fetch:int, verbose:bool):
    per_page = 100
    baseurl  = f"https://xeno-canto.org/api/3/recordings?query=sp:\"{species}\"&key={mykey}&per_page={per_page}"
    countries = {}
    country = "cnt"
    sex     = 'sex'
    sexes   = { "male": 0, "female": 0, "uncertain": 0, "female, male": 0, "empty": 0, 'female, male, uncertain': 0, 'female, uncertain': 0, 'male, uncertain': 0 }
    recs    = "recordings"
    # We do not know how many recordings there are for each species, so use a while loop.
    page       = 0
    response   = requests.get(baseurl)
    data       = response.json()
    nfetched   = 0
    while page*per_page < int(data["numRecordings"]):
        if not recs in data:
            continue
        for rec in data[recs]:
            if rec[country] in exclude:
                continue
            if not rec[country] in countries:
                countries[rec[country]] = 1
            else:
                countries[rec[country]] += 1
            if sex in rec:
                if rec[sex] in sexes:
                    sexes[rec[sex]] += 1
                elif len(rec[sex]) == 0:
                    sexes["empty"] += 1
                else:
                    print("Unknown gender '%s'" % rec[sex])
            else:
                sexes["empty"] += 1
            # Now try and download if requested
            if fetch == -1 or nfetched < fetch:
                if rec[sex] in [ "male", "female" ]:
                    outfile = ("%s%05d.%s" % ( rec[sex], sexes[rec[sex]], rec["file-name"][-3:] ) )
                    if download(rec["file"], rec["file-name"], outfile, species, rec[sex], verbose):
                        nfetched += 1
        page    += 1
        # URL for the next page to fetch
        myurl    = baseurl + f"&page={page}"
        response = requests.get(myurl)
        data     = response.json()
    
    print("Species: %s, #countries %d male: %d female: %d" % ( species, len(countries.keys()),
                                                               sexes['male'], sexes['female']) )
    if verbose:
        print(countries)
        print(sexes)

def parse_args():
    parser  = argparse.ArgumentParser(description="""
    Collect data from [xeno-canto](https://xeno-canto.org) (XC) and print information.
    Can now also download sound files, and will store them in directories
    called species/sex (as specified on XC).
    """)
    
    defjson = "owls.json"
    parser.add_argument("-json", "--json", help="Json file with species, default "+defjson, type=str, default=defjson)
    parser.add_argument("-dump_json", "--dump_json", help="Dump Json file with species", type=str, default=None)
    parser.add_argument("-species", "--species", nargs="+", help="Only treat these species", type=str, default=None)
    dvds   = "9af56de7eed0daebc546b722bc6cbd047461237e"
    parser.add_argument("-key", "--key", help="API key for using xeno-canto (check your login page)",type=str, default=dvds)
    parser.add_argument("-v", "--verbose", help="Print more stuff", action="store_true")
    parser.add_argument("-dbg", "--debug", help="Print much more stuff", action="store_true")
    nfetch = 0
    parser.add_argument("-fetch", "--fetch", help="Download at most this many wav files per species and sex, -1 = all, default = "+str(nfetch), type=int, default=nfetch)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    # Input the file with species
    with open(args.json, "r") as inf:
        myowls = json.load(inf)
        # Maybe we need to dump a new copy?
        if args.dump_json:
            with open(args.dump_json, "w") as outf:
                json.dump(myowls, outf, indent=4)
        # Print stuff if really needed
        if args.debug:
            print(myowls)
    # Which species does the user want?
    myspecies = args.species
    if None == myspecies or len(myspecies) == 0:
        myspecies = myowls.keys()
    for owl in myspecies:
        fetch(species=owl, exclude=myowls[owl], mykey=args.key,
              fetch=args.fetch, verbose=args.verbose)

