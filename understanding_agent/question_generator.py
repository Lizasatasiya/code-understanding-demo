import os
import json
import urllib.request

class QuestionGenerator:
    def generate(self, context: dict, summary: dict) -> list:
        print("[QUESTIONS] Generating questions with LLM...")
        
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            try:
                # Try reading from the .env file one level up
                env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('GROQ_API_KEY'):
                            api_key = line.split('=', 1)[1].strip()
                            break
            except Exception:
                pass
                
        if not api_key:
            print("[QUESTIONS] Warning: GROQ_API_KEY not set. Using fallback questions.")
            return [
                "What behavior did your change introduce?",
                "Why is is_fraudulent_transaction() called during checkout?",
                "What happens if the fraud check fails?"
            ]

        prompt = f"""
You are a senior developer reviewing code. 
Based on the following code changes and context, generate 3 specific, non-generic questions to test if the author understands their own code change. 
Focus on dependencies, data flow, and logic.

Context:
{json.dumps(context, indent=2)}

Change Summary:
{json.dumps(summary, indent=2)}

Return ONLY a valid JSON array of 3 string questions. No markdown blocks, no other text.
"""
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        data = {
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.5
        }
        
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode("utf-8"), 
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                text = result["choices"][0]["message"]["content"].strip()
                
                # Clean up if the model includes markdown formatting
                if text.startswith("```json"):
                    text = text[7:-3].strip()
                elif text.startswith("```"):
                    text = text[3:-3].strip()
                    
                questions = json.loads(text)
                print(f"[QUESTIONS] Successfully generated {len(questions)} questions from LLM")
                return questions[:3]
                
        except Exception as e:
            print(f"[QUESTIONS] Error generating questions: {e}")
            print("[QUESTIONS] Falling back to default questions.")
            return [
                "What behavior did your change introduce?",
                "Why is is_fraudulent_transaction() called during checkout?",
                "What happens if the fraud check fails?"
            ]
        
    def validate(self, questions: list) -> list:
        # Simple validation
        return [q for q in questions if len(q) > 10]
