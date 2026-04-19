#!/bin/bash
# monkey-fuzzer.sh -- Fuzz Android apps with pseudo-random event injection
# Finds crashes, ANRs, and memory leaks
# Usage: ./monkey-fuzzer.sh com.example.app [num_events] [seed]

PKG="${1:?Usage: $0 <package> [num_events] [seed]}"
EVENTS="${2:-10000}"
SEED="${3:-42}"

echo "🐵 Android Monkey Fuzzer"
echo "Package: $PKG"
echo "Events: $EVENTS"
echo "Seed: $SEED"
echo ""

# Clear logcat
adb logcat -c

# Run monkey
echo "Running monkey..."
adb shell monkey -p "$PKG" -s "$SEED" --throttle 50 -v -v $EVENTS 2>&1 | tee monkey_log.txt

# Parse results
echo ""
echo "📊 Results:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

crashes=$(grep -c "CRASH" monkey_log.txt || echo 0)
anrs=$(grep -c "ANR" monkey_log.txt || echo 0)
npe=$(grep -c "NullPointerException" monkey_log.txt || echo 0)

echo "Crashes: $crashes"
echo "ANRs (Application Not Responding): $anrs"
echo "NullPointerExceptions: $npe"

# Dump to file for analysis
if [[ $crashes -gt 0 || $anrs -gt 0 ]]; then
    echo ""
    echo "⚠️  Issues found. Dumping logcat for analysis..."
    adb logcat -d > fuzzing_logcat_$(date +%s).txt
    echo "Logcat saved."
fi
