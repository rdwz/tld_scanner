#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import json
import urllib.request, urllib.error
import sys, getopt, socket
from tqdm import tqdm

domain = ""
https = False
outputfile = ""
tldfile = ""
mode = ""
omode = "json"
iana = False


def scan(tlds, domain, protocols):
    if outputfile != "":
        f = open(outputfile, "w")
    exists = {}
    for tld in tqdm(tlds, unit="domains"):
        for protocol in protocols:
            try:
                ip = ""
                if mode in ["b", "n"]:
                    ip = socket.gethostbyname(domain + tld)
                if ip != "127.0.53.53":
                    target = protocol + domain + tld.lower()
                    if mode != "n":
                        urllib.request.urlopen(target)
                    exists[target] = ip
                    # print (target+" "+ip)
            except Exception as e:
                print(e)
    if outputfile != "":
        if omode == "json":
            f.write(json.dumps(exists))
        elif omode == "jsonarray":
            f.write(json.dumps(list(exists)))
        elif omode == "plain":
            for key in exists:
                f.write("{0}\n".format(key))
        f.close()
        print("Wrote results to '" + outputfile + "' as " + omode)
    print("")
    if omode == "plain":
        for key in exists:
            print("{0}".format(key))
    elif omode == "json":
        print(json.dumps(exists))
    elif omode == "jsonarray":
        print(json.dumps(list(exists)))
    return exists


def print_header():
    print("  _____ _    ______  _____ _____   ___   _   _  _   _  ___________  ")
    print(" |_   _| |   |  _  \/  ___/  __ \ / _ \ | \ | || \ | ||  ___| ___ \ ")
    print("   | | | |   | | | |\ `--.| /  \// /_\ \|  \| ||  \| || |__ | |_/ / ")
    print("   | | | |   | | | | `--. \ |    |  _  || . ` || . ` ||  __||    /  ")
    print("   | | | |___| |/ / /\__/ / \__/\| | | || |\  || |\  || |___| |\ \  ")
    print("   \_/ \_____/___/  \____/ \____/\_| |_/\_| \_/\_| \_/\____/\_| \_| ")


def main(argv):
    global domain, https, outputfile, tldfile, mode, iana, omode
    c = False
    n = False
    b = False
    try:
        opts, args = getopt.getopt(argv, "fbncsd:o:i:m:")
    except getopt.GetoptError:
        _show_help()
    for opt, arg in opts:
        if opt == "-s":
            https = True
        elif opt in ("-o"):
            outputfile = arg
        elif opt in ("-d"):
            domain = arg
        elif opt in ("-i"):
            tldfile = arg
        elif opt in ("-m"):
            omode = arg.lower()
        elif opt in ("-b"):
            b = True
        elif opt in ("-c"):
            c = True
        elif opt in ("-n"):
            n = True
        elif opt in ("-f"):
            iana = True
    mode = "b"  # DEFAULT
    if b or (n and c):
        mode = "b"
    elif n:
        mode = "n"
    elif c:
        mode = "c"
    if omode not in ["json", "jsonarray", "plain"]:
        omode = "json"


def _show_help():
    print("tld_scanner.py  [-d <domain>] [-o <outputfile>] [-m <outputmode>] [-i <tldfile>] [-n] [-c] [-b] [-s] [-f]")
    print("")
    print("Scan for possible TLDs of a given domain name")
    print("")
    print('-d <domain>       | Specifiy the domain name, example: "google"')
    print("-o <outputfile>   | Write results into <outputfile>")
    print("-i <tldfile>      | Use your own custom TLD list")
    print("                    One TLD per line, no other seperators, case insensitive")
    print("-m <outputmode>   | Sets the output mode, defaults to 'json'")
    print("                    json      - json objects, key = url and value = ip")
    print("                    jsonarray - json array, entries = urls")
    print("                    plain     - plain text, one url per line")
    print("-f                | Use the newest and complete list of TLDs from IANA")
    print("                    This will take quite some time")
    print("-n                | Does a name lookup and prints the ip (fastest)")
    print("-c                | Tries to connect to the host directly")
    print("-b                | Default: Does a namelookup and then tries to connect")
    print("                    prints the IP")
    print("-s                | Check for HTTPS too")

    sys.exit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
    print_header()
    surpressCTldMsg = False
    if iana:
        try:
            print("Getting the newest TLD's from iana.org . . .")
            f = urllib.request.urlopen(
                "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
            )
            data = f.read()
            with open("tld_scanner_list.txt", "wb") as list:
                list.write(data)
        except Exception as e:
            print(e)
            print("Please check your network connectivity (or https://data.iana.org is down)!")
            sys.exit(2)
    if iana == False and tldfile == "":
        tldfile = "data/ccTLDs.txt"
        print("Using country code TLDs")
        surpressCTldMsg = True
    try:
        if tldfile != "":
            try:
                tlds = [line.rstrip("\n") for line in open(tldfile)]
            except Exception as e:
                print("Inputfile doesn't exist / not readable")
                sys.exit(2)
            if not surpressCTldMsg:
                print(f"Using custom TLD List: {tlds}")
        else:
            tlds = [line.rstrip("\n") for line in open("tld_scanner_list.txt")]
            print((tlds.pop(0)))
        print("")
        if mode == "c":
            print("Mode: Connecting to host")
        if mode == "b":
            print("Mode: Name lookup + connecting to host")
        if mode == "n":
            print("Mode: Name lookup only")
        protocols = ["http://", "https://"] if https else ["http://"]
        print(f"Using the following protocol(s): {protocols}")
        print(domain)
        if domain == "":
            print("")
            domain = input("Enter Domain name (example 'google'): ")
        else:
            print(("\nUsing domain: " + domain))
        domain = f"{domain}."
        print("")
        start_time = time.time()
        scan(tlds, domain, protocols)
        print(("\n--- %s seconds ---" % (time.time() - start_time)))
    except Exception as e:
        print(e)
        print("CTRL-C or exception")
