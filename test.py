import keibascraper
import json
import os
import time

if __name__ == "__main__":
    start_time = time.time()

    horse, history = keibascraper.load('horse', '2023106816')

    with open(f"horse.json", "w", encoding="utf-8") as f:
        json.dump(horse[0], f, ensure_ascii=False, indent=4)
    with open(f"history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)

    end_time = time.time()
    elapsed = end_time - start_time

    time_taken_minutes = int(elapsed // 60)
    time_taken_seconds = elapsed % 60

    print(f"Data scraping completed in {time_taken_minutes}:{time_taken_seconds:05.2f} seconds.")