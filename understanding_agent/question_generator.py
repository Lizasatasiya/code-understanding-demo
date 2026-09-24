import os
import json
import http.client
import ssl


class QuestionGenerator:
    def generate(self, context: dict, summary: dict) -> list:
        print("[QUESTIONS] Generating questions with LLM...")

        api_key = self._load_api_key()
        if not api_key:
            print("[QUESTIONS] Warning: GROQ_API_KEY not set. Using fallback questions.")
            return self._fallback()

        prompt = self._build_prompt(context, summary)
        questions = self._call_groq(api_key, prompt)
        if questions:
            print(f"[QUESTIONS] Successfully generated {len(questions)} questions from LLM")
            return questions
        else:
            print("[QUESTIONS] Falling back to default questions.")
            return self._fallback()

    def _load_api_key(self) -> str:
        """Load GROQ_API_KEY from env var or walk up directory tree to find .env file."""
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if api_key:
            return api_key

        # Walk up to find a .env file (up to 4 levels from this file)
        search_dir = os.path.dirname(os.path.abspath(__file__))
        for _ in range(4):
            env_path = os.path.join(search_dir, ".env")
            if os.path.exists(env_path):
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("GROQ_API_KEY"):
                            api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if api_key:
                                print(f"[QUESTIONS] Loaded GROQ_API_KEY from {env_path}")
                                return api_key
            search_dir = os.path.dirname(search_dir)

        return ""

    def _build_prompt(self, context: dict, summary: dict) -> str:
        """
        Build a focused, concise prompt using only:
        - Change summary (what, why, impact)
        - Changed functions and their new calls
        - Key dependencies (what calls what, where it's defined)
        """
        lines = [
            "You are a senior developer reviewing a code change.",
            "Generate 3 specific questions to test if the author understands their own change.",
            "Focus on logic, data flow, and dependency reasoning. No generic questions.",
            "",
            "## What Changed",
            f"- {summary.get('what_changed', 'N/A')}",
            f"- Impact: {summary.get('impact', 'N/A')}",
            f"- Why it matters: {summary.get('why_it_matters', 'N/A')}",
            "",
            "## Changed Functions",
        ]

        for f in context.get("changed_code", []):
            lines.append(f"File: {f.get('path', '?')}")
            for fn in f.get("changed_functions", []):
                calls = ", ".join(fn.get("added_calls", [])) or "none"
                lines.append(f"  - {fn['name']}()  →  new calls: [{calls}]")

        lines += [
            "",
            "## Key Dependencies",
        ]

        for dep in context.get("dependencies", []):
            lines.append(f"  - {dep.get('function', '?')} is defined in {dep.get('defined_in', '?')}")

        lines += [
            "",
            'Return ONLY a JSON array of 3 strings. Example: ["Q1?", "Q2?", "Q3?"]',
        ]
        return "\n".join(lines)

    def _call_groq(self, api_key: str, prompt: str) -> list:
        """
        Call Groq API using http.client directly.
        This avoids the macOS urllib SSL/proxy 403 Forbidden issue.
        """
        payload = json.dumps({
            "model": "qwen/qwen3.8-27b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5,
            "max_tokens": 512
        }).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Length": str(len(payload))
        }

        try:
            ctx = ssl.create_default_context()
            conn = http.client.HTTPSConnection("api.groq.com", context=ctx, timeout=30)
            conn.request("POST", "/openai/v1/chat/completions", body=payload, headers=headers)
            response = conn.getresponse()

            if response.status != 200:
                body = response.read().decode("utf-8")
                print(f"[QUESTIONS] Groq API error {response.status}: {body[:300]}")
                return []

            result = json.loads(response.read().decode("utf-8"))
            text = result["choices"][0]["message"]["content"].strip()

            # Strip markdown code fences if present
            if text.startswith("```json"):
                text = text[7:].strip()
            if text.startswith("```"):
                text = text[3:].strip()
            if text.endswith("```"):
                text = text[:-3].strip()

            return json.loads(text)[:3]

        except Exception as e:
            print(f"[QUESTIONS] Error calling Groq: {e}")
            return []

    def _fallback(self) -> list:
        return [
            "What behavior did your change introduce?",
            "Why is the new function called before the main logic executes?",
            "What should happen when the new check fails?"
        ]

    def validate(self, questions: list) -> list:
        return [q for q in questions if isinstance(q, str) and len(q) > 10]
