# Runs the python file in submission folder.

function errecho
{
    cat <<< "$@" 1>&2
}

mkdir -p "submission"
cd "submission"
cp "../rugby.json" .

# Find submitted python file.
# Use most recent file in python files submitted.
TEST_SUBJECT=$(ls --format=single-column --sort=time *.py | head -n 1 | tr -d '\n')

# Run test script
PYTHON_TEST_SCRIPT_LOCATION="$TESTING_DATA_FOLDER""/""test.py"
PRIVATE_OUTPUT="$TESTING_OUTPUT_FOLDER""/private.out"
STUDENT_VISIBLE_OUTPUT="$TESTING_OUTPUT_FOLDER""/visible.out"

# Run submitted script
echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Using $TEST_SUBJECT as submitted python script (""$(ls *.py | wc -l | tr -d '\n')"" total candidates)"
echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Student script output:"
ulimit -c 0
ulimit -f 10240
timeout 1h python "$TEST_SUBJECT" 2>stderr.txt
RETURNVALUE="$?"


if [[ -f "stderr.txt" ]]
then
    errecho "$(cat stderr.txt)"
fi

echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Script exit code: $RETURNVALUE"
if [[ "$RETURNVALUE" == "124" ]]
then
    echo "[$(date +'%Y/%m/%d %H:%M:%S')]" "Script ran for more than one hour."
fi
