import json
import os
import math
from typing import List, Dict, Any
from transformers import AutoTokenizer

MODEL_NAME = "Qwen/Qwen3.6-27B"

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
        # 1. Считаем базовые токены фиксированных частей
        target_fragment_tokens = self.tokenizer.encode(target_fragment)
        prompt_tokens = self.tokenizer.encode(prompt_template)
        
        fixed_tokens_len = len(target_fragment_tokens) + len(prompt_tokens)
        if fixed_tokens_len >= target_tokens:
            raise ValueError(f"Размер целевого контекста {target_tokens} меньше, чем размер самой задачи ({fixed_tokens_len})!")

        # 2. Вычисляем точный бюджет для шумового текста
        noise_budget = target_tokens - fixed_tokens_len
        
        # Токенизируем шум и подгоняем под бюджет
        encoded_noise = self.tokenizer.encode(noise_text, add_special_tokens=False)
        if len(encoded_noise) < noise_budget:
            repeats = math.ceil(noise_budget / len(encoded_noise))
            encoded_noise = (encoded_noise * repeats)[:noise_budget]
        else:
            encoded_noise = encoded_noise[:noise_budget]

        # 3. Определяем индекс вставки целевого фрагмента
        noise_len = len(encoded_noise)
        if position == "beginning":
            insert_idx = int(noise_len * 0.05)
        elif position == "end":
            insert_idx = int(noise_len * 0.95)
        else:
            insert_idx = int(noise_len * 0.50)

        # 4. Собираем финальный токенизированный пакет
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
    
    cognitive_target_fragment = (
        "\n[DOCKER_DIAG_NOTE] Внимание! В модуле Software/Linux/system_setup.md "
        "обнаружена жесткая привязка: драйвер NVIDIA версии 580.12 требует выделения "
        "базового адреса памяти MMIO в режиме 64-bit выше 4ГБ. Однако текущая прошивка "
        "материнской платы ASUS X99-E WS (BIOS v1203) при включении PLX-коммутаторов "
        "принудительно сбрасывает регистры BAR в 32-bit адресное пространство, если "
        "активировано более двух устройств SXM2.\n"
    )
    
    prompt_instruction = (
        "\nИзучи технические логи и документацию выше. "
        "Определи, возникнет ли аппаратный конфликт адресации памяти при интеграции драйвера "
        "NVIDIA 580.12 на материнской плате ASUS X99-E WS с четырьмя GPU? "
        "Ответ сформируй строго в виде JSON с ключами: 'conflict_detected' (true/false) и 'root_cause' (string)."
    )
    
    output_dir = "./neural_tower_dense_benchmarks"
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n[~] Запуск последовательной генерации пакетов (по возрастанию)...")
    
    for size_label, size_tokens in dense_context_sizes:
        print(f"\n[ РАБОТА С ОБЪЕМОМ: {size_label} ({size_tokens} токенов) ]")
        for pos in positions:
            print(f" -> Генерация подзадачи: Позиция целевого фрагмента = {pos}...")
            try:
                test_case = generator.generate_context(
                    noise_text=mock_noise,
                    target_tokens=size_tokens,
                    prompt_template=prompt_instruction,
                    target_fragment=cognitive_target_fragment,
                    position=pos
                )
                
                filename = f"{output_dir}/test_{size_label}_{pos}.json"
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(test_case, f, ensure_ascii=False, indent=2)
                    
            except Exception as e:
                print(f" [!] Не удалось сгенерировать конфигурацию {size_label}_{pos}: {e}")

    print(f"\n[+] ГЕНЕРАЦИЯ ЗАВЕРШЕНА. Результаты сохранены в '{output_dir}'.")
 