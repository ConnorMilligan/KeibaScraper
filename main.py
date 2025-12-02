import keibascraper
import json
import os
import time

if __name__ == "__main__":
    race_ids = keibascraper.race_list(2025, 11)
    start_time = time.time()
    print(f"Found {len(race_ids)} races in total.")

    for i, race_id in enumerate(race_ids):
        if os.path.exists(f"data/races/race_{race_id}/race.json"):
            print(f"[RACE {race_id}] Data already exists. Skipping...")
            continue
        race_info, entrylist = keibascraper.load('entry', race_id)

        # write Race info and Entry list to json files
        # data/races/race_{id}/race.json
        # data/races/race_{id}/entry_{entry_id}.json
        race_dir = f"data/races/race_{race_id}"
        horse_dir = f"data/horses"

        os.makedirs(race_dir, exist_ok=True)

        progress = (i + 1) / len(race_ids) * 100
        print(f"Progress: {i+1}/{len(race_ids)} ({progress:.2f}%) races processed.")

        print(f"[RACE {race_id}] Writing race info...")
        with open(f"{race_dir}/race.json", "w", encoding="utf-8") as f:
            json.dump(race_info, f, ensure_ascii=False, indent=4)

        # pull results for race
        print(f"[RACE {race_id}] Loading results for race...")
        results = keibascraper.load('result', race_id)
        with open(f"{race_dir}/result.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

        # pull odds for race
        print(f"[RACE {race_id}] Loading odds for race...")
        odds = keibascraper.load('odds', race_id)
        with open(f"{race_dir}/odds.json", "w", encoding="utf-8") as f:
            json.dump(odds, f, ensure_ascii=False, indent=4)

        for entry in entrylist:
            # skip entry if id contains text "None"
            if "None" in entry['id']:
                continue

            # Skip entry if already exists
            if os.path.exists(f"{race_dir}/entry_{entry['id']}.json"):
                print(f"[RACE {race_id}] Entry {entry['horse_number']} data already exists. Skipping...")
                continue
            entry_id = entry['id']
            horse_number = entry['horse_number']
            print(f"[RACE {race_id}] Writing entry info for entry {horse_number}.")
            with open(f"{race_dir}/entry_{entry_id}.json", "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=4)
            
            # save horse info if not already present
            # data/horses/horse_{id}/horse.json
            # data/horses/horse_{id}/history.json
            horse_id = entry['horse_id']
            horse_path = f"{horse_dir}/horse_{horse_id}"
            os.makedirs(horse_path, exist_ok=True)
            horse_info, horse_history = keibascraper.load('horse', horse_id)

            if not os.path.exists(f"{horse_path}/horse.json"):
                print(f"[HORSE {horse_id}] Writing horse info...")
                with open(f"{horse_path}/horse.json", "w", encoding="utf-8") as f:
                    json.dump(horse_info[0], f, ensure_ascii=False, indent=4)

            if not os.path.exists(f"{horse_path}/history.json"):
                print(f"[HORSE {horse_id}] Writing horse history...")
                with open(f"{horse_path}/history.json", "w", encoding="utf-8") as f:
                    json.dump(horse_history, f, ensure_ascii=False, indent=4)


    end_time = time.time()
    elapsed = end_time - start_time

    time_taken_minutes = int(elapsed // 60)
    time_taken_seconds = elapsed % 60

    print(f"Data scraping completed in {time_taken_minutes}:{time_taken_seconds:05.2f} seconds.")