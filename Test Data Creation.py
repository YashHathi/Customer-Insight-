import os
import csv
import json
import random
from datetime import datetime, timedelta

# 📍 Preserving your exact desktop paths
BASE_DIR = "C:\\Users\\yashi\\OneDrive\\Desktop\\Project_TCS"
directories = [
    os.path.join(BASE_DIR, "source_social_media2"),
    os.path.join(BASE_DIR, "source_ecommerce2"),
    os.path.join(BASE_DIR, "source_support_center2")
]

for directory in directories:
    if not os.path.exists(directory):
        os.makedirs(directory)

start_date = datetime(2026, 5, 1)
base_daily_volume = 15             

# 🧠 BLIND VARIETY ENGINE: All tones are pooled together
fragments = {
    "Staff": {
        "subjects": [
            "The shift supervisor on duty", 
            "The support team lead", 
            "The representative on the phone", 
            "The team member at the service desk", 
            "The frontline staff handling requests"
        ],
        "actions": [
            "addressed the account inquiry directly", 
            "seemed completely distracted by their phone", 
            "walked me through the setup step-by-step", 
            "apologized profusely for the confusion", 
            "provided completely contradictory information", 
            "handled the request without a single hesitation",
            "followed standard corporate verification protocols"
        ],
        "endings": [
            "which cleared up my primary concerns.", 
            "and left me feeling completely confused.", 
            "making for a completely standard interaction.", 
            "and resolved the issue right then and there.", 
            "which was quite unexpected.",
            "leaving no room for further complaints."
        ]
    },
    "Technology": {
        "subjects": [
            "The user account dashboard", 
            "The mobile app login screen", 
            "The automated chat assistant", 
            "The digital invoice generator", 
            "The secure password reset interface"
        ],
        "actions": [
            "loaded cleanly on the very first try", 
            "rejected my credentials multiple times", 
            "sent the verification code instantly", 
            "froze midway through the save process", 
            "displayed a completely generic system error", 
            "operated exactly as it routinely does"
        ],
        "endings": [
            "without causing any further delays.", 
            "which forced me to close out the window.", 
            "leading to a completely frictionless experience.", 
            "so I had to wait and try again later.", 
            "which is typical for this application framework."
        ]
    },
    "Inventory": {
        "subjects": [
            "The catalog for promotional clearance items", 
            "The stock levels displayed in the database", 
            "The pre-order availability list", 
            "The item variations dropdown menu", 
            "The physical display in the main section"
        ],
        "actions": [
            "was completely up to date", 
            "showed items that were long sold out", 
            "refreshed every few seconds dynamically", 
            "omitted critical product measurements", 
            "listed standard pricing without the discount", 
            "contained an immense variety of options"
        ],
        "endings": [
            "allowing me to make an informed choice.", 
            "which was incredibly misleading to look at.", 
            "giving a standard baseline of what was left.", 
            "making the selection process highly efficient.", 
            "leaving me completely unsure of what was ready."
        ]
    },
    "Shipping": {
        "subjects": [
            "The tracking status confirmation update", 
            "The international transit route log", 
            "The fulfillment center dispatch timetable", 
            "The local delivery courier alert system", 
            "The protective cardboard packing layout"
        ],
        "actions": [
            "indicated a minor delay in transit", 
            "arrived securely sealed and perfectly intact", 
            "showed zero physical movement for three days", 
            "shipped out ahead of the projected window", 
            "routed the parcel to the wrong sorting facility", 
            "followed the exact standard shipping path"
        ],
        "endings": [
            "and arrived safely on my doorstep.", 
            "which completely disrupted my schedule.", 
            "meaning it got here right on time.", 
            "forcing me to file a missing package claim.", 
            "keeping the entire delivery timeline predictable."
        ]
    }
}

def generate_blind_text(category):
    """Blindly combines fragments with no regard for sentiment polarity."""
    cfg = fragments[category]
    subj = random.choice(cfg["subjects"])
    action = random.choice(cfg["actions"])
    ending = random.choice(cfg["endings"])
    return f"{subj} {action} {ending}"

print("🔄 Generating high-variety data (No Sentiment Assignment)...")

social_records = []
ecomm_records = []
support_records = []

for day in range(30):
    current_date = start_date + timedelta(days=day)
    is_anomaly_day = (current_date.day == 18)
    daily_volume = base_daily_volume * 5 if is_anomaly_day else base_daily_volume
    
    for _ in range(random.randint(daily_volume - 5, daily_volume + 5)):
        timestamp = current_date + timedelta(hours=random.randint(8, 20), minutes=random.randint(0, 59))
        
        # Keep the volume anomaly for tracking spikes, but text generation stays blind
        if is_anomaly_day:
            category = "Shipping" if random.random() < 0.85 else random.choice(["Staff", "Technology", "Inventory"])
        else:
            category = random.choice(["Staff", "Technology", "Inventory", "Shipping"])
            
        text = generate_blind_text(category)
        channel = random.choice(["social", "ecomm", "support"])
        customer_id = f"{random.randint(1000, 9999)}"
        
        if channel == "social":
            social_records.append([timestamp.strftime("%Y-%m-%d %H:%M:%S"), f"@user_{random.randint(1000, 9999)}", customer_id, text])
            
        elif channel == "ecomm":
            ecomm_records.append({
                "review_date": timestamp.strftime("%d-%b-%Y"),
                "rating": random.randint(1, 5), # Completely random rating 
                "customer_id": customer_id,
                "body": text
            })
            
        elif channel == "support":
            support_records.append([timestamp.strftime("%Y-%m-%d %I:%M %p"), customer_id, text])

# Save files
with open(os.path.join(BASE_DIR, "source_social_media2", "twitter_dump2.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["timestamp", "handle", "customer_id", "tweet_text"])
    writer.writerows(social_records)

with open(os.path.join(BASE_DIR, "source_ecommerce2", "web_reviews2.json"), "w", encoding="utf-8") as f:
    json.dump(ecomm_records, f, indent=2)

with open(os.path.join(BASE_DIR, "source_support_center2", "support_logs2.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["date_string", "customer_id", "transcript"])
    writer.writerows(support_records)

print("🔥 HIGH-VARIETY UNBIASED DATA LIVE! Ready for your Hugging Face model.")