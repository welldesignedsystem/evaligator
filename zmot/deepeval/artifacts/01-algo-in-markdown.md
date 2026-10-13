# Algorithm: 
1. Start with the given list of strings and the value of K.
2. Create a frequency map to store each unique string and its occurrence count.
3. Iterate through the list and count the occurrences of every string.
4. Create an empty min-heap to store the top K strings.
5. Iterate through each unique string in the frequency map.
6. Insert the string and its frequency into the min-heap.
7. If the heap contains more than K elements, remove the element with the smallest frequency.
8. Repeat steps 6–7 until all unique strings have been processed.
9. Extract the remaining K strings from the heap.
10. Return the resulting strings, optionally sorted by frequency in descending order.
Time Complexity: \(O(n + m\log K + K\log K)\), where \(n\) is the total number of strings and \(m\) is the number of unique strings.
Space Complexity: \(O(m)\), where \(m\) is the number of unique strings.

```Important Note:``` Every function must have a comment section description of what it does.