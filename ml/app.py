#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install PyPDF2')
get_ipython().system('pip install  pandas')
get_ipython().system('pip install nltk')
get_ipython().system('pip install transformers')
get_ipython().system('pip install torch')
get_ipython().system('pip install sentencepiece')
get_ipython().system('pip install ipywidgets')


# In[92]:


from PyPDF2 import PdfReader
import pandas as pd
import re
import nltk
from nltk.tokenize import sent_tokenize
import torch
from transformers import T5ForConditionalGeneration, T5Tokenizer, pipeline, AutoModelForSeq2SeqLM, AutoTokenizer, AutoConfig


# In[70]:


nltk.download("punkt")
model_name = "mrm8488/t5-base-finetuned-question-generation-ap"  # Or a different text-to-text model
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
qa_generator = pipeline('text2text-generation', model=model, tokenizer=tokenizer)
qa_pipeline = pipeline("question-answering")


# In[4]:


# Extract text from PDF

def extract_text(pdf_paths):
    text_data = []
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()

        text_data.append(full_text)
    return text_data


# In[5]:


def process_text(text):
    text = re.sub(r'\s+', ' ', text)  # Remove excessive spaces
    text = re.sub(r'[^\x00-\x7f]', ' ', text)  # Remove non-ASCII characters
    return text.strip()


# In[59]:


def segment_text(txt, sentences_per_segment=7):
    sentences = sent_tokenize(txt)  # This expects 'txt' to be a string
    segments = []
    
    # Create segments of 'sentences_per_segment' sentences
    for i in range(0, len(sentences), sentences_per_segment):
        segment = sentences[i:i + sentences_per_segment]
        segments.append(" ".join(segment))
    
    return segments


# In[103]:


def generate_qp_pairs_from_segments(segments):
    qa_dataset = []
    count = 0
    for paragraph in segments:
        try:
            # Generate questions using the paragraph as input
            generated_questions = qa_generator(paragraph, max_length=100)
            for generated_question_data in generated_questions:
                try:
                    question = generated_question_data['generated_text']
                    answer_data = qa_pipeline({"question": question, "context": paragraph},padding=True, 
                      truncation=True, 
                      max_length=256, 
                      stride=128)
                    print(f"Generated question {count}: {question}")

                    count = count + 1
                    # The answer is in generated_questions
                    answer = answer_data['answer']
                    qa_dataset.append({"Question": question, "Answer": answer})

                except Exception as inner_e:
                    print(f"Error getting answer for question: {question}\n{inner_e}")
        except Exception as outer_e:
            print(f"Error generating questions for paragraph: {paragraph}\n{outer_e}")
    return qa_dataset


# In[62]:


def save_csv(qp_pairs, output_path):
    df = pd.DataFrame(qp_pairs, columns=["Question", "Answer"])
    df.to_csv(output_path)
    print(f"CSV saved at {output_path}")


# In[10]:


pdf_paths = ["textbook1.pdf", "textbook2.pdf", "textbook3.pdf"]
text = extract_text(pdf_paths)


# In[77]:


pdf_pathsed = ["textbook1.pdf"]
texted = extract_text(pdf_pathsed)


# In[104]:


combined_text = " ".join(text)

segments = segment_text(combined_text, sentences_per_segment=7)


# In[105]:


qp_pairs = generate_qp_pairs_from_segments(segments)


# In[87]:


save_csv(qp_pairs, "temp5.csv")

