# test_pattern_matching.py
import re

text1 = "REQ-13 A customer shall be able to save multiple shipping addresses."
text2 = "REQ-14 Each order must be delivered to exactly one address."

# Clean the text (remove REQ-13, etc.)
txt1_clean = re.sub(r"^\s*(req|fr|nfr|us|def)\s*[-:]?\s*\d+\s+", "", text1.lower())
txt2_clean = re.sub(r"^\s*(req|fr|nfr|us|def)\s*[-:]?\s*\d+\s+", "", text2.lower())

print("Cleaned texts:")
print(f"Text 1: '{txt1_clean}'")
print(f"Text 2: '{txt2_clean}'")

# Test Pattern 3
print("\n" + "="*60)
print("Testing Pattern 3: 'shall be able to verb'")
print("="*60)
pattern3 = r'(?:a|an|the)\s+([\w\s]+?)\s+shall be able to\s+(\w+)\s+.*?\b([\w\s]+?)(?:\s+(?:addresses?|products?|orders?|items?))?(?:\.|,|$)'

match = re.search(pattern3, txt1_clean)
if match:
    print(f"✅ MATCHED!")
    print(f"   Group 1 (source): '{match.group(1)}'")
    print(f"   Group 2 (verb): '{match.group(2)}'")
    print(f"   Group 3 (target): '{match.group(3)}'")
else:
    print("❌ NO MATCH")

# Test Pattern 4
print("\n" + "="*60)
print("Testing Pattern 4: 'must be verb to/with'")
print("="*60)
pattern4 = r'(?:each|every|a|an|the)\s+([\w\s]+?)\s+must be\s+(\w+)\s+(?:to|with)\s+.*?\b([\w\s]+?)(?:\.|,|$)'

match = re.search(pattern4, txt2_clean)
if match:
    print(f"✅ MATCHED!")
    print(f"   Group 1 (source): '{match.group(1)}'")
    print(f"   Group 2 (verb): '{match.group(2)}'")
    print(f"   Group 3 (target): '{match.group(3)}'")
else:
    print("❌ NO MATCH")
