import re
import csv


def extract_info_and_sentences(text):
    pattern = r'Part (\d+(\.\d+)?)\s*(?:\(([^)]+)\))?\s*((?:[\s\S](?!Part))+)'
    matches = re.findall(pattern, text)
    data = []
    for part_num, _, timestamp_val, content in matches:
        sentences = extract_sentences(content)
        data.append((part_num, timestamp_val, sentences))
    return data


def extract_questions_and_motivations(text):
    pattern = r'Part (\d+(\.\d+)?)\s*((?:[\s\S](?!Part))+)'
    matches = re.findall(pattern, text)
    data = {}
    for part_num, _, content in matches:
        sentences = extract_sentences(content)
        data[part_num] = sentences
    return data


def extract_sentences(text):
    sentences = []
    lines = text.splitlines()

    for line in lines:
        if line.startswith("Experimenter:"):
            for sentence in split_sentences(line[len("Experimenter:"):]):
                sentences.append(('Experimenter', sentence.strip()))
        elif re.match(r'P\d+:', line):
            for sentence in split_sentences(re.sub(r'^P\d+:', '', line)):
                sentences.append(('Participant', sentence.strip()))
        elif line.startswith("Question:"):
            for sentence in split_sentences(line[len("Question:"):]):
                sentences.append(('Question', sentence.strip()))
        elif line.startswith("Motivation:"):
            for sentence in split_sentences(line[len("Motivation:"):]):
                sentences.append(('Motivation', sentence.strip()))

    return sentences


def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)


def main():
    with open('conversation_input_template.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    data = extract_info_and_sentences(text)

    with open('Question_input_template.txt', 'r', encoding='utf-8') as f:
        qm_text = f.read()
    qm_data = extract_questions_and_motivations(qm_text)

    with open('output_template.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Part', 'Timestamp', 'Experimenter', 'Participant', 'Question', 'Motivation'])

        for part_num, timestamp_val, sentences in data:
            # Write the Part Number
            writer.writerow([f'Part {part_num}', f'({timestamp_val})' if timestamp_val else '', '', '', '', ''])

            # If it's a major part (e.g., Part 1) and not a subpart, add a row for the first subpart
            if "." not in part_num:
                writer.writerow([f'Part {part_num}.1', '', '', '', '', ''])

            # Extract corresponding question and motivation
            qm_for_part = qm_data.get(part_num, [])
            question = next((s for l, s in qm_for_part if l == "Question"), "")
            motivation = next((s for l, s in qm_for_part if l == "Motivation"), "")

            for (label, sentence) in sentences:
                if label == "Experimenter":
                    writer.writerow(['', '', sentence, '', question, motivation])
                    question = ""  # Ensure question & motivation are only written once
                    motivation = ""
                elif label == "Participant":
                    writer.writerow(['', '', '', sentence, '', ''])

if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()