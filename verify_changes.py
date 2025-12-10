"""
Verification script for all changes made during this session.
"""
import sys
sys.path.insert(0, '.')

results = []

def test_passed(name):
    results.append(f"✅ {name}")
    print(f"✅ {name}")

def test_failed(name, error):
    results.append(f"❌ {name}: {error}")
    print(f"❌ {name}: {error}")

print("=" * 60)
print("VERIFICATION OF CHANGES")
print("=" * 60)

# Test 1: helpers.py imports
print("\n[1/6] Testing helpers.py imports...")
try:
    from src.utils.helpers import retry_with_backoff, RateLimiter
    test_passed("helpers.py - retry_with_backoff imported")
    test_passed("helpers.py - RateLimiter imported")
except Exception as e:
    test_failed("helpers.py imports", str(e))

# Test 2: RateLimiter functionality
print("\n[2/6] Testing RateLimiter...")
try:
    import time
    limiter = RateLimiter(rate=100, per=1.0)
    start = time.time()
    for _ in range(5):
        limiter.wait()
    elapsed = time.time() - start
    if elapsed < 1.0:  # Should be very fast at 100 req/sec
        test_passed(f"RateLimiter works (5 calls in {elapsed:.3f}s)")
    else:
        test_failed("RateLimiter", f"Too slow: {elapsed:.3f}s")
except Exception as e:
    test_failed("RateLimiter", str(e))

# Test 3: kubernetes_manager.py
print("\n[3/6] Testing kubernetes_manager.py...")
try:
    from src.infrastructure.kubernetes_manager import KubernetesManager
    # Check that is_k8s_available method exists
    assert hasattr(KubernetesManager, 'is_k8s_available'), "is_k8s_available method missing"
    test_passed("kubernetes_manager.py - is_k8s_available exists")
except Exception as e:
    test_failed("kubernetes_manager.py", str(e))

# Test 4: mongodb_manager.py
print("\n[4/6] Testing mongodb_manager.py...")
try:
    from src.infrastructure.mongodb_manager import MongoDBManager
    assert hasattr(MongoDBManager, 'is_k8s_available'), "is_k8s_available method missing"
    test_passed("mongodb_manager.py - is_k8s_available exists")
except Exception as e:
    test_failed("mongodb_manager.py", str(e))

# Test 5: Config Loading
print("\n[5/6] Testing config loading...")
try:
    from config.config_manager import ConfigManager
    
    environments = ['staging', 'local', 'kefar_saba']
    for env in environments:
        ConfigManager._instance = None
        ConfigManager._current_env = None
        config = ConfigManager(env)
        test_passed(f"ConfigManager({env}) loaded")
        
        # Verify is_production() for kefar_saba
        if env == 'kefar_saba':
            if config.is_production():
                test_passed(f"kefar_saba.is_production() = True")
            else:
                test_failed("kefar_saba.is_production()", "Expected True, got False")
except Exception as e:
    test_failed("Config loading", str(e))

# Test 6: Verify 'production' doesn't exist
print("\n[6/6] Verifying 'production' environment removed...")
try:
    import yaml
    with open('config/environments.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check that production is not a top-level environment
    data = yaml.safe_load(content)
    if 'environments' in data and 'production' in data['environments']:
        test_failed("Production env", "Still exists in environments.yaml")
    else:
        test_passed("Production environment correctly removed")
except Exception as e:
    test_failed("Production check", str(e))

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
passed = len([r for r in results if r.startswith("✅")])
failed = len([r for r in results if r.startswith("❌")])
print(f"Passed: {passed}")
print(f"Failed: {failed}")

if failed == 0:
    print("\n🎉 ALL TESTS PASSED!")
else:
    print("\n⚠️  SOME TESTS FAILED:")
    for r in results:
        if r.startswith("❌"):
            print(f"  {r}")
