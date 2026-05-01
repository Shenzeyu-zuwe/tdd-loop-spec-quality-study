# TDDLoop Report

| | |
|---|---|
| Result | **ALL PASSED** |
| Change | ClassEval_10 |
| Environment | python_local |
| Start | 2026-04-27 10:04:05 |
| End | 2026-04-27 10:11:50 |
| Duration | 7m44s |
| Iterations | 4 |
| Model | haiku |
| Cost | $0.7690 |
| Sessions | 28 |

## Features (4/4 passed)

### [PASSED] F-001 Method `clean_non_binary_chars(self)` on class `BinaryDataProcessor` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-001-01** ORACLE TEST RUN for `BinaryDataProcessor.clean_non_binary_chars`.

Write the following Python code to a temp file (e.g. `_oracle_clean_non_binary_chars.py`) in the project root and execute `python _oracle_clean_non_binary_chars.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import BinaryDataProcessor

class BinaryDataProcessorTestCleanNonBinaryChars(unittest.TestCase):
    def test_clean_non_binary_chars(self):
        bdp = BinaryDataProcessor("01101000daf3e4r01100101011011000110110001101111")
        self.assertEqual(bdp.binary_string, "0110100001100101011011000110110001101111")

    def test_clean_non_binary_chars_2(self):
        bdp = BinaryDataProcessor("01101000daf3e4r01100101011011addf0110001d1111")
        self.assertEqual(bdp.binary_string, "011010000110010101101101100011111")

    def test_clean_non_binary_chars_3(self):
        bdp = BinaryDataProcessor("0sd1000daf3e4r01100101011011addf0110001d1111")
        self.assertEqual(bdp.binary_string, "010000110010101101101100011111")

    def test_clean_non_binary_chars_4(self):
        bdp = BinaryDataProcessor("sdsdf")
        self.assertEqual(bdp.binary_string, "")

    def test_clean_non_binary_chars_5(self):
        bdp = BinaryDataProcessor("0")
        self.assertEqual(bdp.binary_string, "0")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BinaryDataProcessorTestCleanNonBinaryChars)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 unit tests passed successfully. The clean_non_binary_chars method correctly removes all non-binary characters (anything other than '0' and '1') from the input string via the list comprehension f

### [PASSED] F-002 Method `calculate_binary_info(self)` on class `BinaryDataProcessor` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-002-01** ORACLE TEST RUN for `BinaryDataProcessor.calculate_binary_info`.

Write the following Python code to a temp file (e.g. `_oracle_calculate_binary_info.py`) in the project root and execute `python _oracle_calculate_binary_info.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import BinaryDataProcessor

class BinaryDataProcessorTestCalculateBinaryInfo(unittest.TestCase):
    def test_calculate_binary_info(self):
        bdp = BinaryDataProcessor("0110100001100101011011000110110001101111")
        self.assertEqual(bdp.calculate_binary_info(), {'Zeroes': 0.475, 'Ones': 0.525, 'Bit length': 40})

    def test_calculate_binary_info_2(self):
        bdp = BinaryDataProcessor("0110100001100101011010011111")
        self.assertEqual(bdp.calculate_binary_info(), {'Bit length': 28, 'Ones': 0.5357142857142857, 'Zeroes': 0.4642857142857143})

    def test_calculate_binary_info_3(self):
        bdp = BinaryDataProcessor("01101001111100101011010011111")
        self.assertEqual(bdp.calculate_binary_info(), {'Bit length': 29, 'Ones': 0.6206896551724138, 'Zeroes': 0.3793103448275862})

    def test_calculate_binary_info_4(self):
        bdp = BinaryDataProcessor("011010011111001")
        self.assertEqual(bdp.calculate_binary_info(), {'Bit length': 15, 'Ones': 0.6, 'Zeroes': 0.4})

    def test_calculate_binary_info_5(self):
        bdp = BinaryDataProcessor("0110100111110010")
        self.assertEqual(bdp.calculate_binary_info(), {'Bit length': 16, 'Ones': 0.5625, 'Zeroes': 0.4375})

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BinaryDataProcessorTestCalculateBinaryInfo)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle test cases for BinaryDataProcessor.calculate_binary_info() executed successfully with exit code 0 and unittest reported OK.

### [PASSED] F-003 Method `convert_to_ascii(self)` on class `BinaryDataProcessor` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-003-01** ORACLE TEST RUN for `BinaryDataProcessor.convert_to_ascii`.

Write the following Python code to a temp file (e.g. `_oracle_convert_to_ascii.py`) in the project root and execute `python _oracle_convert_to_ascii.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import BinaryDataProcessor

class BinaryDataProcessorTestConvertToAscii(unittest.TestCase):
    def test_convert_to_ascii(self):
        bdp = BinaryDataProcessor("0110100001100101011011000110110001101111")
        self.assertEqual(bdp.convert_to_ascii(), "hello")

    def test_convert_to_ascii_2(self):
        bdp = BinaryDataProcessor("0110100000100101011011000110110001101111")
        self.assertEqual(bdp.convert_to_ascii(), "h%llo")

    def test_convert_to_ascii_3(self):
        bdp = BinaryDataProcessor("01101000011011010110001001101111")
        self.assertEqual(bdp.convert_to_ascii(), "hmbo")

    def test_convert_to_ascii_4(self):
        bdp = BinaryDataProcessor("01101000011001010110001001101111")
        self.assertEqual(bdp.convert_to_ascii(), "hebo")

    def test_convert_to_ascii_5(self):
        bdp = BinaryDataProcessor("0110100001100101011011000110110001101111")
        self.assertEqual(bdp.convert_to_ascii(), "hello")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BinaryDataProcessorTestConvertToAscii)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle unit tests for convert_to_ascii passed successfully. Exit code 0 with unittest reporting OK.

### [PASSED] F-004 Method `convert_to_utf8(self)` on class `BinaryDataProcessor` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-004-01** ORACLE TEST RUN for `BinaryDataProcessor.convert_to_utf8`.

Write the following Python code to a temp file (e.g. `_oracle_convert_to_utf8.py`) in the project root and execute `python _oracle_convert_to_utf8.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import BinaryDataProcessor

