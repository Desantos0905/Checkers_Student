#!/bin/bash

# Check if number of iterations is provided
if [ $# -lt 1 ]; then
    echo "Usage: $0 <number_of_iterations>"
    exit 1
fi

iterations=$1
wins=0

# Create output directory if it doesn't exist
mkdir -p game_logs

# Run the games
for ((i=1; i<=$iterations; i++))
do
    echo "Running game $i..."
    # Run the game and save output to a file
    python3 main.py 7 7 2 l ../../Tools/Sample_AIs/Random_AI/main.py ./main.py > "game_logs/game_$i.txt"
    
    # Check the last line of output for win
    if tail -n 1 "game_logs/game_$i.txt" | grep -q "player 2 wins"; then
        ((wins++))
        echo "Game $i: Win"
    else
        echo "Game $i: Loss"
    fi
done

echo "Total wins: $wins out of $iterations games"
echo "Win rate: $(( (wins * 100) / iterations ))%"
