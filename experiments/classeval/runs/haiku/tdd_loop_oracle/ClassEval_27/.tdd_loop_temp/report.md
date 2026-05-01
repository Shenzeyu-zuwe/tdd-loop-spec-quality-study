# TDDLoop Report

| | |
|---|---|
| Result | **ALL PASSED** |
| Change | ClassEval_27 |
| Environment | python_local |
| Start | 2026-04-27 12:41:40 |
| End | 2026-04-27 12:49:57 |
| Duration | 8m16s |
| Iterations | 4 |
| Model | haiku |
| Cost | $0.7850 |
| Sessions | 28 |

## Features (4/4 passed)

### [PASSED] F-001 Method `convert(self, amount, from_currency, to_currency)` on class `CurrencyConverter` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-001-01** ORACLE TEST RUN for `CurrencyConverter.convert`.

Write the following Python code to a temp file (e.g. `_oracle_convert.py`) in the project root and execute `python _oracle_convert.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import CurrencyConverter

class CurrencyConverterTestConvert(unittest.TestCase):
    def test_convert_1(self):
        cc = CurrencyConverter()
        res = cc.convert(64, 'CNY', 'USD')
        self.assertEqual(res, 10.0)

    def test_convert_2(self):
        cc = CurrencyConverter()
        res = cc.convert(64, 'USD', 'USD')
        self.assertEqual(res, 64)

    def test_convert_3(self):
        cc = CurrencyConverter()
        res = cc.convert(64, 'CNY', 'GBP')
        self.assertAlmostEqual(res, 7.1999999999999)

    def test_convert_4(self):
        cc = CurrencyConverter()
        res = cc.convert(64, 'USD', 'GBP')
        self.assertAlmostEqual(res, 46.08)

    def test_convert_5(self):
        cc = CurrencyConverter()
        res = cc.convert(64, 'USD', 'CAD')
        self.assertAlmostEqual(res, 78.72)

    def test_convert_6(self):
        cc = CurrencyConverter()
        res = cc.convert(64, '???', 'USD')
        self.assertFalse(res)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CurrencyConverterTestConvert)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 6 oracle unit tests for CurrencyConverter.convert passed. Process exited with code 0 and unittest reported OK.

### [PASSED] F-002 Method `get_supported_currencies(self)` on class `CurrencyConverter` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-002-01** ORACLE TEST RUN for `CurrencyConverter.get_supported_currencies`.

Write the following Python code to a temp file (e.g. `_oracle_get_supported_currencies.py`) in the project root and execute `python _oracle_get_supported_currencies.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import CurrencyConverter

