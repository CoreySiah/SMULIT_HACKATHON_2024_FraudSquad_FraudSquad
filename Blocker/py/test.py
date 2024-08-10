import json
import csv
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import tldextract
import re
import socket
import ssl
from datetime import datetime
import certifi
import whois

# File paths
manifest_path = './Blocker/manifest.json'
reportsCsv_path = './data/reports.csv'
logsCsv_path = './data/logs.csv'
whitelistCsv_path = './data/whitelist.csv'
blacklistCsv_path = './data/blacklist.csv'
greylistCsv_path = './data/greylist.csv'

def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def getURLs(URLS,path):
    with open(path, mode='r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            url = row.get('URL')  # Adjust the column name if necessary
            if url:
                URLS.append(url)
def get_ssl_certificate_info(domain):
    try:
        # Create an SSL context using certifi's CA bundle
        ctx = ssl.create_default_context(cafile=certifi.where())
        
        # Create a TCP connection and wrap it in an SSL context
        with socket.create_connection((domain, 443)) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                # Get the peer certificate
                cert = ssock.getpeercert()
                return cert
                
    except Exception as e:
        print(f"Error retrieving SSL certificate for {domain}: {e}")
        return None

def get_domain_age(domain):
    try:
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date
        # Some domains might return a list of creation dates
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        # Calculate the age of the domain
        age = (datetime.now() - creation_date).days // 365
        return creation_date, age
    except Exception as e:
        print(f"Error retrieving information for {domain}: {e}")
        return None, None

def analyze_url(url):
    suscount = 0
    print(f"\nURL info: {url}")
    domain_info = tldextract.extract(url)
    domain = f"{domain_info.domain}.{domain_info.suffix}"
    subdomain = domain_info.subdomain
    print(f"Domain: {domain}")
    print(f"Subdomain: {subdomain}")

    # URL Features
    if len(url) > 35:
        print("Warning: URL is unusually long.")
        suscount+=1
    if re.search(r"@|-|_|%|=|&|#", url):
        print("Warning: URL contains suspicious characters.")
        suscount+=1
    
    # SSL Certificate Info
    ssl_info = get_ssl_certificate_info(domain)
    if ssl_info:
        issuer = ssl_info.get('issuer')
        print(f"SSL Certificate Issuer: {issuer}")
        not_before = ssl_info.get('notBefore')
        not_after = ssl_info.get('notAfter')
        print(f"SSL Certificate Valid From: {not_before}")
        print(f"SSL Certificate Expires On: {not_after}")
    else:
        suscount+=1
    # Scrape and Analyze Page Content
    try:
        if url.endswith("/*"):
            url = url[:-2]  # Remove the last two characters (/*)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Page Title and Meta Tags
        title = soup.title.string if soup.title else "No Title Found"
        print(f"Page Title: {title}")
        
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            print(f"Meta Description: {meta_description['content']}")
        
        # Check for Forms
        forms = soup.find_all('form')
        for form in forms:
            action_url = form.get('action')
            if action_url:
                action_domain = urlparse(action_url).netloc
                if action_domain and action_domain != domain:
                    print(f"Warning: Form action URL points to a different domain: {action_url}")
        
        # Check for Suspicious Links
        links = soup.find_all('a', href=True)
        hrefCount = 0
        for link in links:
            href = link['href']
            if href.startswith("http") and domain not in href:
                print(f"Warning: External link found: {href}")
                hrefCount+=1
            if href == "#":
                print(f"# found:")
                hrefCount+=1
        if hrefCount>=2:
            suscount+=1
    
        
        # Check for External Resources
        ECount = 0
        external_resources = soup.find_all(['script', 'link', 'img'], src=True)
        for resource in external_resources:
            src = resource['src']
            if src.startswith("http") and domain not in src:
                print(f"Warning: External resource found: {src}")
                ECount+=1
        if ECount>=2:
            suscount+=1


        #domain age
        # domainn = url.split("//")[-1].split("/")[0]
        creation_date, age = get_domain_age(domain)
        if creation_date:
            print(f"Domain: {domain}")
            print(f"Creation Date: {creation_date}")
            print(f"Domain Age: {age} years")
        else:
            print(f"Could not retrieve domain age for {domain}") 
            age = 0
        if age<=1:
            suscount+=2
        print(suscount)
    except Exception as e:
        print(f"Error analyzing {url}: {e}")
        return -1
    return suscount

#load blacklist URL
blacklistURL = []
getURLs(blacklistURL,blacklistCsv_path)
# Load Whitelist URLs
whitelistURL = []
getURLs(whitelistURL,whitelistCsv_path)

# Load URLs from reports CSV
urls = []
with open(reportsCsv_path, mode='r') as f:
    csv_reader = csv.DictReader(f)
    for row in csv_reader:
        url = get_base_url(row.get('URL')) + "/*"
        if url not in whitelistURL and url not in blacklistURL: # Check against whitelist URLs
            urls.append(url)
# move to logs
rows_to_keep = []
with open(reportsCsv_path, mode='r') as source_file:
    csv_reader = csv.reader(source_file)
    with open(logsCsv_path, mode='a', newline='') as destination_file:
        csv_writer = csv.writer(destination_file)
        for index, row in enumerate(csv_reader):
            if index == 0:
                rows_to_keep.append(row)
            else:
                csv_writer.writerow(row)
# Write back the rows to keep to the source file
with open(reportsCsv_path, mode='w') as f:
    csv_writer = csv.writer(f)
    for row in rows_to_keep:
        csv_writer.writerow(row)

for url in urls:
    x = analyze_url(url)
    if x <3 and x!=-1:
        with open(greylistCsv_path, mode='a', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([url])
    else:
        with open(blacklistCsv_path, mode='a', newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([url])


blacklistURL = []
getURLs(blacklistURL,blacklistCsv_path)

# Load manifest.json
with open(manifest_path, 'r') as f:
    manifest_data = json.load(f)
# Add URLs to matches in manifest.json
matches = manifest_data['content_scripts'][0]['matches']
for url in blacklistURL:
    if url not in matches:
        matches.append(url)

# Save the updated manifest.json
with open(manifest_path, 'w') as f:
    json.dump(manifest_data, f, indent=4)

print("URLs have been added to manifest.json successfully.")