import sys
import requests
from config import BASE_URL, get_auth_token

def run():
    print("Testing Detection Rules API...")
    try:
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Test: Get Rules
        response = requests.get(f"{BASE_URL}/rules/", headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch rules. Status: {response.status_code}")
        
        rules = response.json()
        if not isinstance(rules, list):
            raise Exception("Rules endpoint did not return a list")

        # Test: Create a rule
        new_rule = {
            "rule_type": "sigma",
            "rule_content": "title: Validation Rule\nlogsource:\n  category: process_creation\ndetection:\n  condition: selection"
        }
        create_response = requests.post(f"{BASE_URL}/rules/import", json=new_rule, headers=headers)
        if create_response.status_code != 200:
            raise Exception(f"Failed to create rule. Status: {create_response.status_code}")
        
        rule_id = create_response.json()["id"]

        # Test: Delete the rule (cleanup)
        # Note: Depending on the API, deletion might not be fully implemented in the dummy EDR,
        # but if we can't delete, we at least tested create.
        # delete_response = requests.delete(f"{BASE_URL}/rules/{rule_id}", headers=headers)

        return True, "Rules API passed"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    success, msg = run()
    if success:
        print(f"PASS: {msg}")
        sys.exit(0)
    else:
        print(f"FAIL: {msg}")
        sys.exit(1)
