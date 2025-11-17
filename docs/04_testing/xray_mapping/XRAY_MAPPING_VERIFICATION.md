# 📊 Xray Test Mapping Verification Report
**Generated:** 2025-11-09 14:02:45

## 📈 Summary

- **Xray markers in code:** 195
- **Jira bug markers in code:** 6
- **Xray tests in documentation:** 146
- **Xray tests in Jira:** 0

## 🔍 Xray Markers Analysis

- **Markers covered in docs:** 74
- **Markers NOT in docs:** 121
- **Docs tests NOT covered:** 72

### ⚠️ Xray Markers NOT in Documentation

| Xray ID | File | Line |
|---------|------|------|
| PZ-1234 | tests\conftest_xray.py | 15 |
| PZ-14026 | tests\integration\api\test_health_check.py | 54 |
| PZ-14027 | tests\integration\api\test_health_check.py | 133 |
| PZ-14028 | tests\integration\api\test_health_check.py | 204 |
| PZ-14029 | tests\integration\api\test_health_check.py | 310 |
| PZ-14030 | tests\integration\api\test_health_check.py | 372 |
| PZ-14031 | tests\integration\api\test_health_check.py | 443 |
| PZ-14032 | tests\integration\api\test_health_check.py | 506 |
| PZ-14033 | tests\integration\api\test_health_check.py | 562 |
| PZ-14060 | tests\integration\calculations\test_system_calculations.py | 32 |
| PZ-14061 | tests\integration\calculations\test_system_calculations.py | 89 |
| PZ-14062 | tests\integration\calculations\test_system_calculations.py | 138 |
| PZ-14066 | tests\integration\calculations\test_system_calculations.py | 193 |
| PZ-14067 | tests\integration\calculations\test_system_calculations.py | 242 |
| PZ-14068 | tests\integration\calculations\test_system_calculations.py | 274 |
| PZ-14069 | tests\integration\calculations\test_system_calculations.py | 315 |
| PZ-14069 | tests\integration\calculations\test_system_calculations.py | 350 |
| PZ-14070 | tests\integration\calculations\test_system_calculations.py | 391 |
| PZ-14071 | tests\integration\calculations\test_system_calculations.py | 456 |
| PZ-14072 | tests\integration\calculations\test_system_calculations.py | 496 |
| PZ-14073 | tests\integration\calculations\test_system_calculations.py | 536 |
| PZ-14078 | tests\integration\calculations\test_system_calculations.py | 574 |
| PZ-14079 | tests\integration\calculations\test_system_calculations.py | 615 |
| PZ-14080 | tests\integration\calculations\test_system_calculations.py | 658 |
| PZ-14088 | tests\load\test_job_capacity_limits.py | 810 |
| PZ-14088 | tests\load\test_job_capacity_limits.py | 825 |
| PZ-14089 | tests\integration\api\test_prelaunch_validations.py | 358 |
| PZ-14090 | tests\integration\performance\test_latency_requirements.py | 205 |
| PZ-14091 | tests\integration\performance\test_latency_requirements.py | 153 |
| PZ-14092 | tests\integration\performance\test_latency_requirements.py | 100 |
| PZ-14093 | tests\integration\api\test_view_type_validation.py | 104 |
| PZ-14094 | tests\integration\api\test_view_type_validation.py | 48 |
| PZ-14095 | tests\integration\api\test_config_validation_high_priority.py | 270 |
| PZ-14097 | tests\integration\api\test_config_validation_high_priority.py | 224 |
| PZ-14098 | tests\integration\api\test_config_validation_high_priority.py | 178 |
| PZ-14099 | tests\integration\api\test_config_validation_high_priority.py | 130 |
| PZ-14100 | tests\integration\api\test_config_validation_nfft_frequency.py | 142 |
| PZ-14715 | tests\infrastructure\resilience\test_mongodb_pod_resilience.py | 107 |
| PZ-14716 | tests\infrastructure\resilience\test_mongodb_pod_resilience.py | 252 |
| PZ-14717 | tests\infrastructure\resilience\test_mongodb_pod_resilience.py | 423 |
| PZ-14718 | tests\infrastructure\resilience\test_mongodb_pod_resilience.py | 568 |
| PZ-14719 | tests\infrastructure\resilience\test_mongodb_pod_resilience.py | 688 |
| PZ-14720 | tests\infrastructure\resilience\test_mongodb_pod_resilience.py | 803 |
| PZ-14721 | tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py | 87 |
| PZ-14722 | tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py | 229 |
| PZ-14723 | tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py | 376 |
| PZ-14724 | tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py | 504 |
| PZ-14725 | tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py | 611 |
| PZ-14726 | tests\infrastructure\resilience\test_rabbitmq_pod_resilience.py | 709 |
| PZ-14727 | tests\infrastructure\resilience\test_focus_server_pod_resilience.py | 86 |
| PZ-14728 | tests\infrastructure\resilience\test_focus_server_pod_resilience.py | 242 |
| PZ-14729 | tests\infrastructure\resilience\test_focus_server_pod_resilience.py | 415 |
| PZ-14730 | tests\infrastructure\resilience\test_focus_server_pod_resilience.py | 533 |
| PZ-14731 | tests\infrastructure\resilience\test_focus_server_pod_resilience.py | 631 |
| PZ-14732 | tests\infrastructure\resilience\test_focus_server_pod_resilience.py | 738 |
| PZ-14733 | tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py | 68 |
| PZ-14734 | tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py | 181 |
| PZ-14735 | tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py | 285 |
| PZ-14736 | tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py | 365 |
| PZ-14737 | tests\infrastructure\resilience\test_segy_recorder_pod_resilience.py | 451 |
| PZ-14738 | tests\infrastructure\resilience\test_multiple_pods_resilience.py | 162 |
| PZ-14739 | tests\infrastructure\resilience\test_multiple_pods_resilience.py | 270 |
| PZ-14740 | tests\infrastructure\resilience\test_multiple_pods_resilience.py | 390 |
| PZ-14741 | tests\infrastructure\resilience\test_multiple_pods_resilience.py | 509 |
| PZ-14742 | tests\infrastructure\resilience\test_pod_recovery_scenarios.py | 90 |
| PZ-14743 | tests\infrastructure\resilience\test_pod_recovery_scenarios.py | 264 |
| PZ-14744 | tests\infrastructure\resilience\test_pod_recovery_scenarios.py | 409 |
| PZ-14750 | tests\integration\api\test_configure_endpoint.py | 62 |
| PZ-14750 | tests\integration\api\test_config_task_endpoint.py | 62 |
| PZ-14751 | tests\integration\api\test_configure_endpoint.py | 144 |
| PZ-14751 | tests\integration\api\test_config_task_endpoint.py | 140 |
| PZ-14752 | tests\integration\api\test_configure_endpoint.py | 221 |
| PZ-14752 | tests\integration\api\test_config_task_endpoint.py | 212 |
| PZ-14753 | tests\integration\api\test_configure_endpoint.py | 295 |
| PZ-14753 | tests\integration\api\test_config_task_endpoint.py | 293 |
| PZ-14754 | tests\integration\api\test_configure_endpoint.py | 369 |
| PZ-14754 | tests\integration\api\test_config_task_endpoint.py | 368 |
| PZ-14755 | tests\integration\api\test_configure_endpoint.py | 436 |
| PZ-14755 | tests\integration\api\test_waterfall_endpoint.py | 62 |
| PZ-14756 | tests\integration\api\test_configure_endpoint.py | 522 |
| PZ-14756 | tests\integration\api\test_waterfall_endpoint.py | 152 |
| PZ-14757 | tests\integration\api\test_configure_endpoint.py | 585 |
| PZ-14757 | tests\integration\api\test_waterfall_endpoint.py | 229 |
| PZ-14758 | tests\integration\api\test_configure_endpoint.py | 652 |
| PZ-14758 | tests\integration\api\test_waterfall_endpoint.py | 287 |
| PZ-14759 | tests\integration\api\test_configure_endpoint.py | 723 |
| PZ-14759 | tests\integration\api\test_waterfall_endpoint.py | 370 |
| PZ-14760 | tests\integration\api\test_task_metadata_endpoint.py | 63 |
| PZ-14761 | tests\integration\api\test_task_metadata_endpoint.py | 155 |
| PZ-14762 | tests\integration\api\test_task_metadata_endpoint.py | 230 |
| PZ-14763 | tests\integration\api\test_task_metadata_endpoint.py | 287 |
| PZ-14764 | tests\integration\api\test_task_metadata_endpoint.py | 388 |
| PZ-14771 | tests\integration\security\test_api_authentication.py | 41 |
| PZ-14772 | tests\integration\security\test_api_authentication.py | 117 |
| PZ-14773 | tests\integration\security\test_api_authentication.py | 199 |
| PZ-14774 | tests\integration\security\test_input_validation.py | 41 |
| PZ-14775 | tests\integration\security\test_input_validation.py | 125 |
| PZ-14776 | tests\integration\security\test_csrf_protection.py | 37 |
| PZ-14777 | tests\integration\security\test_rate_limiting.py | 38 |
| PZ-14778 | tests\integration\security\test_https_enforcement.py | 36 |
| PZ-14779 | tests\integration\security\test_data_exposure.py | 39 |
| PZ-14780 | tests\integration\error_handling\test_http_error_codes.py | 41 |
| PZ-14781 | tests\integration\error_handling\test_http_error_codes.py | 142 |
| PZ-14782 | tests\integration\error_handling\test_http_error_codes.py | 227 |
| PZ-14783 | tests\integration\error_handling\test_network_errors.py | 39 |
| PZ-14784 | tests\integration\error_handling\test_network_errors.py | 132 |
| PZ-14785 | tests\integration\error_handling\test_invalid_payloads.py | 42 |
| PZ-14786 | tests\integration\error_handling\test_invalid_payloads.py | 136 |
| PZ-14787 | tests\integration\error_handling\test_invalid_payloads.py | 226 |
| PZ-14788 | tests\integration\security\test_input_validation.py | 204 |
| PZ-14790 | tests\integration\performance\test_response_time.py | 46 |
| PZ-14791 | tests\integration\performance\test_response_time.py | 111 |
| PZ-14792 | tests\integration\performance\test_response_time.py | 196 |
| PZ-14793 | tests\integration\performance\test_concurrent_performance.py | 38 |
| PZ-14794 | tests\integration\performance\test_resource_usage.py | 43 |
| PZ-14795 | tests\integration\performance\test_resource_usage.py | 109 |
| PZ-14796 | tests\integration\performance\test_resource_usage.py | 197 |
| PZ-14797 | tests\integration\performance\test_database_performance.py | 37 |
| PZ-14798 | tests\integration\performance\test_network_latency.py | 39 |
| PZ-14799 | tests\integration\performance\test_network_latency.py | 131 |
| PZ-14800 | tests\integration\load\test_concurrent_load.py | 39 |
| PZ-14801 | tests\integration\load\test_sustained_load.py | 38 |
| PZ-14802 | tests\integration\load\test_peak_load.py | 39 |
| PZ-14803 | tests\integration\load\test_load_profiles.py | 43 |
| PZ-14804 | tests\integration\load\test_load_profiles.py | 166 |
| PZ-14805 | tests\integration\load\test_load_profiles.py | 301 |
| PZ-14806 | tests\integration\load\test_recovery_and_exhaustion.py | 41 |
| PZ-14807 | tests\integration\load\test_recovery_and_exhaustion.py | 197 |
| PZ-14808 | tests\integration\data_quality\test_data_consistency.py | 39 |
| PZ-14809 | tests\integration\data_quality\test_data_consistency.py | 144 |
| PZ-14810 | tests\integration\data_quality\test_data_integrity.py | 37 |
| PZ-14811 | tests\integration\data_quality\test_data_completeness.py | 40 |
| PZ-14812 | tests\integration\data_quality\test_data_completeness.py | 116 |

