# %pip install -U langchain_community tiktoken langchain-openai langchainhub langchain langgraph langchain_huggingface
# %pip install -U pymilvus sentence-transformers fsspec s3fs yandexcloud transformers pip install langchain-experimental
# %pip install --upgrade huggingface-hub
# %pip install -qU  langchain_milvus
# %pip install pydantic==2.6.0
import re
import string
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_milvus import Milvus
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.chat_models import ChatYandexGPT
from langchain_core.utils.function_calling import convert_to_openai_tool
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from typing import List
from typing_extensions import TypedDict
import time
from langgraph.graph import END, StateGraph, START
from pprint import pprint
from yandex_logic import *


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """
    
    question: str
    generation: str
    documents: List[str]


class SelfReflectiveRag:
    
    def __init__(self, db_path : str, db_name : str, gpt_folder_id : str, iam_token : str):
        self.db_path = db_path
        self.db_name = db_name
        self.gpt_folder_id = gpt_folder_id
        self.iam_token = iam_token
        self.vectorstore = None
        self.embeddings = None
        self.retriever = None
        self.rag_chain = None
        self.retrieval_grader = None
        self.hallucination_grader = None
        self.answer_grader = None
        self.question_rewriter = None
        self.app = None

    def run_rag(self, questions):
        self._compile_app()
        self._preprocess_question(questions)
        question = {"question" : self.questions["questions"][-1]}

        # Run
        for output in self.app.stream(question):
            for key, value in output.items():
                # Node
                pprint(f"Node '{key}':")
                # Optional: print full state at each node
                # pprint.pprint(value["documents"], indent=2, width=80, depth=None)
            pprint("\n---\n")
        # Final generation
        return value
    
    
    def _compile_app(self):
        workflow = StateGraph(GraphState)
        
        self._get_retriever()
        self._get_retrieval_grader()
        self._get_generator_query()
        self._get_hallucination_grader()
        self._get_answer_grader()
        self._get_question_writer()

        # Define the nodes
        workflow.add_node("retrieve", self._retrieve)  # retrieve
        workflow.add_node("grade_documents", self._grade_documents)  # grade documents
        workflow.add_node("generate", self._generate)  # generate
        workflow.add_node("transform_query", self._transform_query)  # transform query

        # Build graph
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "grade_documents")
        workflow.add_conditional_edges(
            "grade_documents",
            self._decide_to_generate,
            {
                "transform_query": "transform_query",
                "generate": "generate",
            },
        )
        workflow.add_edge("transform_query", "retrieve")
        workflow.add_conditional_edges(
            "generate",
            self._grade_generation_v_documents_and_question,
            {
                "not supported": "transform_query",
                "useful": END,
                "not useful": "transform_query",
            },
        )

        # Compile
        self.app = workflow.compile()

        
    def _preprocess_question(self, questions: List[str]):
        # questions for retrieval
        self.questions = {
            "questions_raw": questions
        }
        question_list = []
        for texts in questions:
            dataset_text = ''.join([char.lower() if not char.isdigit() and char is not None else char for char in texts])
            dataset_text = re.sub('  ', ' ', dataset_text)  # remove useless space
            dataset_text = re.sub(r'[\x00-\x1F\x7F-\x9F]+', '', dataset_text)
            question_list.append(dataset_text)

        self.questions["questions"] = question_list
        
        
    def _get_retriever(self, model_name="deepvk/USER-bge-m3", collection_name="npa_storage_512_64"):
        # Retriever
        model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        model_kwargs = {'device': 'cuda'}
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
        )

        self.vectorstore = Milvus(
            collection_name=collection_name, 
            connection_args={"uri": self.db_path},
            embedding_function=self.embeddings
        )
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 20, "fetch_k": 50, "lambda_mult": 0.8})

    
    def _get_retrieval_grader(self):
        # Retrieval Grader
        llm = ChatYandexGPT(iam_token=self.iam_token, folder_id=self.gpt_folder_id, temperature=0, sleep_interval=0.1)
        
        # Prompt
        system = """Ты - грейдер, оценивающий релевантность найденных фрагментов документов вопросу пользователя. \n 
            Это не обязательно должны быть строгие текста. Цель - отсеять ошибочные запросы. \n
            Если фрагмент содержит слова или семантические значения, связанные с вопросом пользователя, оцени его как релевантный. \n
            Дай бинарную оценку «да» или «нет», чтобы указать, релевантен ли фрагмент вопросу. \n"""

        grade_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Документы, которые мы извлекли: \n\n {document} \n\n Вопрос пользователя: {question}"),
            ]
        )
        
        self.retrieval_grader = grade_prompt | llm
        
    
    def _get_generator_query(self):
        ### Generate
        # Prompt
        prompt = hub.pull("rlm/rag-prompt")
        # LLM
        llm = ChatYandexGPT(iam_token=self.iam_token, folder_id=self.gpt_folder_id, temperature=0, sleep_interval=0.1)
        # Chain
        self.rag_chain = prompt | llm | StrOutputParser()
        
    
    def _get_hallucination_grader(self):
        ### Hallucination Grader
        llm = ChatYandexGPT(iam_token=self.iam_token, folder_id=self.gpt_folder_id, temperature=0, sleep_interval=0.1)

        # Prompt
        system = """Ты занимаешься оцениванием, насколько LLM-вывод обоснован / подкреплен набором полученных фактов. \n 
             В качестве ответа ты выдаешь бинарную оценку «да» или «нет». Да» означает, что ответ обоснован / подкреплен набором фактов, а имена собственные совпадают / не перепутаны с изначально упомянутыми в вопросе."""
        hallucination_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Набор фактов: \n\n {documents} \n\n Ответ LLM: {generation}"),
            ]
        )

        self.hallucination_grader = hallucination_prompt | llm
    
    
    def _get_answer_grader(self):
        ### Answer Grader
        # LLM with function call
        llm = ChatYandexGPT(iam_token=self.iam_token, folder_id=self.gpt_folder_id, temperature=0, sleep_interval=0.1)
        # Prompt
        system = """Ты оцениваешь, насколько ответ LLM соответствует/решает вопрос \n 
             Дай бинарную оценку «да» или «нет». Да» означает, что ответ разрешает вопрос. Спасибо!"""
        
        answer_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                ("human", "Вопрос пользователя: \n\n {question} \n\n Ответ LLM: {generation}"),
            ]
        )
        self.answer_grader = answer_prompt | llm

        
    def _get_question_writer(self):
        ### Question Re-writer
        llm = ChatYandexGPT(iam_token=self.iam_token, folder_id=self.gpt_folder_id, temperature=0, sleep_interval=0.1)

        # Prompt
        system = """Ты преобразуешь вопрос в лучшую версию, оптимизированную \n 
             для поиска в векторном хранилище. Посмотри на входные данные и попытайся определить семантическое намерение / смысл."""
        re_write_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                (
                    "human",
                    "Вот начальный вопрос: \n\n {question} \n Сформулируй улучшенный вопрос.",
                ),
            ]
        )
        self.question_rewriter = re_write_prompt | llm | StrOutputParser()
    
    
    ### Nodes
    def _retrieve(self, state):
        """
        Retrieve documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, documents, that contains retrieved documents
        """
        print("---RETRIEVE---")
        question = state["question"]

        # Retrieval
        documents = self.retriever.get_relevant_documents(question) # our database used here
        return {"documents": documents, "question": question}
    
    
    def _generate(self, state):
        """
        Generate LLM response based on query + documents.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, generation, that contains final generation
        """
        print("---GENERATE---")
        question = state["question"]
        documents = state["documents"]

        # RAG generation
        generation = self.rag_chain.invoke({"context": documents, "question": question})
        time.sleep(1)
        return {"documents": documents, "question": question, "generation": generation}
    
    
    def _grade_documents(self, state):
        """
        Score retrieved documents

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): Existing key in state, documents, that now has graded documents
        """
        print("---CHECK DOCUMENT RELEVANCE TO QUESTION---")
        question = state["question"]
        documents = state["documents"]

        # Score each doc
        filtered_docs = []
        for d in documents:
            score = self.retrieval_grader.invoke(
                {"document": d.page_content, "question": question}
            )
            time.sleep(1)
            grade = score.content.lower()
            if "да" in grade:
                print("---GRADE: DOCUMENT RELEVANT---")
                filtered_docs.append(d)
            else:
                print("---GRADE: DOCUMENT NOT RELEVANT---")
        return {"documents": filtered_docs, "question": question}
    
    
    def _grade_generation_v_documents_and_question(self, state):
        """
        Score generation

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): decision: if useful or not useful
        """
        print("---CHECK HALLUCINATIONS---")
        question = state["question"]
        documents = state["documents"]
        generation = state["generation"]

        score = self.hallucination_grader.invoke(
            {"documents": documents, "generation": generation}
        )
        time.sleep(1)
        grade = score.content.lower()

        # Check hallucination
        if "да" in grade:
            print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
            # Check question-answering
            print("---GRADE GENERATION vs QUESTION---")
            score = self.answer_grader.invoke({"question": question, "generation": generation})
            time.sleep(1)
            grade = score.content.lower()
            if "да" in grade:
                print("---DECISION: GENERATION ADDRESSES QUESTION---")
                return "useful"
            else:
                print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
                return "not useful"
        else:
            pprint("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
            return "not supported"
    
    
    def _transform_query(self, state):
        """
        Re-write query.

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key in state, question, that now has the transformed query
        """
        print("---TRANSFORM QUERY---")
        question = state["question"]
        documents = state["documents"]

        # Re-write question
        better_question = self.question_rewriter.invoke({"question": question})
        time.sleep(1)
        print(f"--- REWRITED QUESTION: {better_question} ---")
        return {"documents": documents, "question": better_question}
    
    
    def _decide_to_generate(self, state):
        """
        Decide if query should be transformed or generate LLM response.

        Args:
            state (dict): The current graph state

        Returns:
            str: Edge to follow, "generate" or "transform_query"
        """
        print("---ASSESS GRADED DOCUMENTS---")
        state["question"]
        filtered_documents = state["documents"]

        if not filtered_documents:
            # All documents have been filtered check_relevance
            # We will re-generate a new query
            print(
                "---DECISION: ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, TRANSFORM QUERY---"
            )
            return "transform_query"
        else:
            # We have relevant documents, so generate answer
            print("---DECISION: GENERATE---")
            return "generate"
        