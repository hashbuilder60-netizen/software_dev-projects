def binary_search(sorted_values: list[int], target: int) -> int:
    low = 0
    high = len(sorted_values) - 1

    while low <= high:
        mid = (low + high) // 2
        value = sorted_values[mid]
        if value == target:
            return mid
        if value < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


def merge_sort(values: list[int]) -> list[int]:
    if len(values) <= 1:
        return values[:]

    mid = len(values) // 2
    left = merge_sort(values[:mid])
    right = merge_sort(values[mid:])

    merged: list[int] = []
    i = 0
    j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged


def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    seen: dict[int, int] = {}
    for idx, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], idx)
        seen[num] = idx
    return None