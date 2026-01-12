import os
import time
import yaml
import requests
from dotenv import load_dotenv
from typing import Optional

# Gestion optionnelle de la lib Gemini
try:
    import google.genai as genai
    HAS_GEMINI_LIB = True
except ImportError:
    HAS_GEMINI_LIB = False

load_dotenv()

class LLMEngine:
    def __init__(self, provider: str = "groq", gemini_api_key: str = None, ollama_model: str = "phi3:mini"):
        self.provider = provider.lower()
        self.ollama_model = ollama_model
        self.cache = {}
        
        # Chargement des prompts
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        prompts_path = os.path.join(project_root, "data", "prompts.yaml")
        try:
            with open(prompts_path, "r", encoding="utf-8") as f:
                self.prompts = yaml.safe_load(f)
        except:
            self.prompts = {}

        # 1. Configuration Groq (Par défaut)
        if self.provider == "groq":
            self.api_key = os.getenv("GROK_API_KEY") or os.getenv("GROQ_API_KEY")
            if not self.api_key:
                print("⚠️ Clé API Groq manquante. Vérifiez .env")
            else:
                self.api_url = "https://api.groq.com/openai/v1/chat/completions"
                self.model_name = "llama3-70b-8192" 
                print(f"✅ LLM Configuré : Groq ({self.model_name})")

        # 2. Configuration Gemini
        if self.provider == "gemini":
            if not HAS_GEMINI_LIB:
                print("⚠️ Lib 'google.genai' manquante.")
            else:
                self.api_key = gemini_api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if not self.api_key:
                    print("⚠️ Clé API Gemini manquante.")
                else:
                    try:
                        self.client = genai.Client(api_key=self.api_key)
                        self.model_name = "gemini-2.5-flash"
                        print(f"✅ LLM Configuré : Gemini ({self.model_name})")
                    except Exception as e:
                        print(f"⚠️ Erreur init Gemini: {e}")

    def generate(self, prompt: str, context: Optional[str] = None, user_context: Optional[str] = None) -> str:
        full_prompt = ""
        if user_context:
            full_prompt += f"Contexte utilisateur : {user_context}\n\n"
        if context:
            full_prompt += f"Contexte technique : {context}\n\n"
        full_prompt += prompt
        
        # Cache RAM simple
        if full_prompt in self.cache:
            return self.cache[full_prompt]

        start = time.time()
        
        try:
            if self.provider == "gemini":
                result = self._generate_gemini(full_prompt, start)
            elif self.provider == "groq":
                result = self._generate_groq(full_prompt, start)
            else:
                 raise ValueError(f"Provider non supporté ou désactivé : {self.provider}")
            
            self.cache[full_prompt] = result
            return result
            
        except Exception as e:
            print(f"❌ Erreur LLM ({self.provider}): {e}")
            raise e

    def _generate_gemini(self, prompt, start_time):
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt
        )
        print(f"⏱️ Gemini : {time.time() - start_time:.2f}s")
        return response.text.strip()

    def _generate_groq(self, prompt, start_time):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Séparation System / User pour une meilleure qualité
        messages = []
        # Si on détecte un contexte (débutant par "Contexte"), on le met en System
        if "Contexte" in prompt and "\n\n" in prompt:
            parts = prompt.split("\n\n", 1)
            system_content = parts[0]
            user_content = parts[1] if len(parts) > 1 else "..."
            messages.append({"role": "system", "content": system_content})
            messages.append({"role": "user", "content": user_content})
        else:
            messages.append({"role": "user", "content": prompt})

        # Utilisation du dernier modèle Llama 3.3 (Rapide et supporté)
        model_id = "llama-3.3-70b-versatile" 
        
        payload = {
            "model": model_id,
            "messages": messages,
            "temperature": 0.3
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        
        if not response.ok:
            error_details = response.text
            print(f"❌ Erreur Groq {response.status_code}: {error_details}")
            if response.status_code == 429:
                raise RuntimeError("Quota Groq dépassé (429)")
            raise RuntimeError(f"Groq API Error {response.status_code}: {error_details}")
            
        res_json = response.json()
        print(f"⏱️ Groq ({model_id}) : {time.time() - start_time:.2f}s")
        return res_json["choices"][0]["message"]["content"].strip()

    def _generate_ollama(self, prompt, start_time):
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.3, "num_ctx": 4096}
        }
        try:
            response = requests.post(self.api_url, json=payload, timeout=60)
            response.raise_for_status()
            res_json = response.json()
            print(f"⏱️ Ollama ({self.ollama_model}) : {time.time() - start_time:.2f}s")
            return res_json.get("response", "").strip()
        except Exception as e:
            return f"Erreur Ollama : {str(e)}. Vérifiez que 'ollama serve' tourne."
