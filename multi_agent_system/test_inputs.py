import os
from src.interface.parser import ConfigParser

def run_test(name, yaml_content, expect_success=True):
    print(f"\n--- Testing: {name} ---")
    filename = "temp_test.yaml"
    with open(filename, "w") as f:
        f.write(yaml_content)
    
    try:
        config = ConfigParser.load_config(filename)
        if expect_success:
            print(f"✅ PASSED. parsed as: {config.workflow.type}")
            print(f"   Agent 1 Role: {config.agents[0].role}")
            print(f"   Agent 1 Goal: {config.agents[0].goal}")
        else:
            print("❌ FAILED. Expected error but got success.")
            
    except Exception as e:
        if not expect_success:
            print(f"✅ PASSED. Caught expected error: {e}")
        else:
            print(f"❌ FAILED. Unexpected error: {e}")
    finally:
        if os.path.exists(filename):
            os.remove(filename)

# 1. The "Spelling Mistake" Test
# 'sequntial' should become 'sequential'
yaml_spelling = """
agents:
  - id: a1
    role: tester
    goal: test
workflow:
  type: sequntial  # <--- TYPO
  steps: [a1]
"""

# 2. The "Synonym" Test
# Using 'description' instead of 'role', 'instruction' instead of 'goal'
yaml_synonyms = """
agents:
  - id: a2
    description: I am a researcher  # <--- Alias for role
    instruction: Find data          # <--- Alias for goal
    toolsets: "python"              # <--- Alias for tools
workflow:
  type: sequential
  steps: [a2]
"""

# 3. The "Weird List" Test
# 'agents' is a dict, not a list (Common user error)
yaml_single_agent = """
agents:
  id: a3  # <--- Not a list, just a single object
  role: solo
  goal: fly
workflow:
  type: sequential
  steps: [a3]
"""

# 4. The "Garbage" Test (Should fail gracefully)
yaml_garbage = """
agents: []
workflow:
  type: magic_carpet_ride  # <--- Too crazy to fix
"""

if __name__ == "__main__":
    run_test("Spelling Auto-Correct", yaml_spelling)
    run_test("Synonym Mapping", yaml_synonyms)
    run_test("Single Object vs List", yaml_single_agent)
    run_test("Garbage Input", yaml_garbage, expect_success=False)