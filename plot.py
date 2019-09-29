import csv
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import time

# started on august 12, so get epoch_ms for august 11
start_epoch_ms = datetime.datetime(2019, 8, 1, 0, 0).timestamp() * 1000
end_epoch_ms = datetime.datetime(2019, 8, 28, 0, 0).timestamp() * 1000

epoch_ms = []
with open('data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) # skip header
    for row in reader:
        ms = int(row[0])
        if ms > start_epoch_ms and ms < end_epoch_ms:
            epoch_ms.append(ms)

hist_bins = np.arange(start_epoch_ms, end_epoch_ms, 1000 * 60 * 60)
plt.hist(epoch_ms, bins=hist_bins)
plt.yscale('log')
plt.margins(x=0)
plt.gca().xaxis.set_major_formatter(
    mtick.FuncFormatter(lambda ms, _: time.strftime("%m-%d",time.localtime(ms/1000)))
)

plt.ylabel('Emails/hour (log scale)')
plt.xlabel('Hour')
plt.title('Spam Emails/Hour in August')

plt.show()
