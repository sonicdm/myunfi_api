import csv
from functools import cache, lru_cache
from timeit import timeit
csv_file = r"G:\Stuff\Coding\Python\brdata.csv"


@cache
def cached_convert_to_number(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def convert_to_number(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

def strings_to_numbers(data, cached=False):
    f = cached_convert_to_number if cached else convert_to_number
    for row in data:
        yield [f(value) for value in row]

def read_csv(csv_file, cached=False):
    with open(csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in strings_to_numbers(reader, cached):
            yield row
with open(csv_file, newline='') as csvfile:
    reader = csv.reader(csvfile)
    data = list(reader)

output = []
# print(list(strings_to_numbers(data)))
print("From Memory No Cache")
print(timeit(lambda: output.append(list(strings_to_numbers(data))), number=1))
print("From Memory Cached")
print(timeit(lambda: output.append(list(strings_to_numbers(data, cached=True))), number=1))
cached_convert_to_number.cache_clear()

print("Compare outputs.. Cached == No Cache")
print(output[0] == output[1])

from_csv_output = []
print("From CSV No Cache")
print(timeit(lambda: from_csv_output.append(list(read_csv(csv_file))), number=1))
print("From CSV Cached")
print(timeit(lambda: from_csv_output.append(list(read_csv(csv_file, cached=True))), number=1))
cached_convert_to_number.cache_clear()


print("Compare outputs.. Cached == No Cache")
print(from_csv_output[0] == from_csv_output[1])



