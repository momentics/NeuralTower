import os
import json
import time
import requests
from typing import Dict, Any, List

VLLM_API_URL = "http://localhost:8000/v1/chat/completions"
MODEL_TAG = "Qwen/Qwen3.6-27B"

DOMAINS = ["programming", "data_analysis", "tech_documentation"]

class NeuralTowerInferenceRunner:
    def __init__(self, api_url: str, model_tag: str):
        self.api_url = api_url
        self.model_tag = model_tag
        self.headers = {"Content-Type": "application/json"}

    def run_single_test(self, prompt_text: str, max_tokens: int = 512) -> Dict[str, Any]:
        """
        Отправляет запрос в vLLM с поддержкой потоковой передачи (streaming)
        для точного замера времени до первого токена (TTFT).
        """
        payload = {
            "model": self.model_tag,
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": 0.0,
            "max_tokens": max_tokens,
            "stream": True
        }

        start_prefill = time.time()
        first_token_time = None
        full_response_chunks = []
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, stream=True, timeout=600)
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "error_msg": f"vLLM вернул код ошибки: {response.status_code}",
                    "raw_response": response.text
                }

            for line in response.iter_lines():
                if not line:
                    continue
                
                if first_token_time is None:
                    first_token_time = time.time()
                
                line_str = line.decode('utf-8').strip()
                if line_str.startswith("data: "):
                    data_content = line_str[6:]
                    if data_content == "[DONE]":
                        break
                    try:
                        chunk_json = json.loads(data_content)
                        chunk_text = chunk_json['choices'][0]['delta'].get('content', '')
                        full_response_chunks.append(chunk_text)
                    except Exception:
                        continue

            end_generation = time.time()
            
            ttft = first_token_time - start_prefill if first_token_time else 0.0
            total_time = end_generation - start_prefill
            generation_time = end_generation - first_token_time if first_token_time else 0.0
            
            full_text_output = "".join(full_response_chunks)
            
            return {
                "status": "success",
                "ttft_seconds": round(ttft, 3),
                "generation_seconds": round(generation_time, 3),
                "total_seconds": round(total_time, 3),
                "output_text": full_text_output
            }

        except requests.exceptions.RequestException as e:
            return {
                "status": "oom_or_disconnect",
                "error_msg": f"Сбой связи с сервером. Возможен краш по VRAM/OOM. Ошибка: {e}",
                "output_text": ""
            }

if __name__ == "__main__":
    runner = NeuralTowerInferenceRunner(VLLM_API_URL, MODEL_TAG)
    
    base_input_dir = "./neural_tower_dense_benchmarks"
    results_output_dir = "./neural_tower_benchmark_results"
    os.makedirs(results_output_dir, exist_ok=True)
    
    dense_context_sizes = [
        "2k", "4k", "8k", "16k", 
        "32k", "64k", "96k", "128k", 
        "160k", "192k", "224k", "256k", 
        "320k", "384k", "448k", "512k",
        "640k", "768k", "896k", "1024k"
    ]
    
    positions = ["beginning", "middle", "end"]
    
    print("[~] Запуск автоматизированного цикла инференса на платформе NeuralTower...")
    print("[!] Тестирование идет строго снизу вверх по объему контекста.")
    
    oom_triggered_domains = set()

    for domain in DOMAINS:
        print(f"\nСКАНИРОВАНИЕ ДОМЕНА: {domain.upper()}")
        domain_input_dir = os.path.join(base_input_dir, domain)
        domain_output_dir = os.path.join(results_output_dir, domain)
        os.makedirs(domain_output_dir, exist_ok=True)

        for size in dense_context_sizes:
            if domain in oom_triggered_domains:
                print(f" [->] Контекст {size} пропущен: домен заблокирован из-за OOM на предыдущих шагах.")
                continue

            print(f"\n Нагрузка объема: {size}")
            
            for pos in positions:
                filename = f"test_{size}_{pos}.json"
                file_path = os.path.join(domain_input_dir, filename)
                
                if not os.path.exists(file_path):
                    print(f"  [!] Файл конфигурации не найден: {file_path}, пропускаем.")
                    continue
                
                print(f"  -> Тест позиции целевого фрагмента: [{pos}]")
                
                with open(file_path, "r", encoding="utf-8") as f:
                    test_data = json.load(f)
                
                prompt_text = test_data["prompt"]
                
                result = runner.run_single_test(prompt_text)
                
                result["meta"] = test_data["meta"]
                result["meta"]["domain"] = domain
                
                output_filename = f"result_{size}_{pos}.json"
                output_path = os.path.join(domain_output_dir, output_filename)
                
                with open(output_path, "w", encoding="utf-8") as out_f:
                    json.dump(result, out_f, ensure_ascii=False, indent=2)
                
                if result["status"] == "success":
                    print(f"   [+] Успешно. TTFT: {result['ttft_seconds']} сек. Время генерации: {result['generation_seconds']} сек.")
                else:
                    print(f"   СБОЙ на тесте {size}_{pos}: {result['error_msg']}")
                    if result["status"] == "oom_or_disconnect":
                        print(f"   Зафиксирован аппаратный предел по памяти (OOM) на объеме {size}. Прерываем данный домен.")
                        oom_triggered_domains.add(domain)
                        break

    print(f"\n[+] ТЕСТИРОВАНИЕ ИНФЕРЕНСА ЗАВЕРШЕНО. Все сырые результаты сохранены в папку '{results_output_dir}'.")