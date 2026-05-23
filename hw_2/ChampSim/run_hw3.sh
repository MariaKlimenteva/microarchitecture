#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Использование: $0 <путь_к_champsim> <политика_L2>"
    echo "Пример: $0 ~/university_tasks/microarchitecture-mipt/ChampSim plru"
    exit 1
fi

ORIG_DIR="$(pwd)"
CHAMPSIM_DIR="$1"
POLICY="$2"

WARMUP=1000000
SIM=5000000

cd "$CHAMPSIM_DIR" || exit 1

python3 -c "
import json
import sys

policy = sys.argv[1]
config_file = 'champsim_config.json'

try:
    with open(config_file, 'r') as f:
        data = json.load(f)

    # Ищем L2C и меняем политику (учитываем, что может быть списком или словарем)
    if 'L2C' in data:
        if isinstance(data['L2C'], list):
            for i in range(len(data['L2C'])):
                data['L2C'][i]['replacement'] = policy
        elif isinstance(data['L2C'], dict):
            data['L2C']['replacement'] = policy

    with open(config_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f'Конфиг успешно обновлен: L2C replacement -> {policy}')
except Exception as e:
    print(f'Ошибка обновления JSON: {e}')
    sys.exit(1)
" "$POLICY"

./config.sh champsim_config.json
make -j$(nproc)

if [ ! -f "bin/champsim" ]; then
    echo "Ошибка сборки ChampSim!"
    exit 1
fi

TRACES_DIR="../traces"
OUT_DIR="$ORIG_DIR/L2-${POLICY}-result"
SUMMARY_FILE="$ORIG_DIR/L2-${POLICY}-summary.csv"

mkdir -p "$OUT_DIR"

echo "Trace,IPC,L2_Accesses,L2_Misses,L2_MissRate(%)" > "$SUMMARY_FILE"

shopt -s nullglob
TRACES=("$TRACES_DIR"/*.xz)
TOTAL_TRACES=${#TRACES[@]}

if [ "$ " -eq 0 ]; then
    echo "Ошибка: Трассы не найдены!"
    exit 1
fi

echo "==================================================="
echo "Эксперимент L2 Кэш: Политика [$POLICY]"
echo "Отчет будет сохранен в: $SUMMARY_FILE"
echo "==================================================="

CURRENT=1
for TRACE in "${TRACES[@]}"; do
    BASENAME=$(basename "$TRACE" .champsimtrace.xz)
    LOG_FILE="$OUT_DIR/${BASENAME}.log"

    echo -n "[$CURRENT / $TOTAL_TRACES] $BASENAME ... "

    ./bin/champsim --warmup-instructions $WARMUP --simulation-instructions $SIM "$TRACE" > "$LOG_FILE" 2>&1

    IPC=$(grep "cumulative IPC:" "$LOG_FILE" | tail -n 1 | awk '{print $5}')

    L2_ACCESS=$(grep "L2C TOTAL" "$LOG_FILE" | tail -n 1 | awk '{print $4}')
    L2_MISS=$(grep "L2C TOTAL" "$LOG_FILE" | tail -n 1 | awk '{print $8}')

    if [ -z "$IPC" ]; then IPC="ERR"; fi
    if [ -z "$L2_ACCESS" ]; then L2_ACCESS="ERR"; fi
    if [ -z "$L2_MISS" ]; then L2_MISS="ERR"; fi

    if [ "$L2_ACCESS" != "ERR" ] && [ "$L2_MISS" != "ERR" ] && [ "$L2_ACCESS" -gt 0 ]; then
        L2_MISS_RATE=$(awk "BEGIN { printf \"%.2f\", ($L2_MISS / $L2_ACCESS) * 100 }")
    else
        L2_MISS_RATE="ERR"
    fi

    echo "$BASENAME,$IPC,$L2_ACCESS,$L2_MISS,$L2_MISS_RATE" >> "$SUMMARY_FILE"

    echo "Готово! (IPC: $IPC | L2 Miss Rate: $L2_MISS_RATE%)"

    ((CURRENT++))
done

echo "==================================================="
echo "Отчет сохранен в файл $SUMMARY_FILE"