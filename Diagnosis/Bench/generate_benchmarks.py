import json
import os
import math
from typing import List, Dict, Any
from transformers import AutoTokenizer
from tasks_pool import get_programming_scenario, get_data_analysis_scenario, get_tech_doc_scenario

MODEL_NAME = "Qwen/Qwen3.6-27B"

DOMAINS = ["programming", "data_analysis", "tech_documentation"]

class NeuralTowerBenchmarkGenerator:
    def __init__(self, model_name: str):
        print(f"[~] Загрузка токенизатора для {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        print("[+] Токенизатор успешно загружен.")

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
        
        :param noise_text: Огромный массив фонового текста (тех. документация / код)
        :param target_tokens: Целевой размер контекста (например, 64000)
        :param prompt_template: Шаблон инструкции/вопроса, который крепится в самый конец
        :param target_fragment: Текст когнитивного триггера (логическая задача)
        :param position: Где разместить целевой фрагмент ('beginning', 'middle', 'end')
        """
        target_fragment_tokens = self.tokenizer.encode(target_fragment)
        prompt_tokens = self.tokenizer.encode(prompt_template)
        
        fixed_tokens_len = len(target_fragment_tokens) + len(prompt_tokens)
        if fixed_tokens_len >= target_tokens:
            raise ValueError(f"Размер целевого контекста {target_tokens} меньше, чем размер самой задачи ({fixed_tokens_len})!")

        noise_budget = target_tokens - fixed_tokens_len
        
        encoded_noise = self.tokenizer.encode(noise_text, add_special_tokens=False)
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
    
    mock_noise = "System architecture trace. V-CORE air dynamics parameters nominal. SlimSAS mapping active. " * 8000 
    
    dense_context_sizes = [
        ("2k", 2000),      ("4k", 4000),      ("8k", 8000),      ("16k", 16000),
        ("32k", 32000),    ("64k", 64000),    ("96k", 96000),    ("128k", 128000),
        ("160k", 160000),  ("192k", 192000),  ("224k", 224000),  ("256k", 256000),
        ("320k", 320000),  ("384k", 384000),  ("448k", 448000),  ("512k", 512000),
        ("640k", 640000),  ("768k", 768000),  ("896k", 896000),  ("1024k", 1024000)
    ]
    
    positions = ["beginning", "middle", "end"]
    
    scenarios = {
        "programming": get_programming_scenario(),
        "data_analysis": get_data_analysis_scenario(),
        "tech_documentation": get_tech_doc_scenario()
    }
    
    output_dir = "./neural_tower_dense_benchmarks"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[~] Запуск последовательной генерации пакетов (по возрастанию)...")
    
    for domain in DOMAINS:
        domain_dir = os.path.join(output_dir, domain)
        os.makedirs(domain_dir, exist_ok=True)
        
        print(f"\n[ДОМЕН: {domain.upper()}]")
        
        target_fragment = scenarios[domain]["target_fragment"]
        prompt_template = scenarios[domain]["prompt"]
        
        for size_label, size_tokens in dense_context_sizes:
            print(f"\n[ РАБОТА С ОБЪЕМОМ: {size_label} ({size_tokens} токенов) ]")
            for pos in positions:
                print(f" -> Генерация подзадачи: Позиция целевого фрагмента = {pos}...")
                try:
                    test_case = generator.generate_context(
                        noise_text=mock_noise,
                        target_tokens=size_tokens,
                        prompt_template=prompt_template,
                        target_fragment=target_fragment,
                        position=pos
                    )
                    
                    filename = f"{domain_dir}/test_{size_label}_{pos}.json"
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(test_case, f, ensure_ascii=False, indent=2)
                        
                except Exception as e:
                    print(f" [!] Не удалось сгенерировать конфигурацию {size_label}_{pos}: {e}")

    print(f"\n[+] ГЕНЕРАЦИЯ ЗАВЕРШЕНА. Результаты сохранены в '{output_dir}'.")