from algokit.core import binary_search, merge_sort, two_sum


def test_binary_search_found() -> None:
    assert binary_search([1, 3, 5, 7], 5) == 2


def test_binary_search_not_found() -> None:
    assert binary_search([1, 3, 5, 7], 6) == -1


def test_merge_sort() -> None:
    assert merge_sort([4, 2, 9, 1]) == [1, 2, 4, 9]


def test_two_sum() -> None:
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)