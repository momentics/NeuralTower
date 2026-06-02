import json
import os
import math
import urllib.request
from typing import List, Dict, Any
from transformers import AutoTokenizer

MODEL_NAME = "Qwen/Qwen3.6-27B"

class NeuralTowerBenchmarkGenerator:
    def __init__(self, model_name: str):
        print(f"[~] Загрузка токенизатора для {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        print("[+] Токенизатор успешно загружен.")

    def download_real_noise(self) -> str:
        """
        Скачивает подлинные тяжелые текстовые файлы (исходный код ядра Linux, системные логи)
        для создания массивного, уникального и нелинейного шумового контекста.
        """
        urls = [
            "https://githubusercontent.com",
            "https://githubusercontent.com",
            "https://githubusercontent.com"
        ]
        
        combined_noise = []
        print("[~] Загрузка реальных массивов данных для шумового контекста...")
        
        for url in urls:
            try:
                print(f" -> Скачивание: {url.split('/')[-1]}")
                with urllib.request.urlopen(url, timeout=15) as response:
                    combined_noise.append(response.read().decode('utf-8', errors='ignore'))
            except Exception as e:
                print(f" [!] Не удалось скачать {url}, используем локальный резерв. Ошибка: {e}")
        
        # Если интернета нет или ссылки недоступны, создаем тяжелый псевдо-уникальный лог
        if not combined_noise:
            print("[!] Ссылки недоступны. Генерируем массив уникальных структурированных логов...")
            base_logs = []
            for i in range(50000):
                base_logs.append(
                    f"TIMESTAMP_2026_06_03_{i:06d} [PID {1000+i}] INFO [Subsystem-VCORE] "
                    f"Telemetry metrics offset: VRAM_USED={12.4 + (i%8)*11.2:.2f}GB, "
                    f"SlimSAS_Tx_Rate={850 + (i%3)*50}MB/s, Bus_Id={hex(i)}, Thread_State_Check=OK."
                )
            return "\n".join(base_logs)
            
        return "\n".join(combined_noise)

    def generate_context(
        self, 
        noise_text: str, 
        target_tokens: int, 
        prompt_template: str, 
        target_fragment: str, 
        position: str = "middle"
    ) -> Dict[str, Any]:
        """
        Генерирует финальный контекст заданной длины в токенах.
        """
        target_fragment_tokens = self.tokenizer.encode(target_fragment)
        prompt_tokens = self.tokenizer.encode(prompt_template)
        
        fixed_tokens_len = len(target_fragment_tokens) + len(prompt_tokens)
        if fixed_tokens_len >= target_tokens:
            raise ValueError(f"Размер целевого контекста {target_tokens} меньше, чем размер самой задачи ({fixed_tokens_len})!")

        noise_budget = target_tokens - fixed_tokens_len
        
        # Токенизируем уникальный массив шума
        encoded_noise = self.tokenizer.encode(noise_text, add_special_tokens=False)
        
        # Если уникального текста всё ещё меньше, чем терабайтный предел в 1024к, 
        # только тогда мы безопасно дублируем массив, но уже огромными уникальными кусками
        if len(encoded_noise) < noise_budget:
            repeats = math.ceil(noise_budget / len(encoded_noise))
            encoded_noise = (encoded_noise * repeats)[:noise_budget]
        else:
            encoded_noise = encoded_noise[:noise_budget]

        noise_len = len(encoded_noise)
        if position == "beginning":
            insert_idx = int(noise_len * 0.05)
        elif position == "end":
            insert_idx = int(noise_len * 0.95)
        else:
            insert_idx = int(noise_len * 0.50)

        final_tokens = (
            encoded_noise[:insert_idx] + 
            target_fragment_tokens + 
            encoded_noise[insert_idx:] + 
            prompt_tokens
        )
        
        final_tokens = final_tokens[:target_tokens]
        final_text = self.tokenizer.decode(final_tokens, skip_special_tokens=False)
        
        return {
            "meta": {
                "model_used": MODEL_NAME,
                "target_context_length": target_tokens,
                "actual_context_length": len(final_tokens),
                "target_fragment_position": position,
                "target_fragment_token_index": insert_idx if position != "beginning" else int(noise_len * 0.05)
            },
            "prompt": final_text
        }

if __name__ == "__main__":
    generator = NeuralTowerBenchmarkGenerator(MODEL_NAME)
    
    # ПОЛУЧЕНИЕ НАСТОЯЩЕГО БОЛЬШОГО ОБЪЕМА ДАННЫХ
    real_heavy_noise = generator.download_real_noise()
    print(f"[+] Пул уникального фонового шума подготовлен. Символов: {len(real_heavy_noise)}")
    
    dense_context_sizes = [
        ("2k", 2000),      ("4k", 4000),      ("8k", 8000),      ("16k", 16000),
        ("32k", 32000),    ("64k", 64000),    ("96k", 96000),    ("128k", 128000),
        ("160k", 160000),  ("192k", 192000),  ("224k", 224000),  ("256k", 256000),
        ("320k", 320000),  ("384k", 384000),  ("448k", 448000),  ("512k", 512000),
        ("640k", 640000),  ("768k", 768000),  ("896k", 896000),  ("1024k", 1024000)
    ]
    
    positions = ["beginning", "middle", "end"]
    
    import tasks_pool
    
    scenarios = {
        "programming": tasks_pool.get_programming_scenario(),
        "data_analysis": tasks_pool.get_data_analysis_scenario(),
        "tech_documentation": tasks_pool.get_tech_doc_scenario()
    }
    
    base_output_dir = "./neural_tower_dense_benchmarks"
    os.makedirs(base_output_dir, exist_ok=True)
    
    print("\n[~] Запуск последовательной генерации пакетов по доменам (по возрастанию)...")
    
    for domain_name, task_data in scenarios.items():
        domain_dir = os.path.join(base_output_dir, domain_name)
        os.makedirs(domain_dir, exist_ok=True)
        print(f"\n⚡ Генерация домена: {domain_name.upper()}")
        
        for size_label, size_tokens in dense_context_sizes:
            for pos in positions:
                try:
                    test_case = generator.generate_context(
                        noise_text=real_heavy_noise,
                        target_tokens=size_tokens,
                        prompt_template=task_data["prompt"],
                        target_fragment=task_data["target_fragment"],
                        position=pos
                    )
                    
                    filename = f"{domain_dir}/test_{size_label}_{pos}.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(test_case, f, ensure_ascii=False, indent=2)
                        
                except Exception as e:
                    print(f" [!] Пропуск или ошибка в {domain_name} ({size_label}_{pos}): {e}")

    print(f"\n[+] ГЕНЕРАЦИЯ ЗАВЕРШЕНА. Результаты распределены по папкам в '{base_output_dir}'.")
