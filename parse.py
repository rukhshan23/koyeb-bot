import re

def parse_feedback(text):
    pattern = re.compile(r'Paper Number:\s*(1|2|3)\s*Feedback:\s*(.+)', re.DOTALL)
    match = pattern.search(text)
    
    if match:
        return {
            "paper_number": int(match.group(1)),
            "feedback": match.group(2).strip()
        }
    else:
        return False