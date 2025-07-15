from extractor.scraping import extract_lottery_data

def lambda_handler(event, context):
    lottery_number = event.get("lottery_number")  # None -> scrape último
    result_path = extract_lottery_data(lottery_number)
    return {"status": "ok", "file": result_path}
