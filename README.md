# The Big-O Calculator

This is a simple website I made for my students where they can upload a .txt or PDF with C++ code in it and get an
analysis of the runtime of the functions. It is a flask app that uses LangChain backend to pass the input through OpenAI. 

The "Input" field displays the cleaned C++ functions within the file. This is because the file is no longer visible after being uploaded, and 
can contain other things besides C++ code (students can upload past exams which are several pages, but this would clean it down to leave just the C++ functions).
The "Output" field is where the AI response message is printed. 

An error handling feature exists where a browser alert message will pop up with any server side errors, to prevent the user from just seeing
the loading bar spin indefinitely thinking it is working.

Current problems: 1 page PDFs cause an indexing error in the backend
