import csv
import datetime
import matplotlib.pyplot as plt
import re
from collections import Counter


email_address_regex = r'[\w\.-]+@[\w\.-]+\.\w+'

# started on august 12
start_epoch_ms = datetime.datetime(2019, 8, 12, 0, 0).timestamp() * 1000
end_epoch_ms = datetime.datetime(2019, 8, 13, 0, 0).timestamp() * 1000

names = []
domains = []
tlds = []
names_day1 = []
domains_day1 = []
tlds_day1 = []
num_missing = 0
num_missing_day1 = 0
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
            if ms > start_epoch_ms and ms < end_epoch_ms:
                names_day1.append(name)
                domains_day1.append(domain)
                tlds_day1.append(tld)
        else:
            num_missing += 1
            if ms > start_epoch_ms and ms < end_epoch_ms:
                num_missing_day1 += 1

print(f'Read {len(names)} email addresses ({num_missing} missing)')
print(f'Read {len(names_day1)} email addresses ({num_missing_day1} missing)')


name_counter = Counter(names)
domain_counter = Counter(domains)
tld_counter = Counter(tlds)
name_counter_day1 = Counter(names_day1)
domain_counter_day1 = Counter(domains_day1)
tld_counter_day1 = Counter(tlds_day1)

print(len(names))
print(len(names_day1))

plt.figure()
plt.title('TLD Counts')
plt.bar(*zip(*tld_counter.most_common()))
plt.xticks(rotation=90)

plt.figure()
plt.title('TLD Counts, Day 1')
plt.bar(*zip(*tld_counter.most_common()))
plt.xticks(rotation=90)

plt.figure()
plt.title('Top 100 Domains')
plt.bar(*zip(*domain_counter_day1.most_common(100)))
plt.xticks(rotation=90)

plt.figure()
plt.title('Top 100 Domains, Day 1')
plt.bar(*zip(*domain_counter_day1.most_common(100)))
plt.xticks(rotation=90)

plt.figure()
plt.title('Top 100 Names')
plt.bar(*zip(*name_counter_day1.most_common(100)))
plt.xticks(rotation=90)

plt.figure()
plt.title('Top 100 Domains, Day 1')
plt.bar(*zip(*name_counter_day1.most_common(100)))
plt.xticks(rotation=90)
plt.show()
