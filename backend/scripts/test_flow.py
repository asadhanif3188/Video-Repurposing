import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    print("[*] Testing Health Check...")
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            print(f"✅ Health OK: {r.json()}")
        else:
            print(f"❌ Health Failed: {r.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("Ensure the backend server is running (uvicorn app.main:app).")
        sys.exit(1)

def run_workflow():
    # 1. Create Content
    print("\n[*] 1. Creating Content Job...")
    payload = {
        "url": "https://www.youtube.com/watch?v=example",
        "tone": "professional",
        "emoji_usage": "moderate"
    }
    r = requests.post(f"{BASE_URL}/content/create", json=payload)
    if r.status_code != 202:
        print(f"❌ Failed to create content: {r.text}")
        sys.exit(1)
    
    data = r.json()
    job_id = data["id"]
    print(f"✅ Job Created: ID={job_id}, Status={data['status']}")

    # 2. Poll Status
    print("\n[*] 2. Polling Status...")
    status = "queued"
    max_retries = 30 # 30 seconds wait max (in reality AI takes time, but mock logic might be faster or slower depending on worker)
    # The worker actually calls OpenAI, so it might take 5-10s.
    
    for i in range(max_retries):
        r = requests.get(f"{BASE_URL}/content/status/{job_id}")
        if r.status_code != 200:
             print(f"   ❌ Status Check Failed: {r.status_code} - {r.text}")
             sys.exit(1)

        status_data = r.json()
        status = status_data["status"]
        print(f"   - Status: {status}")
        
        if status == "completed":
            print("✅ processing completed!")
            break
        elif status == "failed":
            print(f"❌ Processing failed! Error: {status_data.get('error', 'Unknown error')}")
            sys.exit(1)
        
        time.sleep(2)
    
    if status != "completed":
        print("❌ Timed out waiting for completion.")
        sys.exit(1)

    # 3. Schedule Content
    print("\n[*] 3. Generating Schedule...")
    r = requests.post(f"{BASE_URL}/content/schedule/{job_id}")
    if r.status_code != 200:
        print(f"❌ Failed to schedule: {r.text}")
        sys.exit(1)
    print(f"✅ Schedule Generated: {r.json()}")

    # 4. Preview Schedule
    print("\n[*] 4. Previewing Schedule...")
    r = requests.get(f"{BASE_URL}/content/schedule/preview/{job_id}")
    if r.status_code != 200:
        print(f"❌ Failed to preview: {r.text}")
        sys.exit(1)
    preview = r.json()
    print(f"✅ Received {len(preview)} scheduled items.")
    if len(preview) > 0:
        print(f"   Example: {preview[0]}")

    # 5. Run Schedule (Simulation)
    print("\n[*] 5. Running Publishing Simulation...")
    r = requests.post(f"{BASE_URL}/content/schedule/run/{job_id}")
    if r.status_code != 200:
        print(f"❌ Failed to run schedule: {r.text}")
        sys.exit(1)
    print(f"✅ Simulation Complete: {r.json()}")

    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_health()
    run_workflow()
