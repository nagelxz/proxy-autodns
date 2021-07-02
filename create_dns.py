import os, sys, requests, digitalocean, re, pydig, logging, logging.config
from time import sleep
from datetime import datetime

LOG_CONF = {
    "version": 1,
    "formatters" : {
        "dns" : {
            "format" : "%(asctime)s %(levelname)s : %(message)s"
        }
    },
    "handlers" : {
        "console" : {
            "level" : "INFO", 
            "formatter" : "dns",
            "class" : "logging.StreamHandler",
            "stream" : "ext://sys.stdout"
        },
        "file" : {
            "level" : "INFO",
            "formatter" : "dns",
            "class" : "logging.FileHandler",
            "filename" : "create_dns.log"
        }
    },
    "loggers" : {
        "" : {
            "handlers" : ["console","file"]
        }
    }
}

logging.config.dictConfig(LOG_CONF)

domain_to_manage = "example.com"
subdomains_to_add = []

# I'd use r-string here but then formatting doesn't work properly
pattern = f".*\.{domain_to_manage.split('.')[0]}\.{domain_to_manage.split('.')[1]}"

with open("Caddyfile", 'r') as file:
    for index,line in enumerate(file):
        if re.search( pattern , line.strip() ):
           subdomains_to_add.append(re.search( pattern , line.strip()).group().split(".{}".format(domain_to_manage))[0])

# #digitalocean part

do_token=os.environ.get("DIGITALOCEAN_ACCESS_TOKEN", None)

if do_token is None:
    logging.warning("Something is wrong with your configuration and your token is missing")
    logging.error("aborting")
    sys.exit(1)

ip_addr = requests.get("http://icanhazip.com").text.strip()

try:
    domain_control = digitalocean.Domain(token=do_token, name=domain_to_manage)
except:
    logging.error("Something is wrong.")
    logging.error("Unable to authenticate with the provided token")
    sys.exit(1)

recordsfetch = domain_control.get_records()
record_names = {}

for r in recordsfetch: 
    record_names.update({r.name : r.data})

for subdomain in subdomains_to_add:

    if subdomain not in record_names.keys():
        new_record = domain_control.create_new_domain_record(type='A', name=subdomain, data=ip_addr, ttl=90)

        logging.info(new_record)
        logging.info(f"waiting for propagation of subdomain {subdomain} ")
        propagation_time = 120
        sleep(propagation_time)

        logging.info("checking if the record is live")

        check = pydig.query(f"{subdomain}.{domain_to_manage}", 'A')
        if len(check) > 0:
            if ip_addr not in check:
                logging.warn("success is not in the cards. Please try again and/or adjust propagation time")
                sys.exit(1)
            else:
                logging.info("success!")
                recordsfetch = domain_control.get_records()
                for r in recordsfetch:
                    if r.name == subdomain:
                        r.ttl = 360
                        r.save()

    else:
        logging.info(f"nothing to do, subdomain {subdomain} exists".format(subdomain))
