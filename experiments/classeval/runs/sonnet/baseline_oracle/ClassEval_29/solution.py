from collections import Counter

class DataStatistics:
    def mean(self, data):
        return round(sum(data) / len(data), 2)

    def median(self, data):
        s = sorted(data)
        n = len(s)
        mid = n // 2
        if n % 2 == 1:
            return round(s[mid], 2)
        return round((s[mid - 1] + s[mid]) / 2, 2)

    def mode(self, data):
        counts = Counter(data)
        max_count = max(counts.values())
        return sorted(k for k, v in counts.items() if v == max_count)