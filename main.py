import keibascraper
import json
import os

if __name__ == "__main__":
    os.makedirs("data/horses", exist_ok=True)
    race_ids = keibascraper.race_list(2025, 11)

    for race_id in race_ids:
        race_info, entrylist = keibascraper.load('entry', race_id)

        # write Race info and Entry list to json files
        # data/race_{id}/race.json
        # data/race_{id}/entry_{entry_id}.json
        race_dir = f"data/races/race_{race_id}"
        horse_dir = f"data/horses"

        os.makedirs(race_dir, exist_ok=True)
        
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
            entry_id = entry['id']
            horse_number = entry['horse_number']
            print(f"[RACE {race_id}] Writing entry info for entry {horse_number}...")
            with open(f"{race_dir}/entry_{entry_id}.json", "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, indent=4)
            
            # save horse info if not already present
            # SAVE HORSE AND HISTORY
            horse_id = entry['horse_id']
            horse_file = f"{horse_dir}/horse_{horse_id}.json"
            if not os.path.exists(horse_file):
                print(f"Loading horse info for horse {horse_id}")
                horse_info, horse_result = keibascraper.load('horse', horse_id)
                with open(horse_file, "w", encoding="utf-8") as f:
                    json.dump(horse_info, f, ensure_ascii=False, indent=4)




    
    # write to a json file for inspection