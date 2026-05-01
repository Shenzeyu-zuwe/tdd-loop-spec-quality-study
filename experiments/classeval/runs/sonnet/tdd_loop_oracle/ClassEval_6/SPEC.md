# ClassEval_6 — AvgPartition

## Class description
```
"""
    This is a class that partitions the given list into different blocks by specifying the number of partitions, with each block having a uniformly distributed length.
    """
```

## Required imports (prepend to solution.py)
```python

```

## Skeleton (to implement)
```python
class AvgPartition:
    """
    This is a class that partitions the given list into different blocks by specifying the number of partitions, with each block having a uniformly distributed length.
    """

    def __init__(self, lst, limit):
        """
        Initialize the class with the given list and the number of partitions, and check if the number of partitions is greater than 0.
        """
        self.lst = lst
        self.limit = limit

    def setNum(self):
        """
        Calculate the size of each block and the remainder of the division.
        :return: the size of each block and the remainder of the division, tuple.
        >>> a = AvgPartition([1, 2, 3, 4], 2)
        >>> a.setNum()
        (2, 0)

        """


    def get(self, index):
        """
        calculate the size of each block and the remainder of the division, and calculate the corresponding start and end positions based on the index of the partition.
        :param index: the index of the partition,int.
        :return: the corresponding block, list.
        >>> a = AvgPartition([1, 2, 3, 4], 2)
        >>> a.get(0)
        [1, 2]

        """
```

## Target file
`solution.py` — write the completed class here. Do **not** modify
any other file in the project root.

## Verification discipline
Every test intent in feature_list.json is a **RUNTIME CHECK**. The
Tester must write a temp Python script, execute it via the Bash
tool, and compare actual stdout to expected. Code review alone is
never sufficient.