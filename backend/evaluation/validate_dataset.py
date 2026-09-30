import json
from pathlib import Path


DATASET_PATH = Path("evaluation/test_questions.json")

REQUIRED_FIELDS = {
    "question",
    "expected_answer",
    "expected_sources",
    "difficulty"
}

VALID_DIFFICULTIES = {
    "easy",
    "medium",
    "difficult",
    "unanswerable"
}


print("Loading evaluation dataset...")
print("--------------------------------")


with DATASET_PATH.open("r", encoding="utf-8") as file:
    data = json.load(file)


assert isinstance(data, list), "Dataset must be a JSON list."

print(f"Total questions: {len(data)}")

assert len(data) == 40, (
    f"Expected 40 questions, but found {len(data)}"
)


questions = []


for index, item in enumerate(data, start=1):

    print(f"Validating question {index}...")

    assert isinstance(item, dict), (
        f"Question {index} must be a JSON object."
    )

    missing_fields = REQUIRED_FIELDS - item.keys()

    assert not missing_fields, (
        f"Question {index} is missing: {missing_fields}"
    )

    assert isinstance(item["question"], str)
    assert item["question"].strip(), (
        f"Question {index} has an empty question."
    )

    assert isinstance(item["expected_answer"], str)
    assert item["expected_answer"].strip(), (
        f"Question {index} has an empty expected answer."
    )

    assert isinstance(item["expected_sources"], list), (
        f"Question {index}: expected_sources must be a list."
    )

    assert item["difficulty"] in VALID_DIFFICULTIES, (
        f"Question {index}: invalid difficulty "
        f"'{item['difficulty']}'."
    )

    if item["difficulty"] == "unanswerable":

        assert item["expected_sources"] == [], (
            f"Question {index}: unanswerable questions "
            f"must have empty expected_sources."
        )

    questions.append(
        item["question"].strip().lower()
    )


assert len(set(questions)) == len(questions), (
    "Duplicate questions found in dataset."
)


counts = {}

for difficulty in VALID_DIFFICULTIES:
    counts[difficulty] = sum(
        item["difficulty"] == difficulty
        for item in data
    )


print("\n--------------------------------")
print("Dataset Summary")
print("--------------------------------")

for difficulty, count in counts.items():
    print(f"{difficulty}: {count}")


print("\n--------------------------------")
print("DATASET VALIDATION PASSED!")
print("--------------------------------")