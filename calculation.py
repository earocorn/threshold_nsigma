import csv
import math
from queue import Queue

rpm_data_filename = 'rpm_sample.csv'

rpm_data = csv.reader(open(rpm_data_filename))

intervals = 0
holdin = 0
n_sigma = 0


def print_threshold(background_message):
    if len(background_message) > 0:
        background_sum = 0
        for index in range(1, len(background_message)):
            background_sum += int(background_message[index])
        sqrt_background_sum = math.sqrt(background_sum)

        threshold = background_sum + (n_sigma * sqrt_background_sum)
        print(f'Threshold (SUM): {threshold}')


def print_sigma(background_message, foreground):
    if foreground.full() and len(background_message) > 0:

        # Get one second of foreground = one second of background
        one_second_foreground = [0, 0, 0, 0]
        for item in foreground.queue:
            for index in range(0, 4):
                one_second_foreground[index] += int(item[index+1])

        # Get sums
        foreground_sum = sum(one_second_foreground)
        background_sum = 0
        for index in range(1, len(background_message)):
            background_sum += int(background_message[index])

        sigma = (foreground_sum - background_sum) / math.sqrt(background_sum)
        print(f'Sigma: {sigma}')


latest_background = list()
foreground_batch = Queue(maxsize=5)

for row in rpm_data:

    # Update setup values
    if row[0] == 'SG1':
        intervals = int(row[3])
        holdin = int(row[4])
        n_sigma = float(row[5])

    # Send new foreground data as one second of gamma counts (queue of length 5)
    elif row[0] == 'GS' or row[0] == 'GA':
        foreground_batch.put(row)

    # Print threshold using latest background
    elif row[0] == 'GB':
        latest_background = row
        print_threshold(latest_background)

    print_sigma(latest_background, foreground_batch)

    if foreground_batch.full():
        foreground_batch.get()
