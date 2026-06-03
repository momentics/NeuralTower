import os
import json
import matplotlib.pyplot as plt

REPORT_PATH = "./neural_tower_benchmark_results/final_cognitive_report.json"
OUTPUT_IMAGE_DIR = "./neural_tower_benchmark_plots"

class NeuralTowerPlotter:
    def __init__(self, report_path: str, output_dir: str):
        self.report_path = report_path
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _load_report(self) -> dict:
        if not os.path.exists(self.report_path):
            raise FileNotFoundError(f"Файл отчета не найден: {self.report_path}. Сначала запустите evaluate_results.py")
        with open(self.report_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _parse_size(self, size_str: str) -> int:
        """Переводит строковое обозначение размера (например, '128k') в число для правильной сортировки."""
        return int(size_str.replace('k', ''))

    def generate_plots(self):
        report_data = self._load_report()
        positions = ["beginning", "middle", "end"]
        pos_labels = {"beginning": "Начало (5%)", "middle": "Середина (50%)", "end": "Конец (95%)"}
        pos_colors = {"beginning": "#2ecc71", "middle": "#e67e22", "red_end": "#e74c3c"} # Цвета для графиков
        
        # Настройка стиля отображения графиков
        plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

        for domain, sizes_data in report_data.items():
            if not sizes_data:
                continue

            # Сортируем размеры контекста по возрастанию
            sorted_sizes = sorted(sizes_data.keys(), key=self._parse_size)
            x_labels = sorted_sizes
            x_values = [self._parse_size(s) for s in sorted_sizes]

            # -------------------------------------------------------------
            # ГРАФИК 1: Когнитивная точность (Accuracy) по позициям целевого фрагмента
            # -------------------------------------------------------------
            plt.figure(figsize=(12, 6))
            
            for pos in positions:
                y_accuracy = []
                for size in sorted_sizes:
                    stats = sizes_data[size].get(pos, {})
                    # Если был OOM или сбой, точность считается равной 0
                    if stats.get("status") == "success":
                        y_accuracy.append(stats.get("accuracy", 0.0) * 100) # Переводим в проценты
                    else:
                        y_accuracy.append(0.0)

                color = pos_colors["end"] if pos == "end" else pos_colors[pos]
                plt.plot(x_values, y_accuracy, marker='o', linewidth=2.5, label=pos_labels[pos], color=color)

            plt.title(f"Когнитивная точность Qwen3.6-27B в длинном контексте\nДомен: {domain.upper()}", fontsize=14, fontweight='bold', pad=15)
            plt.xlabel("Размер контекста (в токенах)", fontsize=12, labelpad=10)
            plt.ylabel("Точность ответов (Accuracy %)", fontsize=12, labelpad=10)
            plt.xticks(x_values, x_labels, rotation=45)
            plt.ylim(-5, 105)
            plt.legend(title="Позиция целевого фрагмента", loc="lower left", frameon=True)
            plt.tight_layout()
            
            acc_plot_path = os.path.join(self.output_dir, f"accuracy_{domain}.png")
            plt.savefig(acc_plot_path, dpi=300)
            plt.close()
            print(f"[+] Построен график точности для домена {domain}: {acc_plot_path}")

            # -------------------------------------------------------------
            # ГРАФИК 2: Задержка до первого токена (TTFT)
            # -------------------------------------------------------------
            plt.figure(figsize=(12, 6))
            
            for pos in positions:
                y_ttft = []
                for size in sorted_sizes:
                    stats = sizes_data[size].get(pos, {})
                    # Фиксируем только успешные замеры времени prefill стадии
                    if stats.get("status") == "success" and stats.get("ttft_seconds") is not None:
                        y_ttft.append(stats.get("ttft_seconds"))
                    else:
                        y_ttft.append(float('nan')) # Не отображаем точки падения/OOM на временной кривой

                color = pos_colors["end"] if pos == "end" else pos_colors[pos]
                plt.plot(x_values, y_ttft, marker='s', linestyle='--', linewidth=1.5, label=f"TTFT ({pos_labels[pos]})", color=color)

            plt.title(f"Время обработки префикса (TTFT latency) на платформе NeuralTower\nДомен: {domain.upper()}", fontsize=14, fontweight='bold', pad=15)
            plt.xlabel("Размер контекста (в токенах)", fontsize=12, labelpad=10)
            plt.ylabel("Время до первого токена (в секундах)", fontsize=12, labelpad=10)
            plt.xticks(x_values, x_labels, rotation=45)
            plt.legend(loc="upper left", frameon=True)
            plt.tight_layout()

            ttft_plot_path = os.path.join(self.output_dir, f"latency_ttft_{domain}.png")
            plt.savefig(ttft_plot_path, dpi=300)
            plt.close()
            print(f"[+] Построен график задержки (TTFT) для домена {domain}: {ttft_plot_path}")

if __name__ == "__main__":
    try:
        plotter = NeuralTowerPlotter(REPORT_PATH, OUTPUT_IMAGE_DIR)
        plotter.generate_plots()
        print(f"\n[+] ВИЗУАЛИЗАЦИЯ ПОЛНОСТЬЮ ЗАВЕРШЕНА. Все графики сохранены в папку '{OUTPUT_IMAGE_DIR}'.")
    except Exception as e:
        print(f"\nОшибка при построении графиков: {e}")
