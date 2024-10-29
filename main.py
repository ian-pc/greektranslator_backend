from Dictionary_Parse import Dictionary, Parser
import openai
from cltk import NLP
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
# from cltk.lemmatize.grc import DictLemmatizer

app = Flask(__name__)
CORS(app)


API_KEY = "sk-proj-W6O9scSc55O6gOradF7DT3BlbkFJZCjatA5iGABY2ITZc0gj"

nlp = NLP(language="grc", suppress_banner=True)

def truncate_string(input_string, max_length=4096):
    if len(input_string) <= max_length:
        return input_string
    truncated_string = input_string[:max_length].rsplit(' ', 1)[0] + "..."
    return truncated_string

def get_partofspeech(word): 

    if not isinstance(word, str):
        raise ValueError("The input word must be a string")

    # Process the word
    doc = nlp(word)
    pos = "Nan"
    for temp in doc: 
        pos = temp.pos
        # print("OIEWHFOUWEHFOUWEHFULOEWHFOUWEUOFWE", pos)
    return pos

def get_lemmatized(word): 
    if not isinstance(word, str):
        raise ValueError("The input word must be a string")

    # Process the word
    doc = nlp(word)
    lemma = word
    for temp in doc: 
        lemma = temp.lemma
        # print("OIEWHFOUWEHFOUWEHFULOEWHFOUWEUOFWE", pos)
    return lemma

def makesense(word, raw_translation): 
    client2 = openai.OpenAI(api_key=API_KEY)

    return_val = ""
    instructions = f"You are going to me given the output for the word {word} from an Ancient Greek lexicon. Output the definition of this word in an understandable manner in a couple of sentences. Do not include any information about references. Do not include parts of speech. Refrain from referencing the word itself in your definition. Ignore any html script such as <b> and <i>"

    assistant = client2.beta.assistants.create(
        name="Greek Translation Interpreter",
        instructions=instructions, 
        model="gpt-4o",
        temperature=0
    )

    thread = client2.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": raw_translation,
            }
        ]
    )
    run = client2.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    
    if run.status == "completed":
        # Retrieve the list of messages in the thread
        messages = client2.beta.threads.messages.list(thread_id=thread.id)

        # Find the latest message from the assistant
        for message in messages:
            if message.role == "assistant":
                return_val = message.content[0].text.value
                break
    
    client2.close()

    return return_val

def get_parse_instructions(sentence): 
    #Word #1: kai
    #In the sentence the word is a 'nominative', '2nd person', ...
    #   use case 1 [kai par]: ...
    #   use case 2 [kai]: a conjunction
    #
    #Word #2: poop
    #...
    return_val = ""
    i = 0
    sentence = sentence.strip()
    sentence = ''.join(char for char in sentence if char not in string.punctuation) #removing punctuation
    for word in sentence.split(' '): 
        i += 1
        return_val += f"word #{i}: {word}\n"
        partofspeech = get_partofspeech(word)
        if (partofspeech != "Nan"): 
            return_val += f"In the sentence the word is a {partofspeech}. \n" 
        
        dictionary = Dictionary().to_dict()
        parser = Parser(dictionary=dictionary)
        lemmatized_word = get_lemmatized(word)
        complete_parse = parser.lookup(lemmatized_word)
        # for usecase in range(len(complete_parse)): 
        #     print(return_val)
        #     # print(f"- Use case #{usecase + 1}, when the word is in the phrase {complete_parse[usecase]['headword']}, it means: [{makesense(word, complete_parse[usecase]['definition'])}]") #.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', ''))}]")
        #     return_val += f"- Use case #{usecase + 1}, when the word is in the form {complete_parse[usecase]['headword']}, its definition is: [{makesense(word, complete_parse[usecase]['definition'])}]\n"
        usecase = 0
        for cur_parse in complete_parse: 
            usecase += 1
            # print(return_val)
            # print(f"- Use case #{usecase + 1}, when the word is in the phrase {complete_parse[usecase]['headword']}, it means: [{makesense(word, complete_parse[usecase]['definition'])}]") #.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', ''))}]")
            definition = cur_parse['definition']
            definition = truncate_string(definition)
            
            return_val += f"- Use case #{usecase}, when the word is in the form {cur_parse['headword']}, its definition is: [{makesense(word, definition)}]\n"

        return_val += "\n"

    return return_val

def get_instructions(): 
    instructions = f"""
    You are an ancient greek translator, however openai's gpt is incapable of accurately translating ancient greek, especially because it does not know the exact translations and morphology of many words. 
    
    Your job is to translate the inputted sentence which is in ancient greek, into a natural english sentence. 
    
    Unfortunately, greek is a complex language and each word has a lot of forms and use cases depending on which words they are paired with. Therefore, you will also be provided with a list of possible definitions for each of the words in the sentence. 
    
    It is your job to find the best definition for each of the words in the context of the sentence using the list, and then output a sentence which is a natural translation of the inputed sentence into english. 
    
    DO NOT OUTPUT ANYTHING OTHER THAN THE TRANSLATED SENTENCE!
    """

    return instructions

def get_content(sentence): 
    parse_instructions = get_parse_instructions(sentence)
    return_val = ""
    return_val += f"Sentence: [{sentence}] \n\n"
    return_val += f"List of possible definitions for each word in the sentence: \n{parse_instructions}"

    return return_val

def generate_response(instructions, content): 
    client = openai.OpenAI(api_key=API_KEY)
    assistant = client.beta.assistants.create(
        name="Greek Translator",
        instructions=instructions, 
        model="gpt-4o",
        temperature=0
    )
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": content,
            }
        ]
    )
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )


    print("Run completed with status: " + run.status)

    if run.status == "completed":
        # Retrieve the list of messages in the thread
        messages = client.beta.threads.messages.list(thread_id=thread.id)

        # Find the latest message from the assistant
        for message in messages:
            if message.role == "assistant":
                return_val = message.content[0].text.value
                break

    client.close()

    return return_val

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        content = data.get('content')

        if not content:
            return jsonify({'error': 'Content is required.'}), 400

        instructions = get_instructions()
        result = generate_response(instructions=instructions, content=content)
        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': 'An internal error occurred.'}), 500


# if __name__ == "__main__":

#     with open('resources/sentence.txt', 'r', encoding="utf8") as file:
#         sentence = file.read()
#         file.close

#     instructions = get_instructions()
#     # print(instructions)
#     content = get_content(sentence)
#     # print(content)

#     print(generate_response(instructions=instructions, content=content))

if __name__ == '__main__':
    # app.run(debug=True)
    # app.run(host="0.0.0.0", port=5000)
    app.run()



