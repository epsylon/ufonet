#!/bin/bash
TEST_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$TEST_DIR/.." && pwd)"
cd "$ROOT_DIR"
export PYTHONPATH="$ROOT_DIR${PYTHONPATH:+:$PYTHONPATH}"
mkdir -p "$TEST_DIR/results"
cat <<'BANNER'
===========================================================================

888     888 8888888888 .d88888b.  888b    888          888
888     888 888        d88P Y888b 8888b   888          888
888     888 888       888     888 88888b  888          888
888     888 8888888   888     888 888Y88b 888  .d88b.  888888
888     888 888       888     888 888 Y88b888 d8P  Y8b 888
888     888 888       888     888 888  Y88888 88888888 888
Y88b. .d88P 888       Y88b. .d88P 888   Y8888 Y8b.     Y88b.
 'Y88888P'  888        'Y88888P'  888    Y888  'Y8888   'Y8888

{(D)enial(OFF)ensive(S)ervice[ToolKit]}-{by_(io=psy+/03c8.net)}

  w3ap0n1z1ng l33t/h4ckt1v1sts/cr4ck3rs/sK1ds...
    4 pWn1ng c0rrupt$/g0vs/evilC0rps...
              8======D  $1nce: 2013 <-

===========================================================================
[Info] [AI] Launching UFONet test suite...
===========================================================================
BANNER
PASS=0; FAIL=0; SKIP=0
FAILED=()
START=$(date +%s)
for d in "$TEST_DIR"/*/; do
    name="$(basename "$d")"
    case "$name" in
        results|_lib|fixtures) continue ;;
    esac
    script=""
    if [ -f "$d/test.py" ]; then script="python3 $d/test.py"; fi
    if [ -f "$d/test.sh" ]; then script="bash $d/test.sh"; fi
    if [ -z "$script" ]; then
        SKIP=$((SKIP+1))
        echo "[SKIP] $name (no test.py / test.sh)"
        continue
    fi
    log="$TEST_DIR/results/${name}.log"
    t0=$(date +%s)
    if $script > "$log" 2>&1; then
        t=$(( $(date +%s) - t0 ))
        echo "[PASS] $name (${t}s)"
        PASS=$((PASS+1))
    else
        rc=$?
        t=$(( $(date +%s) - t0 ))
        echo "[FAIL] $name (${t}s, rc=$rc) -> $log"
        FAIL=$((FAIL+1))
        FAILED+=("$name")
    fi
done
END=$(date +%s)
TOTAL=$((END-START))
echo "======================================================="
echo "  PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP  TOTAL_TIME=${TOTAL}s"
if [ ${#FAILED[@]} -gt 0 ]; then
    echo "  FAILED: ${FAILED[*]}"
fi
echo "======================================================="
exit $FAIL
