import os
import sys
import time
import json
import importlib.util
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# List of modules to run in order
TEST_MODULES = [
    "test_auth",
    "test_health",
    "test_database",
    "test_endpoints",
    "test_telemetry",
    "test_osquery",
    "test_rules",
    "test_detection_engine",
    "test_sigma",
    "test_ai",
    "test_audit",
    "test_scheduler",
    "test_websockets",
    "test_api_latency",
    "benchmark"
]

def generate_html_report(results, overall_score, duration):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SentinelX Validation Report</title>
    <style>
        body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 40px; }}
        h1 {{ text-align: center; color: #38bdf8; font-size: 2.5rem; margin-bottom: 40px; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: #1e293b; border-radius: 12px; padding: 30px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); border: 1px solid #334155; }}
        .metric-row {{ display: flex; justify-content: space-between; padding: 15px 0; border-bottom: 1px solid #334155; }}
        .metric-row:last-child {{ border-bottom: none; }}
        .metric-name {{ font-weight: 500; font-size: 1.1rem; color: #cbd5e1; }}
        .status-pass {{ color: #22c55e; font-weight: bold; background: rgba(34, 197, 94, 0.1); padding: 4px 12px; border-radius: 9999px; font-size: 0.9rem; }}
        .status-fail {{ color: #ef4444; font-weight: bold; background: rgba(239, 68, 68, 0.1); padding: 4px 12px; border-radius: 9999px; font-size: 0.9rem; }}
        .summary {{ margin-top: 40px; text-align: center; padding-top: 30px; border-top: 2px dashed #334155; }}
        .score {{ font-size: 4rem; font-weight: bold; color: { '#22c55e' if overall_score == 100 else '#f59e0b' if overall_score > 80 else '#ef4444' }; margin: 10px 0; }}
        .duration {{ color: #94a3b8; font-size: 0.9rem; margin-top: 10px; }}
    </style>
</head>
<body>
    <h1>SentinelX Validation Report</h1>
    <div class="container">
"""
    
    for name, success, msg in results:
        display_name = name.replace("test_", "").replace("_", " ").title()
        status_class = "status-pass" if success else "status-fail"
        status_text = "PASS" if success else "FAIL"
        
        html_content += f"""
        <div class="metric-row">
            <span class="metric-name">{display_name}</span>
            <span class="{status_class}" title="{msg}">{status_text}</span>
        </div>
"""

    html_content += f"""
        <div class="summary">
            <h2 style="color: #cbd5e1; margin-bottom: 0;">Overall Score</h2>
            <div class="score">{overall_score:.0f}%</div>
            <div class="duration">Test Duration: {duration:.2f} seconds</div>
        </div>
    </div>
</body>
</html>
"""
    
    with open("reports/latest_report.html", "w") as f:
        f.write(html_content)


def generate_json_report(results, overall_score, duration):
    report_data = {
        "timestamp": time.time(),
        "overall_score": overall_score,
        "duration_seconds": duration,
        "results": []
    }
    
    for name, success, msg in results:
        report_data["results"].append({
            "module": name,
            "success": success,
            "message": msg
        })
        
    with open("reports/latest_report.json", "w") as f:
        json.dump(report_data, f, indent=4)


def run_all():
    print(f"{Fore.CYAN}{Style.BRIGHT}==========================================")
    print(f"{Fore.CYAN}{Style.BRIGHT}      SentinelX Validation Suite")
    print(f"{Fore.CYAN}{Style.BRIGHT}==========================================\n")
    
    start_time = time.time()
    results = []
    passed_count = 0
    
    current_dir = os.path.dirname(os.path.abspath(__file__))

    for module_name in TEST_MODULES:
        print(f"{Fore.WHITE}Testing {module_name.replace('test_', '').replace('_', ' ').title()}...")
        
        module_path = os.path.join(current_dir, f"{module_name}.py")
        if not os.path.exists(module_path):
            print(f"{Fore.RED}FAIL - Module not found\n")
            results.append((module_name, False, "Module not found"))
            continue
            
        try:
            # Dynamically load the module
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Execute the 'run' function
            if hasattr(module, 'run'):
                success, msg = module.run()
                if success:
                    print(f"{Fore.GREEN}{Style.BRIGHT}PASS{Style.RESET_ALL} - {msg}\n")
                    passed_count += 1
                else:
                    print(f"{Fore.RED}{Style.BRIGHT}FAIL{Style.RESET_ALL} - {msg}\n")
                results.append((module_name, success, msg))
            else:
                print(f"{Fore.RED}FAIL{Style.RESET_ALL} - No run() function found\n")
                results.append((module_name, False, "No run() function found"))
        except Exception as e:
            print(f"{Fore.RED}FAIL{Style.RESET_ALL} - Exception: {str(e)}\n")
            results.append((module_name, False, str(e)))

    end_time = time.time()
    duration = end_time - start_time
    total_tests = len(TEST_MODULES)
    overall_score = (passed_count / total_tests) * 100 if total_tests > 0 else 0

    print(f"{Fore.CYAN}{Style.BRIGHT}==========================================")
    print(f"{Fore.WHITE}{Style.BRIGHT}Overall: {passed_count} / {total_tests} Passed")
    print(f"{Fore.WHITE}Duration : {duration:.2f} seconds")
    print(f"{Fore.GREEN}{Style.BRIGHT}System Ready{Style.RESET_ALL}\n")

    generate_html_report(results, overall_score, duration)
    generate_json_report(results, overall_score, duration)
    
    print(f"Reports generated in 'reports/' directory.")

if __name__ == "__main__":
    # Ensure reports directory exists
    os.makedirs("reports", exist_ok=True)
    run_all()