### ⚠️ Documentation Tests NOT Covered (72 tests)

| Xray ID | Status |
|---------|--------|
| PZ-13291 | ❌ Missing |
| PZ-13292 | ❌ Missing |
| PZ-13293 | ❌ Missing |
| PZ-13294 | ❌ Missing |
| PZ-13295 | ❌ Missing |
| PZ-13296 | ❌ Missing |
| PZ-13297 | ❌ Missing |
| PZ-13298 | ❌ Missing |
| PZ-13299 | ❌ Missing |
| PZ-13548 | ❌ Missing |
| PZ-13552 | ❌ Missing |
| PZ-13554 | ❌ Missing |
| PZ-13555 | ❌ Missing |
| PZ-13560 | ❌ Missing |
| PZ-13561 | ❌ Missing |
| PZ-13562 | ❌ Missing |
| PZ-13564 | ❌ Missing |
| PZ-13572 | ❌ Missing |
| PZ-13599 | ❌ Missing |
| PZ-13603 | ❌ Missing |
| PZ-13604 | ❌ Missing |
| PZ-13684 | ❌ Missing |
| PZ-13685 | ❌ Missing |
| PZ-13759 | ❌ Missing |
| PZ-13760 | ❌ Missing |
| PZ-13761 | ❌ Missing |
| PZ-13762 | ❌ Missing |
| PZ-13764 | ❌ Missing |
| PZ-13765 | ❌ Missing |
| PZ-13766 | ❌ Missing |
| PZ-13767 | ❌ Missing |
| PZ-13769 | ❌ Missing |
| PZ-13801 | ❌ Missing |
| PZ-13802 | ❌ Missing |
| PZ-13803 | ❌ Missing |
| PZ-13804 | ❌ Missing |
| PZ-13805 | ❌ Missing |
| PZ-13811 | ❌ Missing |
| PZ-13812 | ❌ Missing |
| PZ-13814 | ❌ Missing |
| PZ-13815 | ❌ Missing |
| PZ-13819 | ❌ Missing |
| PZ-13821 | ❌ Missing |
| PZ-13823 | ❌ Missing |
| PZ-13832 | ❌ Missing |
| PZ-13833 | ❌ Missing |
| PZ-13835 | ❌ Missing |
| PZ-13836 | ❌ Missing |
| PZ-13837 | ❌ Missing |
| PZ-13852 | ❌ Missing |
| ... | ... and 22 more |

