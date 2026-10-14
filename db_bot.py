import json
from openai import OpenAI
import os
import sqlite3
from time import time

print("Running db_bot.py!")

fdir = os.path.dirname(__file__)
def getPath(fname):
    return os.path.join(fdir, fname)

# SQLITE
sqliteDbPath = getPath("aidb.sqlite")
setupSqlPath = getPath("setup.sql")
setupSqlDataPath = getPath("setupData.sql")

# Erase previous db
if os.path.exists(sqliteDbPath):
    os.remove(sqliteDbPath)

# create new db
sqliteCon = sqlite3.connect(sqliteDbPath) 
sqliteCursor = sqliteCon.cursor()

# read in setup files
with (
        open(setupSqlPath) as setupSqlFile,
        open(setupSqlDataPath) as setupSqlDataFile
    ):

    setupSqlScript = setupSqlFile.read()
    setupSQlDataScript = setupSqlDataFile.read()

# execute setup files
sqliteCursor.executescript(setupSqlScript) # setup tables and keys
sqliteCursor.executescript(setupSQlDataScript) # setup tables and keys

def runSql(query):
    result = sqliteCursor.execute(query).fetchall()
    return result

# OPENAI
configPath = getPath("config.json")
print(configPath)
with open(configPath) as configFile:
    config = json.load(configFile)

openAiClient = OpenAI(api_key = config["openaiKey"])
openAiClient.models.list() # check if the key is valid (update in config.json)
chosen_model = "gpt-4o"

def getChatGptResponse(content):
    stream = openAiClient.chat.completions.create(
        model=chosen_model,
        messages=[{"role": "user", "content": content}],
        stream=True,
    )

    responseList = []
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            responseList.append(chunk.choices[0].delta.content)

    result = "".join(responseList)
    return result


# strategies
commonSqlOnlyRequest = " Give me a sqlite select statement that answers the question. Only respond with sqlite syntax. If there is an error do not explain it!"
strategies = {
    "zero_shot": (
        setupSqlScript + commonSqlOnlyRequest
    ),

    "single_domain_double_shot": (
        setupSqlScript
        + """
            Example question: Which vending machines have products with fewer than 5 items?
            Example SQL:
            SELECT DISTINCT machine_id
            FROM inventory
            WHERE quantity < 5;
        """
            + commonSqlOnlyRequest
        ),

        "cross_domain_double_shot": (
            """
                Example database schema:
                CREATE TABLE library_branch (
                    branch_id INTEGER PRIMARY KEY
                );
                CREATE TABLE book_stock (
                    branch_id INTEGER,
                    copies INTEGER,
                    FOREIGN KEY (branch_id) REFERENCES library_branch(branch_id)
                );

                Example question: Which library branches have no copies in stock?
                Example SQL:
                SELECT b.branch_id
                FROM library_branch AS b
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM book_stock AS s
                    WHERE s.branch_id = b.branch_id
                    AND s.copies > 0
                );
            """
        + setupSqlScript
        + commonSqlOnlyRequest
    )
}

questions = [
    "Which vending machines are out of stock?",
    "Which products are out of stock in any machine?",
    "Which products have fewer than 5 items left?",
    "What products are in vending machine 1?",
    "Which vending machines carry pepsi?",
    "Which vending machine has the most items in stock?",
    "How many of each product are in stock across all machines?",
    "Which vending machine has the greatest variety of products?"
]


# use the markdown for the sql syntax to find the SQL query
def sanitizeForJustSql(value):
    gptStartSqlMarker = "```"
    gptEndSqlMarker = "```"
    if gptStartSqlMarker in value:
        # Split at the first ``` and take everything after it
        value = value.split(gptStartSqlMarker, 1)[1]
        # Find the newline after the language identifier (sql, sqlite, etc.)
        newline_index = value.find("\n")
        if newline_index != -1:
            value = value[newline_index + 1:]
    if gptEndSqlMarker in value:
        # Split at the closing ``` and take everything before it
        value = value.split(gptEndSqlMarker, 1)[0]

    return value.strip()

for strategy in strategies:
    responses = {"strategy": strategy, "prompt_prefix": strategies[strategy]}
    questionResults = []
    print("########################################################################")
    print(f"Running strategy: {strategy}")
    for question in questions:

        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("Question:")
        print(question)
        sqlSyntaxResponse = ""
        queryRawResponse = ""
        friendlyResponse = ""
        error = "None"
        try:
            getSqlFromQuestionEngineeredPrompt = strategies[strategy] + " " + question
            sqlSyntaxResponse = getChatGptResponse(getSqlFromQuestionEngineeredPrompt)
            sqlSyntaxResponse = sanitizeForJustSql(sqlSyntaxResponse)
            print("SQL Syntax Response:")
            print(sqlSyntaxResponse)
            queryRawResponse = str(runSql(sqlSyntaxResponse))
            print("Query Raw Response:")
            print(queryRawResponse)

            friendlyResultsPrompt = f"""
            Answer the user's question using only the database results below.
            The results are in JSON format, with column names included.
            If the results are empty, say that no matching records were found.
            Do not guess or add information that is not in the results.
            Keep the answer concise and friendly.

            User's question: {question}
            SQL query: {sqlSyntaxResponse}
            Database results: {json.dumps(queryRawResponse)}
            """

            friendlyResponse = getChatGptResponse(friendlyResultsPrompt)
            print("Friendly Response:")
            print(friendlyResponse)
        except Exception as err:
            error = str(err)
            print(err)

        questionResults.append({
            "question": question,
            "sql": sqlSyntaxResponse,
            "queryRawResponse": queryRawResponse,
            "friendlyResponse": friendlyResponse,
            "error": error
        })

    responses["questionResults"] = questionResults

    with open(getPath(f"response_{strategy}_{time()}.json"), "w") as outFile:
        json.dump(responses, outFile, indent = 2)


sqliteCursor.close()
sqliteCon.close()
print("Done!")