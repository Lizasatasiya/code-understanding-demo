import os
import json
import http.client
import ssl


class QuestionGenerator:
    def generate(self, context: dict, summary: dict) -> list:

        api_key = self._load_api_key()
        if not api_key:
            return self._fallback()

        prompt = self._build_prompt(context, summary)
        questions = self._call_groq(api_key, prompt)
        if questions:
            return questions
        else:
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
            "Generate between 2 and 7 specific questions to test if the author understands their own change.",
            "The number of questions should depend on how complex the change is. If the change is small, 2 or 3 is enough.",
            "Keep the questions short and concise. Do not write long questions.",
            "Focus on logic, data flow, and dependency reasoning. No generic questions.",
            "",
        lines = [
            "You are a senior developer reviewing a code change.",
            "Generate between 2 and 7 specific questions to test if the author understands their own change.",
            "The number of questions should depend on how complex the change is. If the change is small, 2 or 3 is enough.",
            "Keep the questions short and concise. Do not write long questions.",
            "Focus on logic, data flow, and dependency reasoning. No generic questions.",
            "",
            "## Changed Functions",
        ]

        for f in context.get("structured_changes", []):
            summary = f.get('summary', {})
            lines.append(f"File: {f.get('file', '?')} | Function: {f.get('function', '?')}()")
            lines.append(f"Summary: {summary.get('what_changed', 'N/A')} Impact: {summary.get('impact', 'N/A')}")
            lines.append("Diff:")
            lines.append(f"```diff\n{f.get('diff', '')}\n```")
            lines.append("Dependencies invoked by this function:")
            lines.append(f"{f.get('dependency_summary', '')}")
            lines.append("")

        lines += [
            "",
            'Return ONLY a JSON array of strings (between 2 and 7). Example: ["Q1?", "Q2?", "Q3?"]',
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

            return json.loads(text)[:7]

        except Exception as e:
            return []

    def _fallback(self) -> list:
        return [
            "What behavior did your change introduce?",
            "Why is the new function called before the main logic executes?",
            "What should happen when the new check fails?"
        ]

    def validate(self, questions: list) -> list:
        return [q for q in questions if isinstance(q, str) and len(q) > 10]
