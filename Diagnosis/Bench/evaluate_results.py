import os
import json
from typing import Dict, Any

RESULTS_DIR = "./neural_tower_benchmark_results"

class NeuralTowerResultEvaluator:
    def __init__(self, results_dir: str):
        self.results_dir = results_dir

    def _parse_model_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Пытается извлечь и распарсить JSON из сырого ответа модели,
        даже если модель обернула его в markdown-блоки ```json ... ```
        """
        if not raw_text:
            return {}
        
        cleaned = raw_text.strip()
        # Срезаем markdown обертки, если они есть
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Попытка найти границы JSON вручную, если в тексте был лишний мусор
            start_idx = cleaned.find("{")
            end_idx = cleaned.rfind("}")
            if start_idx != -1 and end_idx != -1:
                try:
                    return json.loads(cleaned[start_idx:end_idx+1])
                except json.JSONDecodeError:
                    pass
            return {}

    def evaluate_answer(self, domain: str, parsed_json: Dict[str, Any]) -> float:
        """
        Проверяет логическую корректность ответа на основе жестких истинных 
        значений инженерных и аналитических задач, заложенных в Шаге 2.
        Возвращает 1.0 (верно) или 0.0 (неверно).
        """
        if not parsed_json:
            return 0.0

        if domain == "programming":
            # Задача требовала найти уязвимость гонки потоков / порчи памяти
            vund_found = parsed_json.get("vulnerability_found")
            err_type = str(parsed_json.get("error_type", "")).lower()
            
            # Проверяем, зафиксировала ли модель факт ошибки и правильный тип проблемы
            if vund_found is True and ("race" in err_type or "corruption" in err_type or "гонк" in err_type or "порч" in err_type):
                return 1.0

        elif domain == "data_analysis":
            # Математическая задача на перекрестное владение.
            # Формула: x = 0.42 + 0.25 * x => 0.75 * x = 0.42 => x = 0.42 / 0.75 = 0.56 (56%)
            loop_detected = parsed_json.get("loop_detected")
            try:
                # Извлекаем числовое значение процента, убирая знак '%' при наличии
                val_str = str(parsed_json.get("effective_self_ownership_percent", "")).replace("%", "").strip()
                val = float(val_str)
                # Даем погрешность на округление (идеально 56.0)
                if loop_detected is True and (55.0 <= val <= 57.0):
                    return 1.0
            except ValueError:
                pass

        elif domain == "tech_documentation":
            # СЖО: номинал 2.3 + удар 0.4 = 2.7 бар. Клапан на 2.6 бар, фитинг на 2.8 бар.
            # Исход: relief (сброс клапана произойдет раньше прорыва фитинга)
            fault_found = parsed_json.get("engineering_fault")
            behavior = str(parsed_json.get("system_behavior", "")).lower()
            
            if fault_found is True and ("relief" in behavior or "сброс" in behavior):
                return 1.0

        return 0.0

    def process_all_results(self) -> Dict[str, Any]:
        """
        Проходит по всем подкаталогам логов и собирает сводную матрицу
        когнитивной точности и производительности (TTFT).
        """
        if not os.path.exists(self.results_dir):
            print(f"Директория с результатами не найдена: {self.results_dir}")
            return {}

        domains = ["programming", "data_analysis", "tech_documentation"]
        summary_matrix = {}

        print("[~] Запуск комплексного анализа логов инференса...")

        for domain in domains:
            domain_path = os.path.join(self.results_dir, domain)
            if not os.path.exists(domain_path):
                continue
            
            print(f" -> Обработка домена: {domain.upper()}")
            summary_matrix[domain] = {}

            # Сканируем все файлы результатов в домене
            for filename in os.listdir(domain_path):
                if not filename.startswith("result_") or not filename.endswith(".json"):
                    continue
                
                file_path = os.path.join(domain_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        res_data = json.load(f)
                    except json.JSONDecodeError:
                        print(f"  [!] Битая структура файла: {filename}, пропускаем.")
                        continue

                # Извлекаем ключевые параметры из метаданных
                meta = res_data.get("meta", {})
                size_label = filename.split("_")[1] # Извлекаем например "128k"
                position = meta.get("target_fragment_position", "unknown")

                if size_label not in summary_matrix[domain]:
                    summary_matrix[domain][size_label] = {}

                # Если тест упал по OOM или ошибке сети, выставляем худшие метрики
                if res_data.get("status") != "success":
                    summary_matrix[domain][size_label][position] = {
                        "accuracy": 0.0,
                        "ttft_seconds": None,
                        "status": res_data.get("status", "failed")
                    }
                    continue

                # Если инференс успешен — парсим JSON-ответ и оцениваем когнитивную точность
                raw_output = res_data.get("output_text", "")
                parsed_json = self._parse_model_json(raw_output)
                
                accuracy = self.evaluate_answer(domain, parsed_json)

                summary_matrix[domain][size_label][position] = {
                    "accuracy": accuracy,
                    "ttft_seconds": res_data.get("ttft_seconds"),
                    "generation_seconds": res_data.get("generation_seconds"),
                    "status": "success",
                    "json_is_valid": len(parsed_json) > 0
                }

        return summary_matrix

if __name__ == "__main__":
    evaluator = NeuralTowerResultEvaluator(RESULTS_DIR)
    final_report = evaluator.process_all_results()
    
    # Сохраняем агрегированную финальную матрицу для построения графиков
    report_path = os.path.join(RESULTS_DIR, "final_cognitive_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(final_report, f, ensure_ascii=False, indent=2)
        
    print(f"\n[+] СВОДНЫЙ АНАЛИЗ ЗАВЕРШЕН.")
    print(f"[+] Финальный отчет для построения графиков сохранен в: '{report_path}'")
    
    # Выведем краткую текстовую сводку в консоль для быстрой оценки
    print("\n=== КРАТКАЯ СВОДКА ТОЧНОСТИ (Accuracy по позициям) ===")
    for domain, sizes in final_report.items():
        print(f"\nДомен {domain.upper()}:")
        # Сортируем размеры по ключу, переводя "k" в числа для корректного порядка в консоли
        sorted_sizes = sorted(sizes.keys(), key=lambda x: int(x.replace('k', '')))
        for size in sorted_sizes:
            pos_summary = []
            for pos in ["beginning", "middle", "end"]:
                stats = sizes[size].get(pos, {})
                status = stats.get("status")
                if status == "success":
                    acc = stats.get("accuracy", 0.0)
                    pos_summary.append(f"{pos}: {'✅' if acc == 1.0 else '❌'}")
                elif status == "oom_or_disconnect":
                    pos_summary.append(f"{pos}: 💥 OOM")
                else:
                    pos_summary.append(f"{pos}: 🛑 FAIL")
            print(f"  Контекст {size: <5} -> " + " | ".join(pos_summary))