class CurrencyConverterTestGetSupportedCurrencies(unittest.TestCase):
    def test_get_supported_currencies_1(self):
        cc = CurrencyConverter()
        res = cc.get_supported_currencies()
        self.assertEqual(res, ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CNY'])

    def test_get_supported_currencies_2(self):
        cc = CurrencyConverter()
        res = cc.get_supported_currencies()
        self.assertEqual(res, ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CNY'])

    def test_get_supported_currencies_3(self):
        cc = CurrencyConverter()
        res = cc.get_supported_currencies()
        self.assertEqual(res, ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CNY'])

    def test_get_supported_currencies_4(self):
        cc = CurrencyConverter()
        res = cc.get_supported_currencies()
        self.assertEqual(res, ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CNY'])

    def test_get_supported_currencies_5(self):
        cc = CurrencyConverter()
        res = cc.get_supported_currencies()
        self.assertEqual(res, ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CNY'])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CurrencyConverterTestGetSupportedCurrencies)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 5 oracle tests passed successfully. The get_supported_currencies() method returns the exact expected list ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CNY'] in the correct order.

### [PASSED] F-003 Method `add_currency_rate(self, currency, rate)` on class `CurrencyConverter` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-003-01** ORACLE TEST RUN for `CurrencyConverter.add_currency_rate`.

Write the following Python code to a temp file (e.g. `_oracle_add_currency_rate.py`) in the project root and execute `python _oracle_add_currency_rate.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import CurrencyConverter

class CurrencyConverterTestAddCurrencyRate(unittest.TestCase):
    def test_add_currency_rate_1(self):
        cc = CurrencyConverter()
        cc.add_currency_rate('KRW', 1308.84)
        self.assertEqual(cc.rates['KRW'], 1308.84)

    def test_add_currency_rate_2(self):
        cc = CurrencyConverter()
        cc.add_currency_rate('aaa', 1.0)
        self.assertEqual(cc.rates['aaa'], 1.0)

    def test_add_currency_rate_3(self):
        cc = CurrencyConverter()
        cc.add_currency_rate('bbb', 2.0)
        self.assertEqual(cc.rates['bbb'], 2.0)

    def test_add_currency_rate_4(self):
        cc = CurrencyConverter()
        cc.add_currency_rate('ccc', 3.0)
        self.assertEqual(cc.rates['ccc'], 3.0)

    def test_add_currency_rate_5(self):
        cc = CurrencyConverter()
        cc.add_currency_rate('ddd', 4.0)
        self.assertEqual(cc.rates['ddd'], 4.0)

    def test_add_currency_rate_6(self):
        cc = CurrencyConverter()
        res = cc.add_currency_rate('USD', 1.0)
        self.assertFalse(res)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CurrencyConverterTestAddCurrencyRate)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 6 oracle tests passed. The add_currency_rate method correctly adds new currencies to the rates dictionary and returns False when attempting to add an already-existing currency.

### [PASSED] F-004 Method `update_currency_rate(self, currency, new_rate)` on class `CurrencyConverter` passes its hidden unit-test suite (oracle ablation arm).

- [✓] **T-004-01** ORACLE TEST RUN for `CurrencyConverter.update_currency_rate`.

Write the following Python code to a temp file (e.g. `_oracle_update_currency_rate.py`) in the project root and execute `python _oracle_update_currency_rate.py` via the Bash tool. The script runs the hidden unit tests for this method.

PASS criteria: process exits with code 0 AND unittest reports `OK` (no failures, no errors).
FAIL criteria: any failure, error, exception, or non-zero exit. Do NOT modify the test code. Do NOT infer the result without actually executing the script.

Script:
```python
import sys, unittest
sys.path.insert(0, '.')

from solution import CurrencyConverter

class CurrencyConverterTestUpdateCurrencyRate(unittest.TestCase):
    def test_update_currency_rate_1(self):
        cc = CurrencyConverter()
        cc.update_currency_rate('CNY', 7.18)
        self.assertEqual(cc.rates['CNY'], 7.18)

    def test_update_currency_rate_2(self):
        cc = CurrencyConverter()
        cc.update_currency_rate('CNY', 1.0)
        self.assertEqual(cc.rates['CNY'], 1.0)

    def test_update_currency_rate_3(self):
        cc = CurrencyConverter()
        cc.update_currency_rate('CNY', 2.0)
        self.assertEqual(cc.rates['CNY'], 2.0)

    def test_update_currency_rate_4(self):
        cc = CurrencyConverter()
        cc.update_currency_rate('CNY', 3.0)
        self.assertEqual(cc.rates['CNY'], 3.0)

    def test_update_currency_rate_5(self):
        cc = CurrencyConverter()
        cc.update_currency_rate('CNY', 4.0)
        self.assertEqual(cc.rates['CNY'], 4.0)

    def test_update_currency_rate_6(self):
        cc = CurrencyConverter()
        res = cc.update_currency_rate('???', 7.18)
        self.assertFalse(res)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(CurrencyConverterTestUpdateCurrencyRate)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
```

  - All 6 oracle unit tests for update_currency_rate passed successfully. The implementation correctly updates rates for existing currencies and returns False for non-existent currencies.

## Sessions (28 total, $0.7850)

| # | Role | Feature | Task | Status | Duration | Cost | Session ID |
|---|------|---------|------|--------|----------|------|------------|
| 1 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | 9841b4cb-bab.. |
| 2 | Worker | F-001 | fix 1 tests | error | 1s | $0.0000 | f1db9b5c-d08.. |
| 3 | Tester | F-001 | verify T-001-01 | error | 1s | $0.0000 | 1f6146d8-cde.. |
| 4 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | 5fe54d66-216.. |
| 5 | Worker | F-002 | fix 1 tests | error | 1s | $0.0000 | 5ae094af-8e2.. |
| 6 | Tester | F-002 | verify T-002-01 | error | 1s | $0.0000 | 72c76a8f-cfc.. |
| 7 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | e1cfb8da-591.. |
| 8 | Worker | F-003 | fix 1 tests | error | 1s | $0.0000 | f3d95bf7-e11.. |
| 9 | Tester | F-003 | verify T-003-01 | error | 1s | $0.0000 | 80caf038-40e.. |
| 10 | Tester | F-004 | verify T-004-01 | error | 1s | $0.0000 | d2186032-da9.. |
| 11 | Worker | F-004 | fix 1 tests | error | 1s | $0.0000 | 4fdcc71f-069.. |
| 12 | Tester | F-004 | verify T-004-01 | error | 1s | $0.0000 | 8090083c-ccd.. |
| 13 | Tester | F-001 | verify T-001-01 | ok | 30s | $0.0584 | a6815a3b-82f.. |
| 14 | Worker | F-001 | fix 1 tests | ok | 31s | $0.0490 | 510d2f1d-90e.. |
| 15 | Tester | F-001 | verify T-001-01 | ok | 23s | $0.0418 | 13491a9a-675.. |
| 16 | Tester | F-002 | verify T-002-01 | ok | 21s | $0.0449 | 00d5ae84-e15.. |
| 17 | Worker | F-002 | fix 1 tests | ok | 22s | $0.0435 | c652a554-f4d.. |
| 18 | Tester | F-002 | verify T-002-01 | ok | 30s | $0.0512 | 073de6eb-871.. |
| 19 | Tester | F-003 | verify T-003-01 | ok | 30s | $0.0471 | b61ffd40-657.. |
| 20 | Worker | F-003 | fix 1 tests | ok | 31s | $0.0573 | a413f2c0-05a.. |
| 21 | Tester | F-003 | verify T-003-01 | ok | 37s | $0.0513 | 7cdf0144-9f4.. |
| 22 | Tester | F-004 | verify T-004-01 | ok | 24s | $0.0457 | 0fd46123-c80.. |
| 23 | Worker | F-004 | fix 1 tests | ok | 47s | $0.0730 | 891f0017-f5b.. |
| 24 | Tester | F-004 | verify T-004-01 | ok | 33s | $0.0500 | e1cdd97a-b9a.. |
| 25 | Tester | F-001 | verify T-001-01 | ok | 23s | $0.0419 | 9689979c-db5.. |
| 26 | Tester | F-002 | verify T-002-01 | ok | 21s | $0.0439 | ff0d43cb-695.. |
| 27 | Tester | F-003 | verify T-003-01 | ok | 20s | $0.0422 | debb3bda-037.. |
| 28 | Tester | F-004 | verify T-004-01 | ok | 22s | $0.0438 | 2551093e-2e4.. |