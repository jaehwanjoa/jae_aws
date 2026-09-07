import json

class PromptBuilder:

    @staticmethod
    def build_malware_prompt(
        incident,
        wildfire
    ):

        return f"""
You are a senior malware analyst.

Analyze the following security event.

Incident Detail

{json.dumps(
    incident,
    ensure_ascii=False,
    indent=2
)}

WildFire Analysis

{json.dumps(
    wildfire,
    ensure_ascii=False,
    indent=2
)}

Respond using exactly:

1. Executive Summary
2. Risk Assessment
3. Indicators of Compromise
4. Recommended Actions

Rules

- Use only supplied data.
- Do not speculate.
- Do not invent IOC.
- Do not assume compromise.
- Distinguish observed facts from analysis.
"""
