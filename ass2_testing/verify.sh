# For now, simple test, Just check the file is smaller than 1M
# Run with 
#   verify.sh SUBMISSION_FOLDER SUBMISSION_FILE VERIFICATION_OUTPUT_FOLDER USERNAME VERIFICATION_EXTRA_DATA_FOLDER
# 
# SUBMISSION_FOLDER - The folder which contains the submission contents
# VERIFICATION_OUTPUT_FOLDER - The folder which contains the result of verification
# USERNAME - The username of the user to be tested
# VERIFICATION_EXTRA_DATA_FOLDER - Location of any extra data which this script should know about.
SUBMISSION_FOLDER="$1"
VERIFICATION_OUTPUT_FOLDER="$2"
USERNAME="$3"
VERIFICATION_EXTRA_DATA_FOLDER="$4"

# 1M filesize limit
FILESIZE_LIMIT=$(python -c "print(1024 * 1024)" | tr -d '\n')

# Verification log data file.
VERIFICATION_LOG="$VERIFICATION_OUTPUT_FOLDER""/verify_out.txt"

FILESIZE=$(du -cbs "$SUBMISSION_FOLDER" | tail -n 1 | awk '{print $1}' | tr -d '\n')
echo "" > "$VERIFICATION_LOG"
if [[ $FILESIZE -gt $FILESIZE_LIMIT ]]
then
  echo "Filesize $FILESIZE >= $FILESIZE_LIMIT" >> "$VERIFICATION_LOG"
  echo "Failed verification" >> "$VERIFICATION_LOG"
  exit 1
else
  echo "Filesize $FILESIZE < $FILESIZE_LIMIT" >> "$VERIFICATION_LOG"
  echo "Passed filesize verification" >> "$VERIFICATION_LOG"
fi

# Set limits for testing:
ulimit -c 0
# Set filesize limit of 10MB
ulimit -f 1024
# Give a memory limit of 1GiB
ulimit -v 1048576
ulimit -m 1048576

# Second test - If submitting part 1a
if [[ $(ls -lh workshops/ass2_testing/submission/task1a.py | wc -l | tr -d '\n') == "1" ]]
then
    timeout 10m python "verify_ass2_1a.py"
    OUTCODE=$?
    if [[ "$OUTCODE" == "124" ]]
    then
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Task 1a script ran for more than ten minutes and was killed."
        exit 1
    elif [[ "$OUTCODE" == "137" ]]
    then
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "[WARNING] Task 1a script ran out of resources and was killed."
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "[WARNING] Limits are:"
        echo "\t\tTime: 10m"
        echo "\t\tFilesize: 10MiB"
        echo "\t\tMemory: 1GiB"
        echo "\t\t"
        exit 1
    fi
    if [[ "$OUTCODE" != 0 ]]
    then
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Task 1a script ran into error code $OUTCODE."
        exit 1
    fi
fi

# Third test - If submitting part 1b
if [[ $(ls -lh workshops/ass2_testing/submission/task1b.py | wc -l | tr -d '\n') == "1" ]]
then
    timeout 10m python "verify_ass2_1b.py" > "output.txt"
    OUTCODE=$?
    if [[ "$OUTCODE" == "124" ]]
    then
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Task 1b script ran for more than ten minutes and was killed."
        exit 1
    elif [[ "$OUTCODE" == "137" ]]
    then
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "[WARNING] Task 1b script ran out of resources and was killed."
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "[WARNING] Limits are:"
        echo "\t\tTime: 10m"
        echo "\t\tFilesize: 10MiB"
        echo "\t\tMemory: 1GiB"
        echo "\t\t"
        exit 1
    fi
    if [[ "$OUTCODE" != 0 ]]
    then
        echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Task 1b script ran into error code $OUTCODE."
        exit 1
    fi
    RR="$(cat "output.txt" | grep "Reduction Ratio" | awk '{print $3}')"
    if [[ $(python -c "print(float($RR) > 0.9)") == "False" ]]
    then
        echo "A reduction ratio of > 0.9 is required to add you to the leaderboard"
        rm "output.txt"
        exit 1
    fi
    rm "output.txt"
fi

# Fourth test - If submitting part 2a
# -- No actions - Not leaderboard --

# Fifth test - If submitting part 2b
# -- No actions - Not leaderboard --

exit 0