# Test Suite Code Review Checklist

Use this checklist when reviewing changes to the test suite to prevent regression
of fake/non-effective tests.

## Required Checks (Must Pass)

### 1. No `assert True` Statements
- [ ] No tests contain `assert True` without meaningful validation
- [ ] All assertions verify specific expected behavior
- [ ] If no assertion is possible, test should be marked `@pytest.mark.skip` with clear reason

### 2. No Summary Tests Without Proper Marking
- [ ] Summary tests must have `@pytest.mark.documentation_only` marker
- [ ] Summary tests must have `@pytest.mark.skip` with reason
- [ ] Summary tests must NOT have `@pytest.mark.smoke`, `@pytest.mark.regression`, or `@pytest.mark.critical`

### 3. No `logger.warning` for Bugs That Should Fail
- [ ] If server accepts invalid input, test should `pytest.fail()` not `logger.warning()`
- [ ] Pattern to avoid: `if hasattr(response, 'job_id'): logger.warning("Server accepts...")`
- [ ] Pattern to use: `if hasattr(response, 'job_id'): pytest.fail("BUG: Server accepted...")`

### 4. No `pytest.skip` as Default Behavior
- [ ] `pytest.skip()` should only be called conditionally (e.g., when data is unavailable)
- [ ] Default behavior should never be to skip a test
- [ ] If test can't run in certain environments, use `@pytest.mark.skipif(condition, reason=...)`

### 5. Proper Test Assertions
- [ ] Every test has at least one meaningful assertion
- [ ] Assertions verify expected behavior, not just "no exception was raised"
- [ ] Negative tests assert specific error types/messages

## Recommended Checks

### Test Organization
- [ ] Future API tests are marked with `@pytest.mark.future_api`
- [ ] Security tests are environment-aware (`SECURED_ENV` flag)
- [ ] Infrastructure tests that require special access are marked with `@pytest.mark.skipif(IS_CI, ...)`

### Test Quality
- [ ] Test docstrings clearly describe what is being tested
- [ ] Test names follow pattern: `test_<feature>_<scenario>`
- [ ] No hardcoded test data that should be parameterized

### Performance Tests
- [ ] Performance tests have SLA thresholds defined
- [ ] Performance tests use `pytest.fail()` when SLA is exceeded, not warnings
- [ ] Thresholds are aligned with production values

## CI Integration

Run the quality checks script before merging:

```bash
python scripts/ci_quality_checks.py
```

This script will:
1. Scan all test files for `assert True`
2. Check for warning-instead-of-fail patterns
3. Check for unconditional skips
4. Report errors and warnings

## Quick Reference

### Good Patterns

```python
# Good: Meaningful assertion
assert response.status_code == 200
assert response.job_id is not None

# Good: Negative test with specific error
with pytest.raises(APIError) as exc_info:
    api.call_with_invalid_data()
assert exc_info.value.status_code == 400

# Good: Conditional skip
if not recordings:
    pytest.skip("No recordings available for testing")

# Good: Bug detection that fails
if response.job_id:
    pytest.fail(f"BUG: Server accepted invalid input! job_id={response.job_id}")
```

### Bad Patterns

```python
# Bad: Always passes
assert True

# Bad: Warning instead of fail
if response.job_id:
    logger.warning("Server accepted invalid input")

# Bad: Unconditional skip
pytest.skip("Not implemented")

# Bad: No assertion
def test_something():
    api.call()
    # No assertion - test always passes
```

## Questions?

If you're unsure whether a test pattern is acceptable, ask yourself:
1. If this test passes, does it prove something specific about the system?
2. If the system is broken, will this test fail?
3. Is this test adding real coverage or just inflating test count?

If the answer to any of these is "no", the test needs improvement.

