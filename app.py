from flask import Flask,render_template,request
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from pypdf import PdfReader

import textwrap
import os
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('homescreen.html')

@app.route('/home',methods=['POST'])
def home():
    return render_template('homescreen.html')

@app.route('/process',methods=['POST'])
def process():
    if 'file' not in request.files:
        return 'No file part'
    file=request.files['file']
    if file.filename=='':
        return 'No selected file'
    summary=''
    text=''
    if file:
        filename=file.filename
        file.save(os.path.join('uploads',filename))
        print('filename ',filename)
        if filename.endswith('.pdf'):
            print('this is a pdf')
            summary=langpdf(filename)
            uncleaned=''
            with open(os.path.join('uploads',filename),'rb') as file:
                reader=PdfReader(file)
                numpage=len(reader.pages)
                for page in reader.pages:
                    uncleaned+=page.extract_text(extraction_mode='layout')
                # for n in range(numpage):
                #     page=reader.pages[n]
                #     uncleaned+=page.extract_text(extraction_mode="layout")
            print('uncleaned is ',uncleaned)
            with open('dump.txt','w') as wfile:
                wfile.write(uncleaned)
            text=cleancpp('dump.txt')
        elif filename.endswith('.txt'):
            summary=langtxt(filename)
            with open(os.path.join('uploads',filename),'r') as file:
                #text=file.read()
                text=''.join(line for line in file)
        else:
            print('Not supported')
            summary='File type not supported'
    print('summary is ',summary)
    print('original is ',text)
    return [summary,text]

def cleancpp(file):
    llm=ChatOpenAI()
    prompt=ChatPromptTemplate.from_template("""Answer the following question about the provided context:
    
    <context>
    {context}
    </context>
    
    Question: {input}""")
    documentchain=create_stuff_documents_chain(llm,prompt)
    loader=TextLoader(file)
    docs=loader.load()

    embeddings=OpenAIEmbeddings()
    tsplitter=RecursiveCharacterTextSplitter()
    documents=tsplitter.split_documents(docs)
    vec=FAISS.from_documents(documents,embeddings)

    retriever=vec.as_retriever()
    retrievalchain=create_retrieval_chain(retriever,documentchain)
    question='Please eliminate everything from the given text that is not a C++ function. For those C++ functions please add preceding whitespace (for indentations) and newline characters to the output string so that the C++ code is readable to a human. Please do not add any comments in your response either, just the return the code'
    response=retrievalchain.invoke({'input':question})
    print(question)
    cleanans=response['answer']
    print(consoleformat(cleanans))
    return cleanans

def langpdf(file):
    llm=ChatOpenAI()
    prompt=ChatPromptTemplate.from_template("""Answer the following question about the C++ code contents of the provided file:
    
    <context>
    {context}
    </context>
    
    Question: {input}""")
    documentchain=create_stuff_documents_chain(llm,prompt)
    loader=PyPDFLoader(os.path.join('uploads',file))
    pages=loader.load_and_split()

    embeddings=OpenAIEmbeddings()
    #print('ebmeddings ',embeddings,len(embeddings))
    tsplitter=RecursiveCharacterTextSplitter()
    documents=tsplitter.split_documents(pages)
    vec=FAISS.from_documents(documents,embeddings)

    retriever=vec.as_retriever()
    retrievalchain=create_retrieval_chain(retriever,documentchain)
    question='Please give a big-O analysis of each function of C++ code in the following file, ignore other text. For each of those functions please note how each for/while loop contribute to the simplified final answer. If a segment is not C++ please ignore it, and if the file contains no C++ code at all respond that the input was invalid'
    response=retrievalchain.invoke({'input':question})
    print(question)
    cleanans=response['answer']
    print(consoleformat(cleanans))
    return cleanans

def langtxt(file):
    llm=ChatOpenAI()
    prompt=ChatPromptTemplate.from_template("""Answer the following question about the provided context:
    
    <context>
    {context}
    </context>
    
    Question: {input}""")
    documentchain=create_stuff_documents_chain(llm,prompt)
    loader=TextLoader(os.path.join('uploads',file))
    docs=loader.load()

    embeddings=OpenAIEmbeddings()
    tsplitter=RecursiveCharacterTextSplitter()
    documents=tsplitter.split_documents(docs)
    vec=FAISS.from_documents(documents,embeddings)

    retriever=vec.as_retriever()
    retrievalchain=create_retrieval_chain(retriever,documentchain)
    question='Please give a big-O analysis of the given C++ code, noting how each for/while loop contribute to the simplified final answer. If it does not compile as C++ code, or no code is present at all, please respond that the input was invalid'
    response=retrievalchain.invoke({'input':question})
    print(question)
    cleanans=response['answer']
    print(consoleformat(cleanans))
    return cleanans

def consoleformat(input,width=100):
    formatted=textwrap.fill(input,width)
    return formatted

if __name__ == '__main__':
    app.run(debug=True)