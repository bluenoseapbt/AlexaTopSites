System that analyzes the Alexa top 1,000 sites.  The analysis includes:

Per Site
  Word count of the first page and rank across all the sites based off the word count
  Duration of the scan

Across All Sites
  AVG word count of the first page
  Top 20 HTTP headers and the percentage of sites they were seen in
  Duration of the entire scan



## Installing environment and running code
Add AWS credentials to ~/.aws/credentials

## contents of ~/.aws/credentials (add your id and key)
[MyProfile]
aws_access_key_id = 
aws_secret_access_key = 


From the root project directory
* Create virtualenv (see [virtualenv](https://virtualenv.pypa.io/en/latest/) docs for more info)
```bash
python -m virtualenv venv
```
* Activate the virtualenv
```bash
source venv/bin/activate
```
* Install requirements
```bash
pip install -r requirements.txt


* Running from command line (with no arguments it will default to top 1000 sites and top 20 headers)
python alexa_top_sites.py

or specifying number of sites and size of header
python alexa_top_sites.py -S 50 -H 30
