import os
import subprocess
import time
from perfetto.trace_processor import TraceProcessor

# ====== CONFIGURATION ======
PACKAGE_NAME = "com.android.settings"  # You can replace this with any other app
TRACE_PATH_DEVICE = "/data/misc/perfetto-traces/app_trace.perfetto-trace"
TRACE_PATH_LOCAL = "app_trace.perfetto-trace"
CONFIG_FILE = "trace_config.pbtx"
DURATION = 10  # seconds of tracing
ADB_PATH = "adb"  # If adb is not in PATH, give full path like "C:\\platform-tools\\adb.exe"

# ====== 1. Force stop app ======
print("✅ Force-stopping app...")
subprocess.run([ADB_PATH, "shell", "am", "force-stop", PACKAGE_NAME], check=True)

# ====== 2. Start tracing ======
print("⏺️ Starting trace...")
start_cmd = f"{ADB_PATH} shell perfetto -c - --txt -o {TRACE_PATH_DEVICE} < {CONFIG_FILE}"
trace_proc = subprocess.Popen(start_cmd, shell=True)

time.sleep(2)

# ====== 3. Launch the app ======
print(f"🚀 Launching {PACKAGE_NAME}...")
subprocess.run([ADB_PATH, "shell", "monkey", "-p", PACKAGE_NAME, "-c", "android.intent.category.LAUNCHER", "1"], check=True)

# ====== 4. Simulate some interaction (scroll) ======
print("👆 Simulating scroll...")
time.sleep(2)
subprocess.run([ADB_PATH, "shell", "input", "swipe", "500", "1500", "500", "500"], check=True)

# ====== 5. Wait for trace to finish ======
print("⏳ Waiting for trace to finish...")
time.sleep(DURATION)
trace_proc.terminate()

# ====== 6. Pull the trace ======
print("📥 Pulling trace...")
subprocess.run([ADB_PATH, "pull", TRACE_PATH_DEVICE, TRACE_PATH_LOCAL], check=True)

# ====== 7. Analyze the trace ======
print("✅ Loading trace...")
tp = TraceProcessor(trace=TRACE_PATH_LOCAL)

# ✅ Helper function to run SQL queries
def run_query(query):
    return list(tp.query(query))

# 🔍 CPU Time Query
cpu_query = """
SELECT
  thread.name AS thread_name,
  SUM(slice.dur) / 1000000.0 AS total_ms
FROM slice
JOIN thread_track ON slice.track_id = thread_track.id
JOIN thread USING(utid)
WHERE thread.name IS NOT NULL
GROUP BY thread.name
ORDER BY total_ms DESC
LIMIT 10;
"""

rows = run_query(cpu_query)

print("\n🔥 Top CPU consumers:")
for row in rows:
    print(f"Thread: {row.thread_name}, CPU Time: {row.total_ms:.2f} ms")


# 🔍 Frame rendering times (Choreographer)
frame_query = """
SELECT ts, dur/1000000.0 AS duration_ms, slice.name
FROM slice
WHERE name LIKE 'Choreographer#doFrame'
ORDER BY ts
LIMIT 10;
"""
frame_slices = run_query(frame_query)

print("\n🎨 Frame rendering times:")
if frame_slices:
    for row in frame_slices:
        print(f"Frame: {row['name']}, Duration: {row['duration_ms']:.2f} ms")
else:
    print("No frame rendering data found.")
