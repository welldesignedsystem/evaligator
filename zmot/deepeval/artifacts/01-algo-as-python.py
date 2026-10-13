from collections import Counter
import heapq

def top_k_frequent(strings, k):
    counts = Counter(strings)
    # heapq.nlargest is O(n log k); ties broken alphabetically for stable output
    return heapq.nlargest(k, counts, key=lambda s: (counts[s], -ord(s[0]) if s else 0))

# Simpler version using Counter.most_common
def top_k_frequent_simple(strings, k):
    return [s for s, _ in Counter(strings).most_common(k)]

words = ["apple", "banana", "apple", "cherry", "banana", "apple", "date"]
print(top_k_frequent_simple(words, 2))   # ['apple', 'banana']