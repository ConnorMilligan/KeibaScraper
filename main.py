import keibascraper
import json

if __name__ == "__main__":
    race_ids = keibascraper.race_list(2025, 11)
    print(race_ids)

    for race_id in race_ids:
        race_info, entrylist = keibascraper.load('entry', race_id)

        # write Race info and Entry list to json files
        # data/race_{id}/race.json
        # data/race_{id}/entry_{entry_id}.json
        # race_dir = f"data/race_{race_id}"
        
        # with open(f"{race_dir}/race.json", "w", encoding="utf-8") as f:
        #     json.dump(race_info, f, ensure_ascii=False, indent=4)
        # for entry in entrylist:
        #     entry_id = entry['id']
        #     with open(f"{race_dir}/entry_{entry_id}.json", "w", encoding="utf-8") as f:
        #         json.dump(entry, f, ensure_ascii=False, indent=4)




    
    # write to a json file for inspection