## 📋 All Xray Markers in Code

| Xray ID | Files | Total Locations |
|---------|-------|-----------------|
| PZ-1234 | 1 | 1 |
| PZ-13547 | 1 | 1 |
| PZ-13557 | 1 | 1 |
| PZ-13558 | 1 | 1 |
| PZ-13563 | 1 | 1 |
| PZ-13570 | 1 | 1 |
| PZ-13598 | 1 | 1 |
| PZ-13602 | 1 | 1 |
| PZ-13683 | 1 | 1 |
| PZ-13686 | 1 | 1 |
| PZ-13687 | 1 | 1 |
| PZ-13705 | 1 | 1 |
| PZ-13768 | 1 | 1 |
| PZ-13784 | 1 | 1 |
| PZ-13785 | 1 | 1 |
| PZ-13786 | 1 | 1 |
| PZ-13787 | 1 | 1 |
| PZ-13788 | 1 | 1 |
| PZ-13789 | 1 | 1 |
| PZ-13790 | 1 | 1 |
| PZ-13791 | 1 | 1 |
| PZ-13792 | 1 | 1 |
| PZ-13793 | 1 | 1 |
| PZ-13794 | 1 | 1 |
| PZ-13795 | 1 | 1 |
| PZ-13796 | 1 | 1 |
| PZ-13797 | 1 | 1 |
| PZ-13798 | 1 | 1 |
| PZ-13799 | 1 | 1 |
| PZ-13800 | 1 | 1 |
| PZ-13806 | 1 | 1 |
| PZ-13807 | 1 | 1 |
| PZ-13808 | 1 | 1 |
| PZ-13809 | 1 | 1 |
| PZ-13810 | 1 | 1 |
| PZ-13816 | 1 | 1 |
| PZ-13817 | 1 | 1 |
| PZ-13818 | 1 | 1 |
| PZ-13820 | 1 | 1 |
| PZ-13822 | 1 | 1 |
| PZ-13824 | 1 | 1 |
| PZ-13834 | 1 | 1 |
| PZ-13853 | 1 | 1 |
| PZ-13857 | 1 | 1 |
| PZ-13858 | 1 | 1 |
| PZ-13859 | 1 | 1 |
| PZ-13860 | 1 | 1 |
| PZ-13861 | 1 | 1 |
| PZ-13862 | 1 | 1 |
| PZ-13866 | 1 | 1 |
| PZ-13867 | 1 | 1 |
| PZ-13868 | 1 | 1 |
| PZ-13869 | 1 | 1 |
| PZ-13870 | 1 | 1 |
| PZ-13871 | 1 | 1 |
| PZ-13872 | 1 | 1 |
| PZ-13874 | 1 | 1 |
| PZ-13875 | 1 | 1 |
| PZ-13876 | 1 | 1 |
| PZ-13878 | 2 | 2 |
| PZ-13879 | 1 | 1 |
| PZ-13880 | 1 | 1 |
| PZ-13896 | 1 | 1 |
| PZ-13897 | 2 | 2 |
| PZ-13898 | 2 | 2 |
| PZ-13899 | 2 | 2 |
| PZ-13900 | 1 | 1 |
| PZ-13901 | 1 | 1 |
| PZ-13904 | 1 | 1 |
| PZ-13905 | 1 | 1 |
| PZ-13906 | 1 | 1 |
| PZ-13907 | 1 | 1 |
| PZ-13909 | 1 | 1 |
| PZ-14018 | 1 | 1 |
| PZ-14019 | 1 | 1 |
| PZ-14026 | 1 | 1 |
| PZ-14027 | 1 | 1 |
| PZ-14028 | 1 | 1 |
| PZ-14029 | 1 | 1 |
| PZ-14030 | 1 | 1 |
| PZ-14031 | 1 | 1 |
| PZ-14032 | 1 | 1 |
| PZ-14033 | 1 | 1 |
| PZ-14060 | 1 | 1 |
| PZ-14061 | 1 | 1 |
| PZ-14062 | 1 | 1 |
| PZ-14066 | 1 | 1 |
| PZ-14067 | 1 | 1 |
| PZ-14068 | 1 | 1 |
| PZ-14069 | 1 | 2 |
| PZ-14070 | 1 | 1 |
| PZ-14071 | 1 | 1 |
| PZ-14072 | 1 | 1 |
| PZ-14073 | 1 | 1 |
| PZ-14078 | 1 | 1 |
| PZ-14079 | 1 | 1 |
| PZ-14080 | 1 | 1 |
| PZ-14088 | 1 | 2 |
| PZ-14089 | 1 | 1 |
| PZ-14090 | 1 | 1 |
| PZ-14091 | 1 | 1 |
| PZ-14092 | 1 | 1 |
| PZ-14093 | 1 | 1 |
| PZ-14094 | 1 | 1 |
| PZ-14095 | 1 | 1 |
| PZ-14097 | 1 | 1 |
| PZ-14098 | 1 | 1 |
| PZ-14099 | 1 | 1 |
| PZ-14100 | 1 | 1 |
| PZ-14715 | 1 | 1 |
| PZ-14716 | 1 | 1 |
| PZ-14717 | 1 | 1 |
| PZ-14718 | 1 | 1 |
| PZ-14719 | 1 | 1 |
| PZ-14720 | 1 | 1 |
| PZ-14721 | 1 | 1 |
| PZ-14722 | 1 | 1 |
| PZ-14723 | 1 | 1 |
| PZ-14724 | 1 | 1 |
| PZ-14725 | 1 | 1 |
| PZ-14726 | 1 | 1 |
| PZ-14727 | 1 | 1 |
| PZ-14728 | 1 | 1 |
| PZ-14729 | 1 | 1 |
| PZ-14730 | 1 | 1 |
| PZ-14731 | 1 | 1 |
| PZ-14732 | 1 | 1 |
| PZ-14733 | 1 | 1 |
| PZ-14734 | 1 | 1 |
| PZ-14735 | 1 | 1 |
| PZ-14736 | 1 | 1 |
| PZ-14737 | 1 | 1 |
| PZ-14738 | 1 | 1 |
| PZ-14739 | 1 | 1 |
| PZ-14740 | 1 | 1 |
| PZ-14741 | 1 | 1 |
| PZ-14742 | 1 | 1 |
| PZ-14743 | 1 | 1 |
| PZ-14744 | 1 | 1 |
| PZ-14750 | 2 | 2 |
| PZ-14751 | 2 | 2 |
| PZ-14752 | 2 | 2 |
| PZ-14753 | 2 | 2 |
| PZ-14754 | 2 | 2 |
| PZ-14755 | 2 | 2 |
| PZ-14756 | 2 | 2 |
| PZ-14757 | 2 | 2 |
| PZ-14758 | 2 | 2 |
| PZ-14759 | 2 | 2 |
| PZ-14760 | 1 | 1 |
| PZ-14761 | 1 | 1 |
| PZ-14762 | 1 | 1 |
| PZ-14763 | 1 | 1 |
| PZ-14764 | 1 | 1 |
| PZ-14771 | 1 | 1 |
| PZ-14772 | 1 | 1 |
| PZ-14773 | 1 | 1 |
| PZ-14774 | 1 | 1 |
| PZ-14775 | 1 | 1 |
| PZ-14776 | 1 | 1 |
| PZ-14777 | 1 | 1 |
| PZ-14778 | 1 | 1 |
| PZ-14779 | 1 | 1 |
| PZ-14780 | 1 | 1 |
| PZ-14781 | 1 | 1 |
| PZ-14782 | 1 | 1 |
| PZ-14783 | 1 | 1 |
| PZ-14784 | 1 | 1 |
| PZ-14785 | 1 | 1 |
| PZ-14786 | 1 | 1 |
| PZ-14787 | 1 | 1 |
| PZ-14788 | 1 | 1 |
| PZ-14790 | 1 | 1 |
| PZ-14791 | 1 | 1 |
| PZ-14792 | 1 | 1 |
| PZ-14793 | 1 | 1 |
| PZ-14794 | 1 | 1 |
| PZ-14795 | 1 | 1 |
| PZ-14796 | 1 | 1 |
| PZ-14797 | 1 | 1 |
| PZ-14798 | 1 | 1 |
| PZ-14799 | 1 | 1 |
| PZ-14800 | 1 | 1 |
| PZ-14801 | 1 | 1 |
| PZ-14802 | 1 | 1 |
| PZ-14803 | 1 | 1 |
| PZ-14804 | 1 | 1 |
| PZ-14805 | 1 | 1 |
| PZ-14806 | 1 | 1 |
| PZ-14807 | 1 | 1 |
| PZ-14808 | 1 | 1 |
| PZ-14809 | 1 | 1 |
| PZ-14810 | 1 | 1 |
| PZ-14811 | 1 | 1 |
| PZ-14812 | 1 | 1 |

## 🐛 Jira Bug Markers

| Jira ID | Files | Total Locations |
|---------|-------|-----------------|
| PZ-13238 | 1 | 1 |
| PZ-13640 | 1 | 1 |
| PZ-13669 | 1 | 1 |
| PZ-13983 | 1 | 1 |
| PZ-13985 | 1 | 1 |
| PZ-13986 | 1 | 2 |

## 📊 Coverage Statistics

- **Documentation coverage:** 50.7%

## ✅ Conclusion

**⚠️ Issues found:**

- 121 Xray markers not in documentation
- 72 documentation tests without markers

