import json, re, os
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prospect_today.json")
data = json.load(open(p, encoding="utf-8"))
print("count:", len(data))
masked = 0
real = 0
for d in data:
    ph = d.get("phone", "")
    digits = re.sub(r"\D", "", ph)
    has_star = "*" in ph
    if has_star:
        masked += 1
    if len(digits) >= 11:
        real += 1
    print(f"  name={d['name'][:22]:22} digits={len(digits)} star={has_star} raw={ph!r}")
print(f"TOTAL={len(data)} real_digit_count>=11={real} contains_star={masked}")
