# TDDLoop Report

| | |
|---|---|
| Result | **ALL PASSED** |
| Change | ClassEval_10 |
| Environment | python_local |
| Start | 2026-04-25 21:45:35 |
| End | 2026-04-25 21:52:12 |
| Duration | 6m37s |
| Iterations | 4 |
| Model | sonnet |
| Cost | $1.2408 |
| Sessions | 16 |

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

  - All 5 unit tests passed with exit code 0 and unittest reported OK. The `clean_non_binary_chars` method correctly strips all non-'0' and non-'1' characters from the binary string.

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

  - All 5 oracle tests passed with exit code 0 and unittest reported OK. The calculate_binary_info method correctly computes zero/one percentages and bit length.

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

  - All 5 oracle tests for `BinaryDataProcessor.convert_to_ascii` passed with exit code 0 and unittest reported OK.

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

  - All 5 oracle tests for `BinaryDataProcessor.convert_to_utf8` passed with exit code 0 and unittest reporting OK.

## Sessions (16 total, $1.2408)

| # | Role | Feature | Task | Status | Duration | Cost | Session ID |
|---|------|---------|------|--------|----------|------|------------|
| 1 | Tester | F-001 | verify T-001-01 | ok | 28s | $0.0861 | a99cd1ce-9a7.. |
| 2 | Worker | F-001 | fix 1 tests | ok | 18s | $0.0641 | f0f3795e-24d.. |
| 3 | Tester | F-001 | verify T-001-01 | ok | 21s | $0.0803 | 8cacfcdd-937.. |
| 4 | Tester | F-002 | verify T-002-01 | ok | 25s | $0.0893 | f371f019-dc6.. |
| 5 | Worker | F-002 | fix 1 tests | ok | 10s | $0.0654 | 1053ead6-dde.. |
| 6 | Tester | F-002 | verify T-002-01 | ok | 22s | $0.0833 | 5650814f-b58.. |
| 7 | Tester | F-003 | verify T-003-01 | ok | 29s | $0.0842 | 30de73d2-079.. |
| 8 | Worker | F-003 | fix 1 tests | ok | 14s | $0.0617 | 3baab616-4b3.. |
| 9 | Tester | F-003 | verify T-003-01 | ok | 23s | $0.0789 | 40a9844c-319.. |
| 10 | Tester | F-004 | verify T-004-01 | ok | 28s | $0.0844 | 7a9477b1-6cc.. |
| 11 | Worker | F-004 | fix 1 tests | ok | 12s | $0.0617 | 4f122c44-550.. |
| 12 | Tester | F-004 | verify T-004-01 | ok | 30s | $0.0793 | 7b1650be-864.. |
| 13 | Tester | F-001 | verify T-001-01 | ok | 20s | $0.0816 | 3d77d40e-515.. |
| 14 | Tester | F-002 | verify T-002-01 | ok | 23s | $0.0821 | fe44ca5a-8fd.. |
| 15 | Tester | F-003 | verify T-003-01 | ok | 26s | $0.0790 | c63683d4-16e.. |
| 16 | Tester | F-004 | verify T-004-01 | ok | 30s | $0.0793 | 6545d621-0e0.. |