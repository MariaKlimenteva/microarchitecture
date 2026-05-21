#!/bin/bash
# set -x # Включаем трассировку команд для отладки

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CHAMPSIM_DIR="$SCRIPT_DIR/ChampSim"
RESULTS_DIR="$SCRIPT_DIR/results"
TRACES_DIR="$SCRIPT_DIR/traces"
CONFIG_FILE_TARGET="$CHAMPSIM_DIR/champsim_config.json" 
CONFIG_FILE_ORIG="$CHAMPSIM_DIR/champsim_config.json.orig"

# --- НАЧАЛО: ГЛОБАЛЬНАЯ ОЧИСТКА ---
echo "=== PERFORMING GLOBAL CLEANUP ==="
pkill -f champsim 2>/dev/null # Останавливаем все запущенные симуляции
rm -rf "$CHAMPSIM_DIR/bin"
rm -rf "$CHAMPSIM_DIR/.csconfig"
rm -rf "$RESULTS_DIR"

# Восстанавливаем ChampSim в исходное состояние
cd "$CHAMPSIM_DIR"
git restore Makefile config/parse.py config.sh
# Fix absolute.options in Makefile to avoid trailing -isystem
sed -i 's/echo "-I\$(realpath inc) -isystem \$(realpath \$(TRIPLET_DIR)\/include)"/echo "-I$(realpath inc) $(if $(TRIPLET_DIR),-isystem $(realpath $(TRIPLET_DIR)\/include))"/' Makefile

if [ -f "$CONFIG_FILE_ORIG" ]; then
    cp "$CONFIG_FILE_ORIG" "$CONFIG_FILE_TARGET"
else
    echo "ERROR: $CONFIG_FILE_ORIG not found!"
    exit 1
fi

echo "=== CLEANUP COMPLETE ==="
# --- КОНЕЦ: ГЛОБАЛЬНАЯ ОЧИСТКА ---

mkdir -p "$RESULTS_DIR"
mkdir -p "$CHAMPSIM_DIR/bin"

PREDICTORS=("bimodal" "gag" "gap" "pap")

for pred in "${PREDICTORS[@]}"; do
    echo "=== Building $pred ==="
    
    cd "$CHAMPSIM_DIR" || exit 1
    cp "$CONFIG_FILE_ORIG" "$CONFIG_FILE_TARGET"
    
    # Устанавливаем mispredict_penalty = 12
    sed -i 's/"mispredict_penalty": [0-9]*/"mispredict_penalty": 12/' "$CONFIG_FILE_TARGET"
    
    # Обновляем branch_predictor
    sed -i "s/\"branch_predictor\": \"[^\"]*\"/\"branch_predictor\": \"$pred\"/" "$CONFIG_FILE_TARGET"
    
    rm -rf .csconfig
    PYTHONPATH=. ./config.sh champsim_config.json
    
    # Build
    make -j12
    
    # Rename binary
    mv bin/champsim "bin/champsim_$pred"
    
    echo "=== Running $pred experiments ==="
    for trace_path in "$TRACES_DIR"/*.xz; do
        trace_name=$(basename "$trace_path")
        output_file="$RESULTS_DIR/${pred}_${trace_name}.txt"
        
        if [ ! -f "$output_file" ] || [ ! -s "$output_file" ] || grep -q "0 instructions" "$output_file"; then
            echo "Running $trace_name..."
            "$CHAMPSIM_DIR/bin/champsim_$pred" --warmup-instructions 1000000 --simulation-instructions 10000000 "$trace_path" > "$output_file" 2>&1 &
            
            while [ $(jobs -r | wc -l) -ge 8 ]; do
                sleep 5
            done
        else
            echo "Skipping $trace_name (results exist and are non-empty)."
        fi
    done
    wait # Ждем завершения всех симуляций для текущего предиктора
    
    cd "$SCRIPT_DIR" || exit 1
done

echo "Done. Results in $RESULTS_DIR"
