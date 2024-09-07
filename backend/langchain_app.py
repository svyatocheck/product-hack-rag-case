from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# Инициализация векторной базы данных
embeddings = OpenAIEmbeddings()
vectorstore = Chroma(embedding_function=embeddings)

# Добавление документов в векторную базу данных
documents = [
    "Я люблю программирование на Python.",
    "LangChain позволяет легко интегрировать языковые модели.",
    "Векторные базы данных полезны для обработки текстов."
]
vectorstore.add_texts(documents)

# Создание цепочки для вопросно-ответного взаимодействия
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(temperature=0),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# Использование цепочки для получения ответа
question = "Что такое LangChain?"
answer = qa_chain.run(question)

print(f"Ответ: {answer}")