class BinaryDataProcessorTestConvertToUtf8(unittest.TestCase):
    def test_convert_to_utf8(self):
        bdp = BinaryDataProcessor("0110100001100101011011000110110001101111")
        self.assertEqual(bdp.convert_to_utf8(), "hello")

    def test_convert_to_utf8_2(self):
        bdp = BinaryDataProcessor("0110100001100101011011000110110001101001")
        self.assertEqual(bdp.convert_to_utf8(), "helli")

    def test_convert_to_utf8_3(self):
        bdp = BinaryDataProcessor("0110000001100101011011000110110001101111")
        self.assertEqual(bdp.convert_to_utf8(), "`ello")

    def test_convert_to_utf8_4(self):
        bdp = BinaryDataProcessor("0110101101100101011011000110110001101111")
        self.assertEqual(bdp.convert_to_utf8(), "kello")

    def test_convert_to_utf8_5(self):
        bdp = BinaryDataProcessor("0110101101100100011011000110110001101111")
        self.assertEqual(bdp.convert_to_utf8(), "kdllo")

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BinaryDataProcessorTestConvertToUtf8)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle test cases passed successfully. The convert_to_utf8() method correctly converts 8-bit binary chunks to their UTF-8 character equivalents.

## Sessions (28 total, $0.7690)

| # | Role | Feature | Task | Status | Duration | Cost | Session ID |
|---|------|---------|------|--------|----------|------|------------|
| 1 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | 39201949-c10.. |
| 2 | Worker | F-001 | fix 1 tests | error | 1s | $0.0000 | 8be7deb2-258.. |
| 3 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | 96be114f-639.. |
| 4 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | 81fb3d68-ee7.. |
| 5 | Worker | F-002 | fix 1 tests | error | 1s | $0.0000 | 184835ed-7e4.. |
| 6 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | 705a9340-c7a.. |
| 7 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | e5ff1c51-4c3.. |
| 8 | Worker | F-003 | fix 1 tests | error | 1s | $0.0000 | 5c48db8d-cd4.. |
| 9 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | bf71b4be-67c.. |
| 10 | Tester | F-004 | verify T-004-01 | error | 1s | $0.0000 | db31f7a0-391.. |
| 11 | Worker | F-004 | fix 1 tests | error | 1s | $0.0000 | 3036ce1f-23b.. |
| 12 | Tester | F-004 | verify T-004-01 | error | 1s | $0.0000 | c206790f-c59.. |
| 13 | Tester | F-001 | verify T-001-01 | ok | 24s | $0.0446 | 97fa447e-3e3.. |
| 14 | Worker | F-001 | fix 1 tests | ok | 31s | $0.0486 | 4f247bd4-d69.. |
| 15 | Tester | F-001 | verify T-001-01 | ok | 34s | $0.0553 | edb23d82-2da.. |
| 16 | Tester | F-002 | verify T-002-01 | ok | 24s | $0.0448 | 9d90c168-caf.. |
| 17 | Worker | F-002 | fix 1 tests | ok | 29s | $0.0528 | 7cb91b84-468.. |
| 18 | Tester | F-002 | verify T-002-01 | ok | 36s | $0.0565 | afb884ba-b76.. |
| 19 | Tester | F-003 | verify T-003-01 | ok | 26s | $0.0437 | 15c28271-1bd.. |
| 20 | Worker | F-003 | fix 1 tests | ok | 29s | $0.0495 | dc83baae-3e4.. |
| 21 | Tester | F-003 | verify T-003-01 | ok | 26s | $0.0499 | b4ba1431-fe9.. |
| 22 | Tester | F-004 | verify T-004-01 | ok | 23s | $0.0446 | 6b22f8b8-62c.. |
| 23 | Worker | F-004 | fix 1 tests | ok | 22s | $0.0436 | 771db846-7e2.. |
| 24 | Tester | F-004 | verify T-004-01 | ok | 24s | $0.0469 | 9e3932b3-6dc.. |
| 25 | Tester | F-001 | verify T-001-01 | ok | 32s | $0.0620 | e9cb3eee-f7f.. |
| 26 | Tester | F-002 | verify T-002-01 | ok | 24s | $0.0426 | c44a6fef-740.. |
| 27 | Tester | F-003 | verify T-003-01 | ok | 22s | $0.0414 | 3fc85d3e-a47.. |
| 28 | Tester | F-004 | verify T-004-01 | ok | 21s | $0.0423 | e4c1e484-045.. |