import csv
import matplotlib.pyplot as plt

epoch_ms = []
with open('data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)
    next(reader) # skip header
    for row in reader:
        epoch_ms.append(int(row[0]))

plt.hist(epoch_ms, normed=True, bins=30)
plt.show()
