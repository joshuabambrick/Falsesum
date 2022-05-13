import argparse
import json
import os


def span_to_text(span, story):
    if isinstance(span, str):
        return span
    i, j = span
    return story[i:j]


def main(args):
    story_filename_to_path = {}
    for path, _, filenames in os.walk(args.cnndm):
        for filename in filenames:
            if filename.endswith(".story"):
                story_filename_to_path[filename] = os.path.join(path, filename)
    for filename in os.listdir(args.falsesum_data):
        if not filename.endswith(".jsonl"):
            continue
        falsesum_data_path = os.path.join(args.falsesum_data, filename)
        falsesum_summaries = []
        with open(falsesum_data_path, "r") as fin:
            for line in fin:
                falsesum_example = json.loads(line)
                story_path = story_filename_to_path[falsesum_example["context_path"]]
                with open(story_path, "r") as fin:
                    story = fin.read()

                if not story:
                    print(f"Could not find story '{falsesum_example['context_path']}'")
                summary_spans = falsesum_example["summary"]
                summary = "".join(span_to_text(span, story) for span in summary_spans)
                falsesum_summaries.append(
                    {
                        "story_path": story_path,
                        "label": falsesum_example["label"],
                        "summary": summary,
                    }
                )

        os.makedirs(args.output_data, exist_ok=True)
        summaries_filename = os.path.join(args.output_data, filename)
        with open(summaries_filename, "w") as fout:
            for falsesum_summary in falsesum_summaries:
                json.dump(falsesum_summary, fout)
                fout.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("falsesum_data", help="Path to directory holding FalseSum data")
    parser.add_argument("cnndm", help="Path to directory holding CNN/DM data")
    parser.add_argument("output_data", help="Path to target directory for generated output")
    args = parser.parse_args()
    main(args)
