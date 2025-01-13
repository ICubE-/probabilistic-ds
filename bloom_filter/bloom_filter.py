import math, hashlib, bitarray
import csv, re
import time, random, string

class BloomFilter:
    def __init__(self, num_items, false_positive_rate):
        # Calculate the filter size and number of hash functions
        self.size = self._get_size(num_items, false_positive_rate)
        self.num_hashes = self._get_num_hashes(self.size, num_items)
        # Initialize bit array
        self.bit_array = bitarray.bitarray(self.size)
        self.bit_array.setall(0)

    def _get_size(self, num_items, false_positive_rate):
        # m = - (n * log(p)) / log(2 ^ log(2))
        return int(-(num_items * math.log(false_positive_rate)) / math.log(2 ** math.log(2)))

    def _get_num_hashes(self, size, num_items):
        # k = (m / n) * log(2)
        return int((size / num_items) * math.log(2))

    def _hashes(self, item):
        for i in range(self.num_hashes):
            digest = hashlib.sha256(f"{item}{i}".encode()).hexdigest()
            yield int(digest, 16) % self.size

    def add(self, item):
        for hash_value in self._hashes(item):
            self.bit_array[hash_value] = 1

    def contains(self, item):
        return all(self.bit_array[hash_value] for hash_value in self._hashes(item))

if __name__ == "__main__":
    NUM_POSITIVE_TEST = 10_000
    NUM_NEGATIVE_TEST = 10_000

    csv.field_size_limit(10 ** 7)

    # Simple set
    email_set = set()

    # Read csv and add emails
    with open('emails.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            message = row['message']

            from_matches = re.findall(r'(?<=From: )[\w\.-]+@[\w\.-]+(?:,\s*[\w\.-]+@[\w\.-]+)*', message)
            to_matches = re.findall(r'(?<=To: )[\w\.-]+@[\w\.-]+(?:,\s*[\w\.-]+@[\w\.-]+)*', message)

            for match in from_matches:
                for email in match.split(','):
                    email = email.strip()
                    email_set.add(email)

            for match in to_matches:
                for email in match.split(','):
                    email = email.strip()
                    email_set.add(email)

    num_items = len(email_set)

    print("")
    print(f"Number of email addresses: {num_items}")
    print("")

    # Simple list
    email_list = []

    # Bloom filter
    FALSE_POSITVE_RATE = 0.001
    email_filter = BloomFilter(num_items, FALSE_POSITVE_RATE)

    for email in email_set:
        email_list.append(email)
        email_filter.add(email)

    # Extract some emails
    emails_positive = []
    i = 0
    for email in email_set:
        if i >= NUM_POSITIVE_TEST:
            break
        emails_positive.append(email)
        i += 1

    # print(emails_positive)

    # Check time of the membership query
    time_start_set = time.time()
    for email in emails_positive:
        assert email in email_set
    time_end_set = time.time()
    elapsed_positive_set = time_end_set - time_start_set
    time_start_list = time.time()
    for email in emails_positive:
        assert email in email_list
    time_end_list = time.time()
    elapsed_positive_list = time_end_list - time_start_list
    time_start_filter = time.time()
    for email in emails_positive:
        assert email_filter.contains(email)
    time_end_filter = time.time()
    elapsed_positive_filter = time_end_filter - time_start_filter

    print(f"Positive queries ({NUM_POSITIVE_TEST})")
    print(f"Simple set: {elapsed_positive_set} s")
    print(f"Simple list: {elapsed_positive_list} s")
    print(f"Bloom filter: {elapsed_positive_filter} s")
    print("")

    # Make random strings
    str_negative = []
    for _ in range(NUM_NEGATIVE_TEST):
        rand_str = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=20))
        str_negative.append(rand_str)

    # Check time of the membership query
    time_start_set = time.time()
    for email in str_negative:
        assert not (email in email_set)
    time_end_set = time.time()
    elapsed_negative_set = time_end_set - time_start_set
    time_start_list = time.time()
    for email in str_negative:
        assert not (email in email_list)
    time_end_list = time.time()
    elapsed_negative_list = time_end_list - time_start_list
    false_positive_cnt = 0
    time_start_filter = time.time()
    for email in str_negative:
        if email_filter.contains(email):
            false_positive_cnt += 1
    time_end_filter = time.time()
    elapsed_negative_filter = time_end_filter - time_start_filter

    print(f"Negative queries ({NUM_NEGATIVE_TEST})")
    print(f"Simple set: {elapsed_negative_set} s")
    print(f"Simple list: {elapsed_negative_list} s")
    print(f"Bloom filter: {elapsed_negative_filter} s")
    print(f"- False positive rate: {false_positive_cnt / NUM_NEGATIVE_TEST}")
