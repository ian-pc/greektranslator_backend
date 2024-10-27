import openai


API_KEY = "sk-proj-W6O9scSc55O6gOradF7DT3BlbkFJZCjatA5iGABY2ITZc0gj"
def makesense(word, raw_translation): 
    client2 = openai.OpenAI(api_key=API_KEY)

    instructions = f"You are going to me given the output for the word {word} from an Ancient Greek lexicon. Output the definition of this word in an understandable manner in a paragraph or couple of sentences. Do not include any information about references. Do not include parts of speech. Ignore any html script such as <b> and <i>"

    assistant = client2.beta.assistants.create(
        name="Greek Translation Interpreter",
        instructions=instructions, 
        model="gpt-4-turbo",
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

print(makesense(word="ὡσεί", raw_translation="""<b>ὡς</b>, Adv. (1) as, like, just as; (2) that, in order that, so that; (3) how, in what way; (4) as if, as though; (5) about, approximately. Used with various moods and constructions: 

&nbsp;&nbsp;&nbsp;&nbsp;<b>I.</b> with indic., expressing manner, comparison, or circumstance, e.g., <i>ὡς ἀληθῶς</i> truly, <i>ὡς ἐπὶ τὸ πολύ</i> generally, Hdt., etc.; in similes, <i>ὡς λέοντι</i> like a lion, Il.

&nbsp;&nbsp;&nbsp;&nbsp;<b>II.</b> with subj., expressing purpose or result, e.g., <i>ὡς ἴδῃς</i> that you may see, X.; <i>ὡς μὴ γένηται</i> lest it happen, Thuc.

&nbsp;&nbsp;&nbsp;&nbsp;<b>III.</b> with opt., expressing wish or potential, e.g., <i>ὡς ἔλθοιμι</i> would that I might go, Od.

&nbsp;&nbsp;&nbsp;&nbsp;<b>IV.</b> with inf., expressing purpose, after verbs of striving, advising, etc., e.g., <i>κελεύει ὡς ἀγαγέμεναι</i> he orders to bring, Hdt.

&nbsp;&nbsp;&nbsp;&nbsp;<b>V.</b> with part., expressing manner or circumstance, e.g., <i>ὡς ταῦτα εἰπὼν</i> having said this, Thuc.; sometimes nearly equivalent to a finite verb, <i>ὡς οὐκ ἐόντων</i> as if they were not, Thuc.

&nbsp;&nbsp;&nbsp;&nbsp;<b>VI.</b> with acc., expressing extent and degree, <i>ὡς πολύ</i> by much, very much, Hdt.; <i>ὡς ἥκιστα</i> as little as possible, Plat.

&nbsp;&nbsp;&nbsp;&nbsp;<b>VII.</b> in exclamations, <i>ὡς ὀλίγου</i> how little!, Ar.; <i>ὡς καλός</i> how beautiful!, Plat. 

&nbsp;&nbsp;&nbsp;&nbsp;<b>VIII.</b> with numerals or measures of time and space, about, approximately, e.g., <i>ὡς δέκα ἔτη</i> about ten years, Hdt"""))