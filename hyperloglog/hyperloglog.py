import math, hashlib
import csv

class HyperLogLog:
    def __init__(self, precision):
        self.precision = precision
        self.num_buckets = 1 << precision
        self.buckets = [0] * self.num_buckets
        
        if precision == 4:
            self.alpha = 0.673
        elif precision == 5:
            self.alpha = 0.697
        elif precision == 6:
            self.alpha = 0.709
        else:
            self.alpha = 0.7213 / (1 + 1.079 / self.num_buckets)

    def _hash(self, item):
        # 256 bit hash
        return int(hashlib.sha256(str(item).encode('utf-8')).hexdigest(), 16)

    def _get_bucket_and_rank(self, hash_value):
        # Get bucket index
        bucket = hash_value & (self.num_buckets - 1)

        # Get rank, the leftmost position of bit 1
        remaining_hash = hash_value >> self.precision
        rank = self._leading_zeroes(remaining_hash) + 1
        return bucket, rank

    def _leading_zeroes(self, value: int):
        max_bit_length = 256 - self.precision
        if value == 0:
            return max_bit_length
        return max_bit_length - value.bit_length()

    def add(self, item):
        hash_value = self._hash(item)
        bucket, rank = self._get_bucket_and_rank(hash_value)
        self.buckets[bucket] = max(self.buckets[bucket], rank)

    def count(self):
        z = sum(2.0 ** -bucket for bucket in self.buckets)
        estimate = self.alpha * (self.num_buckets ** 2) / z

        # Correction for small estimate
        if estimate <= 2.5 * self.num_buckets:
            num_zero_buckets = self.buckets.count(0)
            if num_zero_buckets > 0:
                estimate = self.num_buckets * math.log(self.num_buckets / num_zero_buckets)

        return int(estimate)

if __name__ == "__main__":
    csv.field_size_limit(10 ** 7)

    # Simple sets
    purchase_set = set()
    invoicenum_set = set()
    stockcode_set = set()

    # Hyperloglogs
    PRECISION = 16
    purchase_hll = HyperLogLog(PRECISION)
    invoicenum_hll = HyperLogLog(PRECISION)
    stockcode_hll = HyperLogLog(PRECISION)

    # Read csv and add purchases
    with open('OnlineRetail.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            purchase = ','.join(row)
            purchase_set.add(purchase)
            purchase_hll.add(purchase)

            invoicenum = row[0]
            invoicenum_set.add(invoicenum)
            invoicenum_hll.add(invoicenum)

            stockcode = row[1]
            stockcode_set.add(stockcode)
            stockcode_hll.add(stockcode)

    print("     Real purchase count:", len(purchase_set))
    print("Estimated purchase count:", purchase_hll.count())
    print("     Real invoice no. count:", len(invoicenum_set))
    print("Estimated invoice no. count:", invoicenum_hll.count())
    print("     Real stock code count:", len(stockcode_set))
    print("Estimated stock code count:", stockcode_hll.count())
