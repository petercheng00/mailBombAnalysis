import csv
import datetime
import matplotlib.pyplot as plt
import re
from collections import Counter


email_address_regex = r'[\w\.-]+@[\w\.-]+\.\w+'

names = []
domains = []
tlds = []
num_missing = 0
with open('data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) # skip header
    for row in reader:
        ms = int(row[0])
        from_field = row[1]
        reply_to_field = row[2]
        # Search for an email address in from_field, or fall back to reply-to
        match = re.search(email_address_regex, from_field) or re.search(email_address_regex, reply_to_field)
        if match is not None:
            addr = match.group(0)
            name, domain = addr.split('@')
            tld = addr.split('.')[-1]
            names.append(name)
            domains.append(domain)
            tlds.append(tld)
        else:
            num_missing += 1

print(f'Read {len(names)} email addresses ({num_missing} missing)')


name_counter = Counter(names)
domain_counter = Counter(domains)
tld_counter = Counter(tlds)

def saveplot(title, counter, num, filename):
    plt.figure()
    plt.title(title)
    plt.bar(*zip(*counter.most_common(num)))
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(filename, dpi=200)

saveplot('Top 10 TLDs', tld_counter, 10, 'tld.jpg')
saveplot('Top 25 Domains', domain_counter, 25, 'domains.jpg')
saveplot('Top 25 Names', name_counter, 25, 'names.jpg')
